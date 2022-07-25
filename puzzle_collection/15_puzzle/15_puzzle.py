color("body", 0.15, 0.15, 0.15, 2)
texture("tex", "texture.jpg", 1 / 60, 0, 0, 0, 0, 1 / 60, 1 / 2, 1 / 2)

mb_block = "block.stl"
mb_frame = "frame.stl"
mf = "sticker.stl"
ms = "selector.stl"

block("frame").add_part(mb_frame, "body")
for i in range(4):
	for j in range(4):
		if not (i == 3 and j == 3):
			h_b = block('b{0}{1}'.format(i, j))
			h_b.add_part(mb_block, "body", translate((i - 1.5) * 15, 1, (j - 1.5) * 15))
			h_b.add_part(mf, "tex", translate((i - 1.5) * 15, 2, (j - 1.5) * 15))
			h_b.add_selector(ms, '', translate((i - 1.5) * 15, 0, (j - 1.5) * 15))

		op_base_name = 'op{0}{1}'.format(i, j)
		block_name = 'b{0}{1}'.format(i, j)
		if i > 0:
			h_op = op(op_base_name + 'l')
			h_op.add_moves(translate(-15, 0, 0), [block_name, 'b{0}{1}'.format(i - 1, j)])
			h_op.click(block_name).drag()
		if i < 3:
			h_op = op(op_base_name + 'r')
			h_op.add_moves(translate(15, 0, 0), [block_name, 'b{0}{1}'.format(i + 1, j)])
			h_op.click(block_name).drag()
		if j > 0:
			h_op = op(op_base_name + 'u')
			h_op.add_moves(translate(0, 0, -15), [block_name, 'b{0}{1}'.format(i, j - 1)])
			h_op.click(block_name).drag()
		if j < 3:
			h_op = op(op_base_name + 'd')
			h_op.add_moves(translate(0, 0, 15), [block_name, 'b{0}{1}'.format(i, j + 1)])
			h_op.click(block_name).drag()
