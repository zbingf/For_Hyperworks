# source D:/github/TclPyHyperWorks/hm/tieCreate/hmtieCreate.tcl
# Tie接触创建
# 面对面创建
# 

namespace eval ::tieCreate {
    variable surf_name
    variable dis_limit
    variable deg_limit
    variable deg_limit_surf

    variable recess
    variable isSaveSelect

    variable file_dir [file dirname [info script]]
}

# set ::tieCreate::file_dir  [file dirname [info script]]

if {[info exists ::tieCreate::surf_name]==0} {set ::tieCreate::surf_name "Tie_Surf2Surf_n"}
if {[info exists ::tieCreate::dis_limit]==0} {set ::tieCreate::dis_limit 1}
if {[info exists ::tieCreate::deg_limit]==0} {set ::tieCreate::deg_limit 10}
if {[info exists ::tieCreate::deg_limit_surf]==0} {set ::tieCreate::deg_limit_surf 70}
if {[info exists ::tieCreate::isSaveSelect]==0} {set ::tieCreate::isSaveSelect 0}

# 获取optistruct_path
proc get_optistruct_path {} {
    set altair_dir [hm_info -appinfo ALTAIR_HOME]
    set optistruct_path [format "%s/templates/feoutput/optistruct/optistruct" $altair_dir]
    return $optistruct_path
}

proc print_elem_node_to_fem {fem_path elem_ids} {
    # 导出指定单元数据到fem
    set altair_dir [hm_info -appinfo ALTAIR_HOME]
    set optistruct_path [format "%s/templates/feoutput/optistruct/optistruct" $altair_dir]
    # elems 1
    eval "*createmark elems 1 $elem_ids"
    # nodes 1
    hm_createmark nodes 1 "by elem" $elem_ids
    # 导出
    hm_answernext yes
    *feoutput_select "$optistruct_path" $fem_path 1 0 0
}


# -------------------------------------
# GUI
if {[grab current] != ""} { return; }

# UI界面
proc ::tieCreate::GUI { args } {
    variable recess;

    set minx [winfo pixel . 225p];
    set miny [winfo pixel . 200p];
    if {![OnPc]} {set miny [winfo pixel . 240p];}
    set graphArea [hm_getgraphicsarea];
    set x [lindex $graphArea 0];
    set y [lindex $graphArea 1];
    
    # 主窗口
    ::hwt::CreateWindow tieCreateWin \
        -windowtitle "TieCreate" \
        -cancelButton "Cancel" \
        -cancelFunc ::tieCreate::Quit \
        -addButton OK ::tieCreate::OkExit no_icon \
        -resizeable 1 1 \
        -propagate 1 \
        -minsize $minx $miny \
        -geometry ${minx}x${miny}+${x}+${y} \
         noGeometrySaving;
    ::hwt::KeepOnTop .tieCreateWin;

    set recess [::hwt::WindowRecess tieCreateWin];

    grid columnconfigure $recess 1 -weight 1;
    grid rowconfigure    $recess 10 -weight 1;

    # ===================
    ::hwt::LabeledLine $recess.end_line1 "单元选择";
    grid $recess.end_line1 -row 2 -column 0 -pady 6 -sticky ew -columnspan 2;

    # ===================
    label $recess.baseLabel -text "Base Elems";
    grid $recess.baseLabel -row 3 -column 0 -padx 2 -pady 2 -sticky nw;

    button $recess.baseButton \
        -text "Select Base Elems" \
        -command ::tieCreate::fun_baseButton \
        -width 16;
    grid $recess.baseButton -row 4 -column 0 -padx 2 -pady 2 -sticky nw;

    # ===================
    label $recess.targetLabel -text "Target Elems";
    grid $recess.targetLabel -row 3 -column 1 -padx 2 -pady 2 -sticky nw;

    button $recess.targetButton \
        -text "Select Target Elems" \
        -command ::tieCreate::fun_targetButton \
        -width 16;
    grid $recess.targetButton -row 4 -column 1 -padx 2 -pady 2 -sticky nw;

    # ===================
    ::hwt::LabeledLine $recess.end_line "";
    grid $recess.end_line -row 5 -column 0 -pady 6 -sticky ew -columnspan 2;

    label $recess.entryLabel1 -text "Surf Name";
    grid $recess.entryLabel1 -row 6 -column 0 -padx 2 -pady 2 -sticky nw;
    entry $recess.entry1 -width 16 -textvariable ::tieCreate::surf_name
    grid $recess.entry1 -row 6 -column 1 -padx 2 -pady 2 -sticky nw;

    label $recess.entryLabel2 -text "单元间-中心距离-Limit";
    grid $recess.entryLabel2 -row 7 -column 0 -padx 2 -pady 2 -sticky nw;
    entry $recess.entry2 -width 16 -textvariable ::tieCreate::dis_limit
    grid $recess.entry2 -row 7 -column 1 -padx 2 -pady 2 -sticky nw;

    label $recess.entryLabel3 -text "单元间-法向夹角-Limit deg";
    grid $recess.entryLabel3 -row 8 -column 0 -padx 2 -pady 2 -sticky nw;
    entry $recess.entry3 -width 16 -textvariable ::tieCreate::deg_limit
    grid $recess.entry3 -row 8 -column 1 -padx 2 -pady 2 -sticky nw;

    label $recess.entryLabel4 -text "单元间-偏移角度-Limit deg";
    grid $recess.entryLabel4 -row 9 -column 0 -padx 2 -pady 2 -sticky nw;
    entry $recess.entry4 -width 16 -textvariable ::tieCreate::deg_limit_surf
    grid $recess.entry4 -row 9 -column 1 -padx 2 -pady 2 -sticky nw;

    checkbutton $recess.checkSelect \
        -text "计算后保留选择" \
        -onvalue 1 \
        -offvalue 0 \
        -variable ::tieCreate::isSaveSelect \
        -command ::tieCreate::fun_checkSelectButton
        # -width 16;
    grid $recess.checkSelect -row 10 -column 0 -padx 2 -pady 2 -sticky nw;

    button $recess.delButton \
        -text "删除名称对应的Tie" \
        -command ::tieCreate::fun_delButton \
        -width 16;
    grid $recess.delButton -row 10 -column 1 -padx 2 -pady 2 -sticky nw;

    ::hwt::RemoveDefaultButtonBinding $recess;
    ::hwt::PostWindow tieCreateWin -onDeleteWindow ::tieCreate::Quit;
}

