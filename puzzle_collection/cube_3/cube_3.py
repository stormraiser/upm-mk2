import cube_3_blank

x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")

color("U", 0.85, 0.85, 0.85)
color("F", 1, 0, 0)
color("R", 0, 0.2, 1)
color("D", 1, 0.9, 0)
color("B", 1, 0.5, 0)
color("L", 0, 0.8, 0)

mf = "sticker_3.stl"

with group(x, y):
	merge("U/RF", "U/FL").add_part(mf, "U", translate(0, 28.5, 0))
	block("UR").add_part(mf, "U", translate(19, 28.5, 0))
	block("URF").add_part(mf, "U", translate(19, 28.5, 19))
