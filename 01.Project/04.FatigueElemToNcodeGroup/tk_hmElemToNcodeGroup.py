

import hmElemToNcodeGroup
import tkui

TkUi = tkui.TkUi


class ElemToNcodeGroupUI(TkUi):

    def __init__(self, title):
        super().__init__(title)
        str_label = '-'*40

        self.frame_loadpath({
            'frame':'fem_path', 'var_name':'fem_path', 'path_name':'fem file',
            'path_type':'.fem', 'button_name':'基础fem路径',
            'button_width':20, 'entry_width':40,
            })

        self.frame_savepath({
            'frame':'asc_path', 'var_name':'asc_path', 'path_name':'asc_path',
            'path_type':'.asc', 'button_name':'asc 路径\n[Ncode User Group]',
            'button_width':20, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'set_id','var_name':'set_id','label_text':'计算目标set的ID【1位】',
            'label_width':20,'entry_width':30,
            })

        self.frame_entry({
            'frame':'fun_lambda','var_name':'fun_lambda','label_text':'prop2mat name\nlambda函数',
            'label_width':20,'entry_width':30,
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

        self.vars['fun_lambda'].set("lambda propname: propname.split('_')[2]")


    def fun_run(self):
        """
            运行按钮调用函数
            主程序
        """
        # 获取界面数据
        params = self.get_vars_and_texts()
        # print(params)
        fem_path = params['fem_path']
        asc_path = params['asc_path']
        set_id = str(params['set_id'])


        self.print('\n\n----开始计算----\n\n')

        hmElemToNcodeGroup.main_by_Setid(fem_path, asc_path, set_id)

        self.print('\n\n----计算结束----\n\n')

        return True

if __name__=='__main__':

    ElemToNcodeGroupUI('SET转Ncode User Group').run()