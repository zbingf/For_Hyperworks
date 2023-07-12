"""
    编辑fatigue fem的set数据
"""

import re
import os
import logging
import math



logger = logging.getLogger('fatigue_fem_fatdef_split_limit')


get_line_n = lambda line, n: line[8*n:8*(n+1)].strip()

def str2float(str1):

    if '-' in str1[1:]:
        new_str1 = str1[0] + str1[1:].replace('-', 'e-')
    elif '+' in str1[1:]:
        new_str1 = str1[0] + str1[1:].replace('+', 'e+')
    else:
        new_str1 = str1

    return float(new_str1)


def read_fem(fem_path):
    with open(fem_path, 'r') as f:
        return f.readlines()

# 读取&解析数据
def read_fem_set(fem_path, set_id_range=None):

    f = open(fem_path, 'r')
    
    set2elems = {}
    elem2set  = {}

    is_set = False
    lines  = []
    elem_ids  = []
    n_read = -1
    set2line = {}

    while True:
        line = f.readline()
        n_read += 1

        if not line :break
        cline = line.strip()
        lines.append(line)

        if "SET" in cline[:4]:
            set_id = get_line_n(line, 1)
            set_type = get_line_n(line, 2)

            # 过滤条件
            if set_type != 'ELEM': continue
            if set_id_range != None:
                if int(set_id) < set_id_range[0] or \
                    int(set_id) > set_id_range[1]:
                    print_str = 'set_id {} not in set_id_range {}'.format(set_id, set_id_range)
                    logger.info(print_str)
                    print(print_str)
                    continue

            set2line[set_id] = {}
            is_set = True
            set2line[set_id]['start'] = n_read
            continue

        if is_set: # set设置范围
            if cline[0] == '+': # 续接 set
                n_len = round(len(line)/8)
                for n in range(1, n_len):
                    elem_id = get_line_n(line, n)
                    if elem_id in elem2set: 
                        print_str = 'elem_id在不同set_id中存在: {} ; set_id: {} ; current set_id: {} 覆盖;'.format(elem_id, elem2set[elem_id], set_id)
                        logger.info(print_str)
                        print(print_str)
                    
                    elem2set[elem_id] = set_id
                    elem_ids.append(elem_id)
            
            else: # 中断set读取
                set2line[set_id]['end'] = n_read
                is_set = False
                set2elems[set_id] = elem_ids
                elem_ids = []
    # print(set2elems.keys())
    data = {
        'set2elems': set2elems,
        'elem2set': elem2set,
        'lines' : lines,
        'set2line' : set2line,
    }

    return data


# 根据elem_ids, 调整set, 删除elem_ids外的数据
def edit_lines_by_elems(data, elem_ids):
    # 调整set大小
    # 选出无关set

    set2elems = data['set2elems']
    elem2set = data['elem2set']
    set2line = data['set2line']
    lines = data['lines']

    def is_inedit(edit_sets, loc):
        # 判定是否在修改范围内
        for set_id in edit_sets:
            start_loc, end_loc = edit_sets[set_id]['start'], edit_sets[set_id]['end']
            if loc >= start_loc and \
                loc <= end_loc:
                return True, set_id

        return False, 0

    # -------------------------
    new_set2elems = {}

    for elem_id in elem_ids:
        if elem_id not in elem2set: continue
        set_id = elem2set[elem_id]
        if set_id not in new_set2elems:
            new_set2elems[set_id] = []
        new_set2elems[set_id].append(elem_id)

    # -------------------------
    edit_sets = {}
    for set_id in new_set2elems:
        edit_sets[set_id] = set2line[set_id]

    # -------------------------
    new_lines = []
    for loc, line in enumerate(lines):

        inedit, set_id = is_inedit(edit_sets, loc)
        if inedit:
            if loc == set2line[set_id]['start']:
                new_lines.append(line)

            if loc == set2line[set_id]['start']+1:
                # 数据替换
                new_lines.extend( lines_set_elem(new_set2elems[set_id]) )
            continue
        new_lines.append(line)
    
    return new_lines


