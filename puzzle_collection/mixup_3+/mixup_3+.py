x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")

color("body", 0.15, 0.15, 0.15, 2)
color("U", 0.85, 0.85, 0.85)
color("R", 0, 0.25, 1)
color("F", 0.9, 0, 0)
color("D", 0.9, 0.8, 0)
color("L", 0.2, 0.7, 0)
color("B", 1, 0.55, 0)

mb_f = "center_block.stl"
mb_e = "edge_block.stl"
mb_m = "middle_block.stl"
mb_c = "corner_block.stl"
mf_f = "center_sticker.stl"
mf_e = "edge_sticker.stl"
mf_m = "middle_sticker.stl"
mf_c = "corner_sticker.stl"

with group(x, y):
	merge("U/R", "U/F").add_parts((mb_f, "body"), (mf_f, "U"))
	merge("UR", "UR:+1", "RU").add_part(mb_e, "body")
	block("UR").add_part(mf_e, "U")
	block("UR1").add_parts((mb_m, "body"), (mf_m, "U"))
	merge("URF", "RFU").add_part(mb_c, "body")
	block("URF").add_part(mf_c, "U")
	op("U").add_moves(y("U/R", "UR", "UR1", "UR1:+1", "RU1", "RU1:+1", "URF")).drag()
	op("U'").add_moves(op("U").inverse()).drag()
	op("mU").add_moves(rotate(-45, 0, 1, 0),
		["R/U", "RF:+1", "F/U"], ["R/B", "FR", "F/R"],
		["R/D", "FR:+1", "F/D"], ["R/F", "RF", "F/L"],
		["RF1", "FR1:+1", "FL1"], ["RF1:+1", "FR1", "FL1:+1"],
	).drag()
