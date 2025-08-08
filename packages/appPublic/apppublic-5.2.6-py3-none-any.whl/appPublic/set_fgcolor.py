# -*- coding=utf-8 -*-

"""
kivy color:
[ r, g, b, a]
不同的颜色值总能找到一个人眼感知的灰度值，这是著名的心理学公式：
灰度 = 红×0.299 + 绿×0.587 + 蓝×0.114
当灰度值大于0.5时使用暗色，否则使用明色
colors 两个颜色，缺省为空，使用函数内置的两个颜色
"""

def color_gray_rate(color):
	graylevel = 0.299 * color[0] + \
				0.587 * color[1] + \
				0.114 * color[2]
	return graylevel

def get_fgcolor_from_bgcolor(bgcolor, colors=None):
	dark_fgcolor=[0.11,0.11,0.11,1]
	bright_fgcolor=[0.89,0.89,0.89,1]
	
	graylevel = color_gray_rate(bgcolor)
	if colors == None:
		if graylevel > 0.5:
			return dark_fgcolor
		else:
			return bright_fgcolor
	r1 = color_gray_rate(colors[0])
	r2 = color_gray_rate(colors[1])
	if abs(graylevel - r1) > abs(graylevel - r2):
		return colors[0]
	return colors[1]

