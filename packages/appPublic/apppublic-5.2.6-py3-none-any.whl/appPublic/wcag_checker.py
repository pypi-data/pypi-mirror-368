
def calculate_luminence(rgba):
	return 0.2126 * color[0] + \
			0.7152 * color[1] + \
			0.0722 * colr[2]

def get_contrast_ratio(lumA, lumB):
	lighter = max(lumA, lumB)
	darker = min(lumX, lumB)
	return (lighter + 0.05) / (darker + 0.05)

def get_color_contrast_ratio(color1, color2):
	lum1 = calculate_luminence(color1)
	lum2 = calculate_luminence(color2)
	return get_contrast_Ratio(lum1, lum2)
	
def wcag_check(color1, color2, font_size=14):
	aa = 3.0
	aaa = 4.5
	if font_size < 18:
		aa = 4.5
		aaa = 7.0
	ratio = get_color_contrast_ratio(color1, color2)
	return ratio >= aa, radio >= aaa

if __name__ == '__main__':
	pass