# 创建set elemID行数据, 不带标题
def lines_set_elem(elem_ids, n_line=8):
    
    lines = []
    line_start = '+'.ljust(8)
    elems1 = []
    for loc, elem_id in enumerate(elem_ids):
        if loc%8 == 0:
            if elems1:
                lines.append(line_start + ''.join(elems1) + '\n')
            elems1 = []

        elems1.append(elem_id.ljust(8))

    lines.append(line_start + ''.join(elems1) + '\n')

    return lines


# 写入文件, 列表字符串自带换行符
def write_file(fem_path, lines):
    with open(fem_path, 'w') as f:
        f.write(''.join(lines))
        

# 搜索fatdef的设置, 耐久计算选取set
def search_fatdef(lines):

    data = {}
    is_fatdef = False
    n_lines = []
    fatdef_lines = []

    # 
    for loc, line in enumerate(lines):
        if line[:6] == 'FATDEF':
            is_fatdef = True
            continue

        if is_fatdef:
            if '+' in line[:2]:
                fatdef_lines.append(line)
                n_lines.append(loc)
            else:
                is_fatdef = False
                break

    # 数据识别
    values = []
    for line in fatdef_lines:
        if ',' in line:
            list1 = line.split(',')[2:]
            values.extend(list1)
        else:
            n_vlaue = math.ceil(len(line.strip())/8)
            for n in range(2, n_vlaue):
                value = get_line_n(line, n)
                values.append(value)

    set2pfat = {}
    set_ids = values[0::2]
    pfat_ids = values[1::2]
    for set_id, pfat_id in zip(set_ids, pfat_ids):
        set2pfat[set_id] = pfat_id

    # print(fatdef_lines)
    # print(n_lines)
    # print('set_ids', set_ids)
    # print('pfat_ids', pfat_ids)

    return n_lines, set2pfat


# 选择性编辑fatdef
def edit_lines_fatdef(lines, set_ids, n_lines, set2pfat):
    # set_ids 目标set的id
    # lines fem各行数据

    pfat_ids = []
    new_set_ids = []
    for set_id in set_ids:
        if set_id not in set2pfat:
            print_str = 'warning: set_id {} 不在 set2pfat 中, 绕过该set!!'.format(set_id)
            logger.warning(print_str)
            print(print_str)
            continue
        pfat_ids.append(set2pfat[set_id])
        new_set_ids.append(set_id)

    if not pfat_ids: return None

    # 新fatdef lines
    fatdef_lines = []
    loc = -1
    for pfat_id, set_id in zip(pfat_ids, new_set_ids):
        loc += 1
        if loc == 0:
            line = '+'.ljust(8) + 'ELSET'.ljust(8) + set_id.ljust(8) + pfat_id.ljust(8) + '\n'
        else:
            line = '+'.ljust(8) + ' '.ljust(8) + set_id.ljust(8) + pfat_id.ljust(8) + '\n'
        fatdef_lines.append(line)

    # 新fem line
    new_lines = []
    for loc, line in enumerate(lines):
        if loc in n_lines:
            if loc == n_lines[0]:
                new_lines.extend(fatdef_lines)
            continue
        new_lines.append(line)

    return new_lines


