x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD")
y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")

color("body", 0.15, 0.15, 0.15, 2)

mb = "cubelet_3.stl"
ms_center_suquat = "selector_3_center_sqquat.stl"
ms_edge_0 = "selector_3_edge_0.stl"
ms_edge_1 = "selector_3_edge_1.stl"
ms_corner_0 = "selector_3_corner_0.stl"
ms_corner_1 = "selector_3_corner_1.stl"

with group(x, y):
	merge("U/RF", "U/FL").add_part(mb, "body", translate(0, 19, 0))
	block("U/RF").add_selectors(ms_center_suquat)

	merge("UR", "RU").add_part(mb, "body", translate(19, 19, 0))
	block("UR").add_selectors(ms_edge_0, ms_edge_1)

	merge("URF", "RFU").add_part(mb, "body", translate(19, 19, 19))
	block("URF").add_selectors(ms_corner_0, ms_corner_1)

	op("R").add_moves(x("R/FU", "UR", "URF")).add_selectors("R/FU", "FUR.0")
	op("R'").add_moves(op("R").inverse()).add_selectors("R/FU&r", "URF.1")
	op("mR").add_moves(x("U/RF", "UF")).add_selectors("FU.0", "FU.1")
	op("2R").add_moves(op("R"), op("mR")).add_selectors("R/FU&s", "FUR.0&s", "FU.1&s")
	op("2R'").add_moves(op("2R").inverse()).add_selectors("URF.1&s", "R/FU&sr", "UF.0&s")
	op_fR = op("fR").add_moves(op("R"), op("mR"), op("L'"))
	op_fR.add_selectors("R/FU&c", "FUR.0&c", "FU.0&c", "FU.1&c", "FLU.1&c", "L/BU&cr")

op_names = [
	"mR" , "mL" , "mU" , "mD" , "mF" , "mB" , "fR" , "fL" , "fU" , "fD" , "fF" , "fB" , 
	"2R" , "2L" , "2U" , "2D" , "2F" , "2B" , "2R'", "2L'", "2U'", "2D'", "2F'", "2B'"
]
cmds = [
	 "M'",  "M" ,  "E'",  "E" ,  "S'",  "S" ,  "x" ,  "x'",  "y" ,  "y'",  "z" ,  "z'",
	 "r" ,  "l" ,  "u" ,  "d" ,  "f" ,  "b" ,  "r'",  "l'",  "u'",  "d'",  "f'",  "b'"
]
for op_name, cmd in zip(op_names, cmds):
	op(op_name).set_cmd(cmd)
