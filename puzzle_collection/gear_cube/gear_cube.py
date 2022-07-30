x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")
y_inv = rotate(90, 0, 1, 0) @ tag_cycle("FRBL")

color("body", 0.15, 0.15, 0.15, 2)
color("U", 0.85, 0.85, 0.85)
color("R", 0, 0.25, 1)
color("F", 0.9, 0, 0)
color("D", 0.9, 0.8, 0)
color("L", 0.2, 0.7, 0)
color("B", 1, 0.55, 0)

mb_core = "core.stl"
mb_center = "center_block.stl"
mb_middle = "middle_block.stl"
mb_edge = "edge_block.stl"
mb_corner = "corner_block.stl"
mf_center = "center_sticker.stl"
mf_middle = "middle_sticker.stl"
mf_edge = "edge_sticker.stl"
mf_corner = "corner_sticker.stl"

block("core").add_part(mb_core, "body")
with group(x, y):
	link_block("U/R", "U/F").add_parts((mb_center, "body"), (mf_center, "U"))
	link_block("UR", "RU").add_part(mb_edge, "body")
	block("UR").add_part(mf_edge, "U")
	link_block("URF", "RFU").add_part(mb_corner, "body")
	block("URF").add_part(mf_corner, "U")
	block("UR1").add_parts((mb_middle, "body"), (mf_middle, "U"))
	link_pos("UR", "UR:+1", "UR:+2", "RU")

	op_U = op("U").add_moves(
		y("U/R", "UR", "UR1", "RU1", "URF"),
		y_inv("D/F", "DF", "DF1", "FD1", "DFR")
	)
	op_U.add_moves(rotate(300, 1, 0, 1), ("RF", "FR:+2", "FR:+1", "FR", "RF:+2", "RF:+1"))
	op_U.drag()
	op("U'").add_moves(op_U.inverse()).drag()