# 主程序
proc ::tieCreate::OkExit { args } {
    
    set choice [tk_messageBox -type yesnocancel -default yes -message "是否计算" -icon question ]
    if {$choice != yes} {return;}

    set elem_ids_b $::tieCreate::elem_ids_b
    set elem_ids_t $::tieCreate::elem_ids_t

    # 参数
    set surf_1_name "$::tieCreate::surf_name\_A"
    set surf_2_name "$::tieCreate::surf_name\_B"
    set dis_limit $::tieCreate::dis_limit
    set deg_limit $::tieCreate::deg_limit
    set deg_limit_surf $::tieCreate::deg_limit_surf

    # 路径定义
    set temp_path [format "%s/__temp.csv" $::tieCreate::file_dir]
    set fem_path  [format "%s/__temp.fem" $::tieCreate::file_dir]
    set tcl_path  [format "%s/__temp.tcl" $::tieCreate::file_dir]
    set tcl_path2  [format "%s/__temp2.tcl" $::tieCreate::file_dir]
    set tcl_path3  [format "%s/__temp3.tcl" $::tieCreate::file_dir]
    set tcl_path4  [format "%s/__temp4.tcl" $::tieCreate::file_dir]
    set py_path   [format "%s/hmTieSurfToSurfCreate.py" $::tieCreate::file_dir]


    # 导出数据-fem (仅导出显示的数据)
    *clearmarkall 1
    set elem_output_ids [concat $elem_ids_b $elem_ids_t]
    print_elem_node_to_fem $fem_path $elem_output_ids
    
    # 写入文档数据
    set f_obj [open $temp_path w]
    # *createmarkpanel elems 1
    # set elem_ids_b [hm_getmark elems 1]
    puts $f_obj $elem_ids_b
    # *maskentitymark elems 1 0

    # *createmarkpanel elems 2
    # set elem_ids_t [hm_getmark elems 2]
    puts $f_obj $elem_ids_t

    close $f_obj

    # *createmark elems 1 $elem_ids_b
    # *unmaskentitymark elems 1 0

    # ------------------------------------------
    # 调用 python数据
    set result_py [exec python $py_path $dis_limit $deg_limit $deg_limit_surf]
    if {$result_py} {
        puts "python run success!!"
    } else {
        return;
    }

    # ------------------------------------------
    # A surf创建
    source $tcl_path
    *contactsurfcreatewithshells "$surf_1_name" 11 1 0
    *createmark contactsurfs 2 "$surf_1_name"
    *dictionaryload contactsurfs 2 [get_optistruct_path] "SURF"
    # *attributeupdateint contactsurfs 1 3240 1 2 0 1

    # 方向修正
    catch {
        source $tcl_path3
        *reversecontactsurfnormals "$surf_1_name" 1 1
    }

    # ------------------------------------------
    # B surf创建
    source $tcl_path2
    *contactsurfcreatewithshells "$surf_2_name" 11 1 0
    *createmark contactsurfs 2 "$surf_2_name"
    *dictionaryload contactsurfs 2 [get_optistruct_path] "SURF"
    # *attributeupdateint contactsurfs 1 3240 1 2 0 1

    # 方向修正
    catch {
        source $tcl_path4
        *reversecontactsurfnormals "$surf_2_name" 1 1
    }


    # ------------------------------------------
    set surf_name $::tieCreate::surf_name
    # *startnotehistorystate {Interface "$surf_name" created}
    *interfacecreate "$surf_name" 2 3 11
    *createmark groups 2 "$surf_name"
    *dictionaryload groups 2 [get_optistruct_path] "TIE"
    # *endnotehistorystate {Attached attributes to group "$surf_name"}

    *createmark groups 1 "$surf_name"   
    set group_id [hm_getmark groups 1]
    *createmark contactsurfs 1 "$surf_1_name"
    set surf_1_id [hm_getmark contactsurfs 1]
    *createmark contactsurfs 1 "$surf_2_name"
    set surf_2_id [hm_getmark contactsurfs 1]

    *setvalue groups id=$group_id STATUS=2 1997="S2S"
    *setvalue groups id=$group_id STATUS=1 3915=$dis_limit
    *setvalue groups id=$group_id masterentityids={contactsurfs $surf_1_id}
    *setvalue groups id=$group_id slaveentityids={contactsurfs $surf_2_id}


    # ------------------------------------------
    # 删除临时文件
    file delete $temp_path
    file delete $fem_path
    file delete $tcl_path
    file delete $tcl_path2
    file delete $tcl_path3
    file delete $tcl_path4


    puts "-----End-----"
    *clearmarkall 1
    *clearmarkall 2
    tk_messageBox -message "Run End!!!" 

    
    if {$::tieCreate::isSaveSelect==0} {
        set ::tieCreate::elem_ids_b []
        set ::tieCreate::elem_ids_t []   
    }
}

