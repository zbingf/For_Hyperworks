"""
	fem_fatigue_edit.py
	version 2.0
	编辑opt耐久计算fem文件的配置
	主要变更内容
		mrf路径 h3d路径 SUBCASE的LABEL字符
	输入
		fem_path
		mrf_path

	输出
		new_fem_path
"""

import re
import os

def read_fem(fem_path):

	f = open(fem_path, 'r')
	return f.read().split('\n')


def write_fem(fem_path, lines):

	with open(fem_path, 'w') as f:
		f.write('\n'.join(lines))

	return None


def change_tcl_path(file_path):

	return file_path.replace('\\', '/')


def new_fem_lines(lines, h3d_path, mrf_path):
	
	lines_new = []

	h3d_path = change_tcl_path(os.path.abspath(h3d_path))
	mrf_path = change_tcl_path(os.path.abspath(mrf_path))

	pattern_h3d = r'(ASSIGN\s*,\s*H3DMBD\s*,\s*\d*\s*,\s*).*'
	pattern_mrf = r'(ASSIGN\s*,\s*MBDINP\s*,\s*\d*\s*,\s*).*'

	is_subcase = False
	n_sublines = 0
	n_subcase  = 0
	for loc, line in enumerate(lines):

		if loc < 100:
			if 'ASSIGN' in line.upper():
				if 'H3DMBD' in line.upper():
					line = re.sub(pattern_h3d, r"\1'{}'".format(h3d_path), line)
				if 'MBDINP' in line.upper():
					line = re.sub(pattern_mrf, r"\1'{}'".format(mrf_path), line)
				# print(line)
				lines_new.append(line)
				continue

			if 'SUBCASE' in line.upper():
				is_subcase = True
				lines_new.append(line)
				n_sublines = 0
				continue

			if is_subcase:
				if n_sublines > 2: is_subcase = False
				if 'LABEL' in line.upper():
					name = os.path.basename(mrf_path)[:-4]	
					name = re.sub('\W', '_', name)
					line = '  LABEL ' + name + '_0{}'.format(n_subcase)
					is_subcase = False
				n_subcase += 1
				n_sublines += 1
				lines_new.append(line)
				continue

		lines_new.append(line)

	return lines_new


def edit_fem_lines(lines, h3d_path, mrf_path):
	
	h3d_path = change_tcl_path(os.path.abspath(h3d_path))
	mrf_path = change_tcl_path(os.path.abspath(mrf_path))

	pattern_h3d = r'(ASSIGN\s*,\s*H3DMBD\s*,\s*\d*\s*,\s*).*'
	pattern_mrf = r'(ASSIGN\s*,\s*MBDINP\s*,\s*\d*\s*,\s*).*'

	is_subcase = False
	n_sublines = 0
	n_subcase  = 0
	for loc, line in enumerate(lines):

		if loc < 100:
			if 'ASSIGN' in line.upper():
				# print(line)
				if 'H3DMBD' in line.upper():
					line = re.sub(pattern_h3d, r"\1'{}'".format(h3d_path), line)
				if 'MBDINP' in line.upper():
					line = re.sub(pattern_mrf, r"\1'{}'".format(mrf_path), line)
				lines[loc] = line
				continue

			if 'SUBCASE' in line.upper():
				is_subcase = True
				n_sublines = 0
				lines[loc] = line
				continue

			if is_subcase:
				if n_sublines > 2: is_subcase = False
				if 'LABEL' in line.upper():
					name = os.path.basename(mrf_path)[:-4]	
					name = re.sub('\W', '_', name)
					line = '  LABEL ' + name + '_0{}'.format(n_subcase)
					is_subcase = False
				n_subcase += 1
				n_sublines += 1
				lines[loc] = line
				continue
		else: 
			break

	return lines


def fatigue_fem_path_edit(fem_paths, h3d_path, mrf_paths):

	new_fem_paths = []

	for fem_path in fem_paths:

		lines = read_fem(fem_path)

		name = os.path.basename(fem_path)[:-4]

		for mrf_path in mrf_paths:
			edit_fem_lines(lines, h3d_path, mrf_path)
			# new_name = name + os.path.basename(mrf_path)[:-3] + 'fem'
			new_name = os.path.basename(mrf_path)[:-4] + '_' + name + '.fem'
			new_dir = os.path.dirname(mrf_path)
			fem_path_new = os.path.join(new_dir ,new_name)
			write_fem(fem_path_new, lines)
			print('fem: {}'.format(fem_path_new))

			new_fem_paths.append(fem_path_new)

	return new_fem_paths



if __name__ == '__main__':
	import tkinter
	import tkinter.filedialog
	tkinter.Tk().withdraw()

	fem_paths = tkinter.filedialog.askopenfilenames(
		filetypes = (('fem', '*.fem'),),
		)


	h3d_path = tkinter.filedialog.askopenfilename(
		filetypes = (('h3d', '*.h3d'),),
		)


	mrf_paths = tkinter.filedialog.askopenfilenames(
		filetypes = (('mrf', '*.mrf'),),
		)

	# print(fem_path)
	# print(h3d_path)
	# print(mrf_paths)
	# 
	fatigue_fem_path_edit(fem_paths, h3d_path, mrf_paths)


	print('----end----')



