x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD", "MNPQ", "HWIX", "KZJY")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB", "XYZW", "MKNH", "QJPI")

color("body", 0.15, 0.15, 0.15, 2)
color("U", 0.85, 0.85, 0.85)
color("R", 0, 0.25, 1)
color("F", 0.9, 0, 0)
color("D", 0.9, 0.8, 0)
color("L", 0.2, 0.7, 0)
color("B", 1, 0.55, 0)

mb_face = "face_block.stl"
mb_edge = "edge_block.stl"
mb_corner = "corner_block.stl"
mf_face = "face_sticker.stl"
mf_edge = "edge_sticker.stl"
mf_corner = "corner_sticker.stl"
ms_edge = "edge_selector.stl"

with group(x, y):
	block("UR1F1").add_parts((mb_face, "body"), (mf_face, "U"))
	merge("UR", "RU").add_part(mb_edge, "body")
	block("UR").add_part(mf_edge, "U").add_selector(ms_edge)
	merge("URF", "RFU").add_part(mb_corner, "body")
	block("URF").add_part(mf_corner, "U")

	forbid_list = [
		"RF:X+3", "UF:M+2", "UR1F1:M+2", "BR1U1:N+4", "UF1L1:M+1",
		"ULB:K+2", "LBU:K+2", "BUL:K+2", "UL1B1:K+2",
		"LUF:M+2", "UFL:M+2", "FLU:M+2", "LB1U1:K+3"
	]
	op("H+2").add_moves(rotate(-70.528779, 1, 1, 0),
		["RU:H+3", "UR", "UR:H+2"],
		["RUB:H+1", "FUR:X+2", "URF", "URF:H+2", "URF:H+4"],
		["UBR:H+1", "URF:X+2", "RFU", "RFU:H+2", "RFU:H+4"],
		["BRU:H+1", "RFU:X+2", "FUR", "FUR:H+2", "FUR:H+4"],
		["RU1B1:H+1", "FU1R1:X+2", "UR1F1", "UR1F1:H+2", "UR1F1:H+4"],
		["UB1R1:H+1", "UB1R1:H+3", "RF1U1", "RF1U1:H+2", "RF1U1:H+4"]
	).forbid(forbid_list).click("RU:H+3", "UR").drag()
	op("H-2").add_moves(op("H+2").inverse()).forbid(forbid_list).click("UR&r", "UR:H+2&r").drag()
	op("H+1").add_moves(rotate(-38.942441, 1, 1, 0),
		["UR:H+2", "UR:H+3"],
		["URF:H+4", "RUB", "RUB:H+1"],
		["RFU:H+4", "UBR", "UBR:H+1"],
		["FUR:H+4", "BRU", "BRU:H+1"],
		["URF:H+2", "BRU:N+2"], ["RFU:H+2", "RUB:N+2"], ["FUR:H+2", "UBR:N+2"],
		["RU1B1:H+4", "UR1F1", "UR1F1:H+1"], ["UB1R1:H+4", "RF1U1", "RF1U1:H+1"],
		["UR1F1:H+2", "BR1U1:N+2"], ["RF1U1:H+2", "RF1U1:H+3"]
	).forbid(forbid_list + ["UR"]).click("UR:H+2").drag()
	op("H-1").add_moves(op("H+1").inverse()).forbid(forbid_list + ["UR"]).click("UR:H+3&r").drag()
