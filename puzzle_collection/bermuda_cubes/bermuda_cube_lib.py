def make_bermuda_cube(u_type, l_type, f_type, r_type, b_type, d_type):
	color("body", 0.15, 0.15, 0.15, 2)
	color("U", 0.85, 0.85, 0.85)
	color("R", 0, 0.25, 1)
	color("F", 0.9, 0, 0)
	color("D", 0.9, 0.8, 0)
	color("L", 0.2, 0.7, 0)
	color("B", 1, 0.55, 0)

	face_blocks = [u_type, l_type, f_type, r_type, b_type, d_type]
	faces = "ULFRBD"
	for face, face_block in zip(faces, face_blocks):
		if face_block[0] != face:
			raise ValueError("invalid face type")

	mb_f4 = "center_square.stl"
	mf_f4 = "center_sticker_square.stl"
	mb_f3 = "center_triangle.stl"
	mf_f3 = "center_sticker_triangle.stl"
	mb_e4 = "edge_square.stl"
	mf_e4 = "edge_sticker_square.stl"
	mb_e5 = "edge_pentagon.stl"
	mf_e5 = "edge_sticker_pentagon.stl"
	mb_c4 = "corner_square.stl"
	mf_c4 = "corner_sticker_square.stl"
	mb_c3 = "corner_triangle.stl"
	mf_c3 = "corner_sticker_triangle.stl"
	ms_f4 = "selector_square.stl"
	ms_f3 = "selector_triangle.stl"

	x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD")
	y = rotate(-90, 0, 1, 0) @ tag_cycle("RFLB")
	sym = group(x, y)
	with sym:
		block("U").add_parts((mb_f4, "body"), (mf_f4, "U"))
		block("U").add_selector(ms_f4)
		block("U:+1").add_parts(
			(mb_f4, "body", rotate(-45, 0, 1, 0)),
			(mf_f4, "U", rotate(-45, 0, 1, 0))
		)
		block("U:+1").add_selector(ms_f4, '', rotate(-45, 0, 1, 0))
		block("U/RF").add_parts((mb_f3, "body"), (mf_f3, "U"))
		block("U/RF").add_selector(ms_f3)
		block("U/R").add_parts(
			(mb_f3, "body", rotate(45, 0, 1, 0)),
			(mf_f3, "U", rotate(45, 0, 1, 0))
		)
		block("U/R").add_selector(ms_f3, '', rotate(45, 0, 1, 0))
		link_block("UR", "RU").add_part(mb_e4, "body")
		block("UR").add_part(mf_e4, "U")
		block("UR:U+1").add_parts(
			(mb_e5, "body"),
			(mf_e5, "U"),
			(mf_c4, "R", rotate(-120, 1, 1, 1)),
			(mf_c4, "F", rotate(120, 1, 1, 1))
		)
		link_block("URF", "RFU").add_part(mb_c4, "body")
		block("URF").add_part(mf_c4, "U")
		block("UBR:U+1").add_parts(
			(mb_c3, "body"),
			(mf_c3, "U"),
			(mf_e4, "R", rotate(180, 1, 1, 0))
		)
		link_pos("URF", "RFU")
		link_pos("UR", "RU")
		link_pos("URF:U+1", "RFU:U+1", "FUR:U+1")
		link_pos("UR:U+1", "RU:U+1")

		forbid_list = ["R/UB", "R/B", "R/D", "R/F", "R/FU", "R:+1"]
		op("U").add_moves(rotate(-45, 0, 1, 0),
			("U", "U:+1"), ["U/R", "U/RF", "U/F"],
			["URF", "URF:U+1", "UFL"], ["UR", "UR:U+1", "UF"],
		).forbid(forbid_list).click("U", "U:+1", "U/R", "U/RF").drag()
		op("U'").add_moves(op("U").inverse())
		op("U'").forbid(forbid_list).click("U&r", "U:+1&r", "U/R&r", "U/RF&r").drag()

	for face_block in face_blocks:
		if not block(face_block).exists():
			raise ValueError("invalid face type")

	block_incompat_lists = [
		["U", ["URF:U+1", "UR:U+1"]],
		["U:+1", ["URF", "UR"]],
		["U/RF", ["URF", "UFL:U+1", "ULB:U+1", "UR", "UF", "UF:U+1", "UL:U+1", "UB:U+1"]],
		["U/R", ["UFL", "ULB", "UBR:U+1", "UR:U+1", "UF", "UL", "UB", "UB:U+1"]]
	]
	for block_incompat_list in block_incompat_lists:
		for face_block, other_blocks in sym.transform(block_incompat_list):
			if face_block in face_blocks:
				for other_block in other_blocks:
					if not block(other_block).exists():
						raise RuntimeError("incompatible face types")
					block(other_block).remove()
			else:
				block(face_block).remove()
