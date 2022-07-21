import cube_3_blank

f = rotate(-120, 1, 1, 1) @ tag_cycle("URF", "DLB", "XYZ")
g = rotate(-120, 1, 1, -1) @ tag_cycle("UBR", "DFL", "ZXW")

color("X", 1, 0.9, 0)
color("Y", 0, 0.2, 1)
color("Z", 1, 0, 0)
color("W", 0, 0.8, 0)

mf = "sticker_3.stl"
mf_sqhalf = "sticker_3_sqhalf.stl"
mf_sqquat = "sticker_3_sqquat.stl"

with group(f, g):
	U = block("U/RF").add_part(mf_sqquat, "X", translate(0, 28.5, 0))
	U.add_part(mf_sqquat, "W", rotate(-90, 0, 1, 0) @ translate(0, 28.5, 0))

	UR = block("UR").add_part(mf_sqhalf, "Z", rotate(90, 0, 1, 0) @ translate(19, 28.5, 0))
	UR.add_part(mf_sqhalf, "X", rotate(-90, 0, 1, 0) @ translate(19, 28.5, 0))

	UF = block("UF").add_part(mf_sqhalf, "X", translate(0, 28.5, 19))
	UF.add_part(mf_sqhalf, "W", rotate(180, 0, 1, 0) @ translate(0, 28.5, 19))

	block("URF").add_part(mf, "X", translate(19, 28.5, 19))
	block("UFL").add_part(mf, "W", translate(-19, 28.5, 19))
