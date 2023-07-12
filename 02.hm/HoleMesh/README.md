## HoleMesh


### 软件版本
+ hypermesh 2017


-----------------
### 功能
+ 孔网格划分, 在圆孔周围创建正方形网格
+ 当前版本要求: 圆孔离边界较远


-----------------
### 控制参数
+ 圆孔外环偏置
+ 边界偏置
+ 单元尺寸
+ 网格划分模式


-----------------
### 操作
1. 设置控制参数
2. 选择矢量轴参考线
3. 选择圆孔线(每个圆孔选1个line)


-----------------
## 原理
+ 根据选择的轴线生成矢量轴V1
+ 根据圆孔线获取所属的面的法向量V2
+ V1与V2叉乘获得V3(目标矢量轴)
+ V3与V2叉乘获得V4(目标矢量轴)
+ 根据矢量轴创建node点
+ 根据node点分割面, 划分单元


-----------------
### 版本更替
+ v1.0
	+ 仅创建node点, 圆孔边界需为矩形

+ v2.0
	+ 更改圆孔参考坐标轴判定方式
	+ 增加几何面分割
	+ 增加单元划分
	+ 名称变更 hmHoleMesh01.tcl

+ v2.2
	+ 增加GUI界面设置
	+ 支持
		+ 模式1 : 内环 8 外环 8 边界4
		+ 模式2 : 内环 8 外环 4 边界4

+ v3.0
	+ 增加模式
		+ 模式3 : 内环 8 外环 8 边界4, 边界双边超过界限(矩形钢适用)

+ v3.2
	+ 修改边界分割后,是否为目标的判定(内环nodes是否属于surf)
	+ 模式修改:
		+ 支持边界超界限
		+ 模式1 : 双环:: 内环 8 外环 8 边界4
		+ 模式2 : 双环:: 内环 8 外环 4 边界4
		+ 模式3 : 单环:: 内环 8 边界4
		+ 模式4 : 单环:: 内环 8 边界8
+ v3.3
	+ 修改create_circle_node_by_line, 将line_base_id 改为线上的两个坐标点line_base_2_locs, 避免line_base_id的变更引起的报错

+ v3.4
	+ 节点创建优化, 增加起始偏转角
	```
		proc create_circle_node_with_v
	```
	+ 增加自定义UI界面
+ v3.5
	+ 优化UI界面

+ v3.6
	+ 函数名称变更

+ v3.7
	+ point不会随surf的分割而变更ID, 将初始line切换为pointID,再根据pointID找新lineID
	```
	    foreach line_circle_id $line_circle_ids {
        *createmark points 1 "by lines" $line_circle_id
        dict set cirlce_line_to_point $line_circle_id [lindex [hm_getmark points 1] 0]
	    }


	    foreach line_circle_id $line_circle_ids {
	        *createmark lines 1 "by points" [dict get $cirlce_line_to_point $line_circle_id ]
	        set line_circle_id [lindex [hm_getmark lines 1] 0]
	        ...
	```