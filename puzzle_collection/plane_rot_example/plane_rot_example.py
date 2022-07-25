y = rotate(180, 0, 1, 0) @ tag_cycle("UD")

t = 14 * (0.5 + 0.5 * 3 ** 0.5)
color("body", 0.15, 0.15, 0.15, 2)
texture("tex", "texture.jpg", 1 / 59.2487, 0, 0, 0, 0, 1 / 97.4974, 1 / 2, 1 / 2)

mb_frame = "frame.stl"
mb_center = "center_block.stl"
mb_edge = "edge_block.stl"
mb_corner = "corner_block.stl"
mf_frame = "frame_sticker.stl"
mf_center = "center_sticker.stl"
mf_edge = "edge_sticker.stl"
mf_corner = "corner_sticker.stl"
ms = "selector.stl"

frame = block("frame").add_part(mb_frame, "body")
frame.add_part(mf_frame, "tex", translate(0, 2, 0))
frame.add_selector(ms, "U")
frame.add_selector(ms, "D", rotate(180, 0, 1, 0))
with group(y):
	U = block("U").add_part(mb_center, "body", translate(0, 1, 0))
	U.add_part(mf_center, "tex", translate(0, 2, 0))
	for i in range(5):
		Ue = block("Ue" + str(i)).add_part(mb_edge, "body", translate(0, 1, 0) @ rotate(-60 * (i + 1), 0, 1, 0, 0, 0, -t))
		Ue.add_part(mf_edge, "tex", translate(0, 2, 0) @ rotate(-60 * (i + 1), 0, 1, 0, 0, 0, -t))
		Uc = block("Uc" + str(i)).add_part(mb_corner, "body", translate(0, 1, 0) @ rotate(-60 * i, 0, 1, 0, 0, 0, -t))
		Uc.add_part(mf_corner, "tex", translate(0, 2, 0) @ rotate(-60 * i, 0, 1, 0, 0, 0, -t))
	M = block("M").add_part(mb_edge, "body", translate(0, 1, 0))
	M.add_part(mf_edge, "tex", translate(0, 2, 0))

	u_rot = rotate(-60, 0, 1, 0, 0, 0, -t)
	op_U = op("U")
	for i in range(4):
		op_U.add_moves(u_rot,
			["Ue" + str(i), "Ue" + str(i + 1)],
			["Uc" + str(i), "Uc" + str(i + 1)],
			["Uc" + str(i) + ":+1", "Uc" + str(i + 1) + ":+1"],
			["Uc" + str(i) + ":+2", "Uc" + str(i + 1) + ":+2"]
		)
	op_U.add_moves(u_rot,
		("U", "U:+1", "U:+2", "U:+3", "U:+4", "U:+5"),
		["Ue4", "M", "Ue0"],
		["Uc4", "Dc0:+1", "Uc0"],
		["Uc4:+1", "Dc0:+2", "Uc0:+1"],
		["Uc4:+2", "Dc0", "Uc0:+2"]
	)
	op_U.click("frame.U").drag()
	op("U'").add_moves(op_U.inverse()).click("frame.U&r").drag()
