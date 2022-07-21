import cube_3_blank

x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")

color("0", 0.85, 0.85, 0.85)
color("1", 0.4, 0.4, 0.4)

mf_sqhalf = "sticker_3_sqhalf.stl"
mf_trihalf = "sticker_3_trihalf.stl"
mf_eighth_0 = "sticker_3_eighth_0.stl"
mf_eighth_1 = "sticker_3_eighth_1.stl"

with group(x, y):
	U = block("U/RF").add_part(mf_eighth_0, "0", translate(0, 28.5, 0))
	U.add_part(mf_eighth_1, "1", translate(0, 28.5, 0))

	UR = block("UR").add_part(mf_sqhalf, "0", rotate(-90, 0, 1, 0) @ translate(19, 28.5, 0))
	UR.add_part(mf_sqhalf, "1", rotate(90, 0, 1, 0) @ translate(19, 28.5, 0))

	URF = block("URF").add_part(mf_trihalf, "0", rotate(90, 0, 1, 0) @ translate(19, 28.5, 19))
	URF.add_part(mf_trihalf, "1", rotate(-90, 0, 1, 0) @ translate(19, 28.5, 19))
