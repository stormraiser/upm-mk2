x = rotate(180, 1, 0, -0.493118) @ tag_cycle("UD", "FB")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")

h = 57
color("body", 0.15, 0.15, 0.15, 2)
color("U", 0.85, 0.85, 0.85)
color("R", 0, 0.25, 1)
color("F", 0.9, 0, 0)
color("D", 0.9, 0.8, 0)
color("L", 0.2, 0.7, 0)
color("B", 1, 0.55, 0)

mb_center = "center_block.stl"
mb_edge = "edge_block.stl"
mb_corner = "corner_block.stl"
mf_center = "center_sticker.stl"
mf_edge = "edge_sticker.stl"
mf_corner = "corner_sticker.stl"
mf_side = "side_sticker.stl"

with group(y):
	U = block("U").add_part(mb_center, "body", translate(0, h / 4, 0))
	U.add_part(mf_center, "U", translate(0, h / 2, 0))
	D = block("D").add_part(mb_center, "body", translate(0, -h / 4, 0))
	D.add_part(mf_center, "D", translate(0, -h / 2, 0))

	UR = block("UR").add_part(mb_edge, "body", translate(0, h / 4, 0))
	UR.add_part(mf_edge, "U", translate(0, h / 2, 0))
	UR.add_part(mf_side, "R", translate(0, h / 4, 0))
	DR = block("DR").add_part(mb_edge, "body", translate(0, -h / 4, 0))
	DR.add_part(mf_edge, "D", translate(0, -h / 2, 0))
	DR.add_part(mf_side, "R", translate(0, -h / 4, 0))

	URF = block("URF").add_part(mb_corner, "body", translate(0, h / 4, 0))
	URF.add_part(mf_corner, "U", translate(0, h / 2, 0))
	URF.add_part(mf_side, "R", rotate(180, 1, 0, 0) @ translate(0, h / 4, 0))
	DFR = block("DFR").add_part(mb_corner, "body", translate(0, -h / 4, 0))
	DFR.add_part(mf_corner, "D", translate(0, -h / 2, 0))
	DFR.add_part(mf_side, "R", rotate(180, 1, 0, 0) @ translate(0, -h / 4, 0))

	with group(x):
		op("U").add_moves(y("U", "UR", "URF")).drag()
		op("U'").add_moves(op("U").inverse()).drag()
		op("R").add_moves(x("UR", "URF", "UBR")).drag()
		op("R'").add_moves(op("R").inverse()).drag()
		op("mR").add_moves(x("U", "UF", "UB")).drag()