def split_fatigue_fatdef_set_limit(fem_path, set_range, max_num=15000):
    """
        fem_path 路径
        max_num 网格上限设置
        set_range = (10000, 90000) 目标setID

    """
    # max_num = 15000
    # set_id_min = 10000
    # set_id_max = 90000
    new_fem_paths = []

    data = read_fem_set(fem_path, set_range)
    set2elems = data['set2elems']
    for set_id in set2elems:
        elem_ids = set2elems[set_id]
        num = round(len(elem_ids)/max_num)
        if num==0: num = 1
        for n in range(num):
            if n < num-1:
                elem_ids_1 = elem_ids[n*max_num : (n+1)*max_num]
            else:
                elem_ids_1 = elem_ids[n*max_num:]

            new_fem_path = fem_path[:-4] + '_{}_{}.fem'.format(set_id, n)
            lines = edit_lines_by_elems(data, elem_ids_1)
            n_lines, set2pfat = search_fatdef(lines)
            new_lines = edit_lines_fatdef(lines, [set_id], n_lines, set2pfat)
            if new_lines==None: continue  # 没有符合的set_id, 绕过该fem文件的创建

            # 创建fem文件
            write_file(new_fem_path, new_lines)
            print_str = 'write: {}'.format(new_fem_path)
            logger.info(print_str)
            print(print_str)
            new_fem_paths.append(new_fem_path)

    return new_fem_paths


# =========================================================
# =========================================================

import tkui
TkUi = tkui.TkUi

# UI模块
class FatigueFemFatdefSplitLimit(TkUi):
    """
        AdmSim 主程序
    """
    def __init__(self, title):
        super().__init__(title)
        str_label = '-'*40

        self.frame_loadpaths({
            'frame':'fem_paths', 'var_name':'fem_paths', 'path_name':'fem files',
            'path_type':'.fem', 'button_name':'fem files',
            'button_width':15, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'max_num','var_name':'max_num','label_text':'网格上限',
            'label_width':15,'entry_width':30,
            })

        self.frame_entry({
            'frame':'set_id_min','var_name':'set_id_min','label_text':'SetID min',
            'label_width':15,'entry_width':30,
            })

        self.frame_entry({
            'frame':'set_id_max','var_name':'set_id_max','label_text':'SetID max',
            'label_width':15,'entry_width':30,
            })


        self.frame_checkbutton({
            'frame':'isSetLimit',
            'var_name':'isSetLimit',
            'check_text':'SET ELEM ID限制',
            })

        self.frame_buttons_RWR({
            'frame' : 'rrw',
            'button_run_name' : '运行',
            'button_write_name' : '保存',
            'button_read_name' : '读取',
            'button_width' : 15,
            'func_run' : self.fun_run,
            })

        self.frame_note()

        # 初始化设置
        self.vars['max_num'].set(15000)
        self.vars['isSetLimit'].set(True)


    def fun_run(self):
        """
            运行按钮调用函数
            主程序
        """
        # 获取界面数据
        params = self.get_vars_and_texts()
        isSetLimit = params['isSetLimit']
        fem_paths = params['fem_paths']
        set_id_max = params['set_id_max']
        set_id_min = params['set_id_min']
        max_num = params['max_num']

        # print(params)
        # return None
        
        if isinstance(fem_paths, str):
            fem_paths = [fem_paths]

        # ======
        if isSetLimit:
            set_range = (set_id_min, set_id_max)
        else:
            set_range = None

        for fem_path in fem_paths:
            split_fatigue_fatdef_set_limit(fem_path, set_range, max_num)
        self.print('计算完成')

        return True


def test_split_fatigue_fatdef_set_limit():

    import tkinter
    import tkinter.filedialog
    tkinter.Tk().withdraw()

    fem_path = tkinter.filedialog.askopenfilename(
        filetypes = (('fem', '*.fem'),),
        )
    set_range = (10000, 90000)
    max_num = 15000

    split_fatigue_fatdef_set_limit(fem_path, set_range, max_num)


# test_split_fatigue_fatdef_set_limit()


if __name__ == '__main__':

    file_dir = os.path.dirname(__file__)
    log_path = os.path.join(file_dir, 'fatigue_fem_fatdef_split_limit.log')
    with open(log_path, 'w') as f: pass
    logging.basicConfig(level=logging.INFO, filename=log_path)  # 设置日志级别

    # Ui测试
    obj = FatigueFemFatdefSplitLimit('Fatigue分割').run()








