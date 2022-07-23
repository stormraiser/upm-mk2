def _to_cycles(t):
	return tuple() if t is None else (t if isinstance(t, tuple) else (t,))

def sym_o(xcycles = None, ycycles = None):
	x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD", *_to_cycles(xcycles))
	y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB", *_to_cycles(ycycles))
	return x, y

def sym_t(fcycles = None, gcycles = None):
	f = rotate(-120, 1, 1, 1) @ tag_cycle("URF", "DLB", *_to_cycles(fcycles))
	g = rotate(-120, 1, 1, -1) @ tag_cycle("UBR", "DFL", *_to_cycles(gcycles))
	return f, g

def make_cube_blank():
	x, y = sym_o()

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

		op("R").add_moves(x("R/FU", "UR", "URF")).click("R/FU", "FUR.0").drag()
		op("R'").add_moves(op("R").inverse()).click("R/FU&r", "URF.1").drag()
		op("mR").add_moves(x("U/RF", "UF")).click("FU.0", "FU.1").drag()
		op("2R").add_moves(op("R"), op("mR")).click("R/FU&s", "FUR.0&s", "FU.1&s").drag("s")
		op("2R'").add_moves(op("2R").inverse()).click("URF.1&s", "R/FU&sr", "UF.0&s").drag("s")
		op_fR = op("fR").add_moves(op("R"), op("mR"), op("L'"))
		op_fR.click("R/FU&c", "FUR.0&c", "FU.0&c", "FU.1&c", "FLU.1&c", "L/BU&cr").drag("c")

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

def six_color():
	color("U", 0.85, 0.85, 0.85)
	color("R", 0, 0.25, 1)
	color("F", 0.9, 0, 0)
	color("D", 0.9, 0.8, 0)
	color("L", 0.2, 0.7, 0)
	color("B", 1, 0.55, 0)

def six_color_alt():
	color("X", 0.85, 0.85, 0.85)
	color("Y", 0, 0.25, 1)
	color("Z", 0.9, 0, 0)
	color("W", 0.9, 0.8, 0)
	color("S", 0.2, 0.7, 0)
	color("T", 1, 0.55, 0)

def four_color():
	color("X", 0.9, 0.8, 0)
	color("Y", 0, 0.25, 1)
	color("Z", 0.9, 0, 0)
	color("W", 0.2, 0.7, 0)

def three_color():
	color("X", 0.9, 0.8, 0)
	color("Y", 0, 0.25, 1)
	color("Z", 0.9, 0, 0)

def sticker_trihalf(fcycle, gcycle, urf_color, ulb_color):
	mf = "sticker_3.stl"
	mf_trihalf = "sticker_3_trihalf.stl"

	with group(*sym_t(fcycle, gcycle)):
		merge("U/RF", "U/FL").add_part(mf_trihalf, urf_color, translate(0, 28.5, 0))
		block("UR").add_part(mf, urf_color, translate(19, 28.5, 0))
		block("UF").add_part(mf, urf_color, translate(0, 28.5, 19))
		block("URF").add_part(mf, urf_color, translate(19, 28.5, 19))
		UFL = block("UFL").add_part(mf_trihalf, urf_color, translate(-19, 28.5, 19))
		UFL.add_part(mf_trihalf, ulb_color, rotate(180, 0, 1, 0) @ translate(-19, 28.5, 19))

def sticker_sqquat_o(xcycle, ycycle, urf_color, ubr_color):
	mf = "sticker_3.stl"
	mf_sqhalf = "sticker_3_sqhalf.stl"
	mf_sqquat = "sticker_3_sqquat.stl"

	with group(*sym_o(xcycle, ycycle)):
		block("U/RF").add_part(mf_sqquat, urf_color, translate(0, 28.5, 0))
		UR = block("UR").add_part(mf_sqhalf, ubr_color, rotate(90, 0, 1, 0) @ translate(19, 28.5, 0))
		UR.add_part(mf_sqhalf, urf_color, rotate(-90, 0, 1, 0) @ translate(19, 28.5, 0))
		block("URF").add_part(mf, urf_color, translate(19, 28.5, 19))

def sticker_sqquat_t(fcycle, gcycle, urf_color, ubr_color, ufl_color):
	mf = "sticker_3.stl"
	mf_sqhalf = "sticker_3_sqhalf.stl"
	mf_sqquat = "sticker_3_sqquat.stl"

	with group(*sym_t(fcycle, gcycle)):
		U = block("U/RF").add_part(mf_sqquat, urf_color, translate(0, 28.5, 0))
		U.add_part(mf_sqquat, ufl_color, rotate(-90, 0, 1, 0) @ translate(0, 28.5, 0))

		UR = block("UR").add_part(mf_sqhalf, ubr_color, rotate(90, 0, 1, 0) @ translate(19, 28.5, 0))
		UR.add_part(mf_sqhalf, urf_color, rotate(-90, 0, 1, 0) @ translate(19, 28.5, 0))

		UF = block("UF").add_part(mf_sqhalf, urf_color, translate(0, 28.5, 19))
		UF.add_part(mf_sqhalf, ufl_color, rotate(180, 0, 1, 0) @ translate(0, 28.5, 19))

		block("URF").add_part(mf, urf_color, translate(19, 28.5, 19))
		block("UFL").add_part(mf, ufl_color, translate(-19, 28.5, 19))
