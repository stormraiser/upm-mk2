from cube_3_lib import *
make_cube_blank()
six_color()

mf = "sticker_3.stl"

with group(*sym_o()):
	link_block("U/RF", "U/FL").add_part(mf, "U", translate(0, 28.5, 0))
	block("UR").add_part(mf, "U", translate(19, 28.5, 0))
	block("URF").add_part(mf, "U", translate(19, 28.5, 19))