proc ::tieCreate::Quit { args } {
    *clearmarkall 1
    *clearmarkall 2
    ::hwt::UnpostWindow tieCreateWin;
   # ::tieCreate::OkExit;
}


proc ::tieCreate::fun_baseButton { args } {
    *createmarkpanel elems 1 "select the elems"
    # hm_highlightmark elems 1 norm
    set elem_ids [hm_getmark elems 1]
    set ::tieCreate::elem_ids_b $elem_ids
}

proc ::tieCreate::fun_targetButton { args } {
    *createmarkpanel elems 1 "select the elems"
    # hm_highlightmark elems 1 norm
    set elem_ids [hm_getmark elems 1]
    set ::tieCreate::elem_ids_t $elem_ids
}

proc ::tieCreate::fun_delButton {args} {

    set choice [tk_messageBox -type yesnocancel -default yes -message "是否删除" -icon question ]
    if {$choice != yes} {return;}

    set surf_name $::tieCreate::surf_name

    catch {
        *createmark groups 1 "$surf_name"
        *deletemark groups 1
    }
    
    catch {
        *createmark contactsurfs 1 "$surf_name\_A"
        *deletemark contactsurfs 1
    }

    catch {
        *createmark contactsurfs 1 "$surf_name\_B"
        *deletemark contactsurfs 1
    }

}


proc ::tieCreate::fun_checkSelectButton {args} {
    if {$::tieCreate::isSaveSelect==0} {
        set ::tieCreate::elem_ids_b []
        set ::tieCreate::elem_ids_t []   
    }
}

*clearmarkall 1
*clearmarkall 2
::tieCreate::GUI;
