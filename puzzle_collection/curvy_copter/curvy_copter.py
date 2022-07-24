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
		"RF:X+14", "UF:M+9",
		"UR1F1:M+9", "BR1U1:N+18", "UF1L1:M+5",
		"URF:M+5", "RFU:M+5", "FUR:M+5",
		"RDF:X+18", "DFR:X+18", "FRD:X+18",
		"ULB:K+5", "LBU:K+5", "BUL:K+5", "UL1B1:K+5",
		"ULB:K+9", "LBU:K+9", "BUL:K+9", "UL1B1:K+9",
		"LUF:M+9", "UFL:M+9", "FLU:M+9", "LB1U1:K+14",
		"ULB:K+18", "LBU:K+18", "BUL:K+18", "UL1B1:K+18"
	]
	op("H+9").add_moves(rotate(-70.528779, 1, 1, 0),
		["RU:H+14", "UR", "UR:H+9"],
		["RUB:H+5", "FUR:X+9", "URF", "URF:H+9", "URF:H+18"],
		["UBR:H+5", "URF:X+9", "RFU", "RFU:H+9", "RFU:H+18"],
		["BRU:H+5", "RFU:X+9", "FUR", "FUR:H+9", "FUR:H+18"],
		["RU1B1:H+5", "FU1R1:X+9", "UR1F1", "UR1F1:H+9", "UR1F1:H+18"],
		["UB1R1:H+5", "UB1R1:H+14", "RF1U1", "RF1U1:H+9", "RF1U1:H+18"]
	).forbid(forbid_list).click("RU:H+14", "UR").drag()
	op("H-9").add_moves(op("H+9").inverse()).forbid(forbid_list).click("UR&r", "UR:H+9&r").drag()
	op("H+5").add_moves(rotate(-38.942441, 1, 1, 0),
		["UR:H+9", "UR:H+14"],
		["URF:H+18", "RUB", "RUB:H+5"],
		["RFU:H+18", "UBR", "UBR:H+5"],
		["FUR:H+18", "BRU", "BRU:H+5"],
		["URF:H+9", "BRU:N+9"], ["RFU:H+9", "RUB:N+9"], ["FUR:H+9", "UBR:N+9"],
		["RU1B1:H+18", "UR1F1", "UR1F1:H+5"], ["UB1R1:H+18", "RF1U1", "RF1U1:H+5"],
		["UR1F1:H+9", "BR1U1:N+9"], ["RF1U1:H+9", "RF1U1:H+14"]
	).forbid(forbid_list + ["UR"]).click("UR:H+9").drag()
	op("H-5").add_moves(op("H+5").inverse()).forbid(forbid_list + ["UR"]).click("UR:H+14&r").drag()
	op("H+23").add_moves(rotate(-180, 1, 1, 0),
		("UR", "RU"), ("UR:H+9", "RU:H+9"), ("UR:H+14", "RU:H+14"),
		("URF", "RUB"), ("RFU", "UBR"), ("FUR", "BRU"),
		("URF:H+5", "RUB:H+5"), ("RFU:H+5", "UBR:H+5"), ("FUR:H+5", "BRU:H+5"),
		("URF:H+9", "RUB:H+9"), ("RFU:H+9", "UBR:H+9"), ("FUR:H+9", "BRU:H+9"),
		("URF:H+18", "RUB:H+18"), ("RFU:H+18", "UBR:H+18"), ("FUR:H+18", "BRU:H+18"),
		("UR1F1", "RU1B1"), ("UR1F1:H+5", "RU1B1:H+5"),
		("UR1F1:H+9", "RU1B1:H+9"),  ("UR1F1:H+18", "RU1B1:H+18"),
		("RF1U1", "UB1R1"), ("RF1U1:H+5", "UB1R1:H+5"), ("RF1U1:H+9", "UB1R1:H+9"),
		("RF1U1:H+14", "UB1R1:H+14"), ("RF1U1:H+18", "UB1R1:H+18")
	).forbid(forbid_list).click("UR&s", "UR:H+9&s", "UR:H+14&s").drag("s")
	op("H-23").add_moves(op("H+23").inverse()).forbid(forbid_list)
	op("H-23").click("UR&rs", "UR:H+9&rs", "UR:H+14&rs").drag("s")
