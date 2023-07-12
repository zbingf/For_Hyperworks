"""
    
    
"""

import os.path
import math
import sys
import os
import re



get_line_n = lambda line, n: line[8*n:8*(n+1)].strip()
dis_loc    = lambda loc1, loc2: ((loc1[0]-loc2[0])**2 + (loc1[1]-loc2[1])**2 + (loc1[2]-loc2[2])**2)**0.5
v_abs      = lambda loc1: (loc1[0]**2 + loc1[1]**2 + loc1[2]**2)**0.5
v_one      = lambda loc1: [loc1[0]/v_abs(loc1), loc1[1]/v_abs(loc1), loc1[2]/v_abs(loc1)]


RAD_2_DEG = 180/math.pi


# 向量叉乘
def v_multi_x(loc1, loc2):
    x1, y1, z1 = loc1
    x2, y2, z2 = loc2
    return [y1*z2-y2*z1, z1*x2-z2*x1, x1*y2-x2*y1]

# 向量点乘
def v_multi_dot(loc1, loc2):
    x1, y1, z1 = loc1
    x2, y2, z2 = loc2
    value = x1*x2 + y1*y2 + z1*z2    
    return value

# 向量数值乘
def v_multi_c(loc1, c):
    x1, y1, z1 = loc1
    return [x1*c, y1*c, z1*c]

# 向量 减
def v_sub(loc1, loc2):
    x1, y1, z1 = loc1
    x2, y2, z2 = loc2
    return [x1-x2, y1-y2, z1-z2]

# 矢量夹角计算
def angle_2vector(base_v_loc, target_v_loc):

    base_abs = v_abs(base_v_loc)
    target_abs = v_abs(target_v_loc)
    a_dot_b = v_multi_dot(base_v_loc, target_v_loc)
    value = a_dot_b / (base_abs*target_abs)
    if value > 1: value = 1
    if value < -1: value = -1

    angle_rad = math.acos(value)
    return angle_rad

#
def str2float(str1):

    if '-' in str1[1:]:
        new_str1 = str1[0] + str1[1:].replace('-', 'e-')
    elif '+' in str1[1:]:
        new_str1 = str1[0] + str1[1:].replace('+', 'e+')
    else:
        new_str1 = str1
    # print(new_str1)
    return float(new_str1)


# 获取elem的法向量
def get_v_element(locs):

    v1 = v_sub(locs[1], locs[0])
    v2 = v_sub(locs[2], locs[1])
    return v_multi_x(v1, v2)


# 读取&解析数据
def read_data(fem_path):


    grid_dic, elem_dic = {}, {}
    f = open(fem_path, 'r')
    while True:
        line = f.readline()
        if not line :break
        if "$" == line[0]: continue
        
        if "GRID" in line[:6]:
            g_id = get_line_n(line, 1)
            x = str2float(get_line_n(line, 3))
            y = str2float(get_line_n(line, 4))
            z = str2float(get_line_n(line, 5))
            grid_dic[g_id] = [x, y, z]
            continue
        
        if "CTRIA3" in line:
            e_id = get_line_n(line, 1)
            elem_dic[e_id] = [get_line_n(line, n) for n in [3, 4, 5]]
            continue

        if "CQUAD4" in line:
            e_id = get_line_n(line, 1)
            elem_dic[e_id] = [get_line_n(line, n) for n in [3, 4, 5, 6]]
            continue

    return grid_dic, elem_dic


def calc_shell_angle(fem_path, target_elem_ids, target_vs):

    # target_elem_ids = [18417139,18415285,2004699]
    # target_vs = [[0,0,1],[0,0,1],[0,0,1]]

    # 获取fem数据
    grid_dic, elem_dic = read_data(fem_path)

    thetas = {}
    for elem_id, t_v in zip(target_elem_ids,target_vs):
        r_ids = elem_dic[str(elem_id)]
        p0 = grid_dic[r_ids[0]]
        p1 = grid_dic[r_ids[1]]
        p2 = grid_dic[r_ids[2]]

        # 
        B = v_sub(p1,p0)
        P1 = get_v_element([p0,p1,p2])
        
        # 
        P2 = v_multi_x(P1, t_v)

        theta = 90 - angle_2vector(B, P2)*RAD_2_DEG
        # thetas.append()
        thetas[str(elem_id)] = theta/RAD_2_DEG
        # print(theta)
    # 弧度输出 rad
    return thetas


# 应力转化
def change_stress(xx, yy, xy, theta):
    
    # if (xx-yy) == 0:
    #     theta_p = math.pi/2
    # else:
    #     theta_p = math.atan(xy/(xx-yy)) / 2
    # # print(theta_p)
    # R = ( ((xx-yy)/2)**2 + (xy/2)**2 )**0.5
    # new_xx = (xx+yy)/2 + R*math.cos(theta_p*2 + theta*2)

    # theta 弧度输入
    new_xx = (xx+yy)/2 + (xx-yy)/2*math.cos(2*theta) - xy*math.sin(2*theta)
    new_xy = (xx-yy)/2*math.sin(2*theta) + xy*math.cos(2*theta)

    new_yy = (xx+yy)/2 - (xx-yy)/2*math.cos(2*theta) + xy*math.sin(2*theta)

    return new_xx, new_yy, new_xy


def csv_elem_vs(csv_path, isStr=False):

    """
    elem_id,vx,vy,vz
    18417139,0,0,1
    18415285,0,0,1
    2004699,0,0,1
    """

    if isStr:
        lines = [re.sub('\s','',line) for line in csv_path.split('\n')]
    else:
        with open(csv_path, 'r') as f:
            lines = [re.sub('\s','',line) for line in f.read().split('\n')]

    lines = [line for line in lines if line]

    target_elem_ids = []
    target_vs = []
    for line in lines[1:]:
        values = [value.replace(' ','') for value in line.split(',') if value]
        target_elem_ids.append(int(values[0]))
        target_vs.append([float(value) for value in values[1:4]])

    return target_elem_ids, target_vs




if __name__ == '__main__':

    import time
    
    csv_str = """
    elem_id,vx,vy,vz
    18417139,0,0,1
    18415285,0,0,1
    2004699,0,0,1
    """
    fem_path = 'test.fem'
    target_elem_ids, target_vs = csv_elem_vs(csv_str, True)

    # target_elem_ids = [18417139,18415285,2004699]
    target_vs = [[0,0,1],[0,0,1],[0,0,1]]

    thetas = calc_shell_angle(fem_path, target_elem_ids, target_vs)
    print(thetas)





    # # 获取fem数据
    # grid_dic, elem_dic = read_data(fem_path)

    # target_elem_ids = [18417139,18415285,2004699]
    # target_vs = [[0,0,1],[0,0,1],[0,0,1]]

    # for elem_id, t_v in zip(target_elem_ids,target_vs):
    #     r_ids = elem_dic[str(elem_id)]
    #     p0 = grid_dic[r_ids[0]]
    #     p1 = grid_dic[r_ids[1]]
    #     p2 = grid_dic[r_ids[2]]

    #     # 
    #     B = v_sub(p1,p0)
    #     P1 = get_v_element([p0,p1,p2])
        
    #     # 
    #     P2 = v_multi_x(P1, t_v)

    #     theta = 90 - angle_2vector(B, P2)*RAD_2_DEG

    #     print(theta)


