import bermuda_cube_lib

def make_choices(raw_list):
	face = raw_list[0]
	button_labels = ["Choose " + face + " face type", "Square", "Diamond"] + ["Triangle >" + t for t in raw_list[1:]]
	block_names = [face, face + ":+1"] + [face + "/" + t for t in raw_list[1:]]
	return button_labels, block_names

variant = input_buttons("Choose variant",
	"Mercury", "Venus", "Earth", "Mars",
	"Jupiter", "Saturn", "Uranus", "Neptune", "Customize...")
if variant == 0:
	bermuda_cube_lib.make_bermuda_cube("U:+1", "L", "F", "R", "B", "D/FR")
elif variant == 1:
	bermuda_cube_lib.make_bermuda_cube("U", "L", "F/R", "R", "B/UL", "D")
elif variant == 2:
	bermuda_cube_lib.make_bermuda_cube("U", "L/B", "F/L", "R", "B:+1", "D")
elif variant == 3:
	bermuda_cube_lib.make_bermuda_cube("U/RF", "L", "F", "R/DF", "B", "D/LF")
elif variant == 4:
	bermuda_cube_lib.make_bermuda_cube("U/RF", "L", "F/U", "R/BD", "B", "D")
elif variant == 5:
	bermuda_cube_lib.make_bermuda_cube("U", "L/F", "F/L", "R", "B/RU", "D/RB")
elif variant == 6:
	bermuda_cube_lib.make_bermuda_cube("U/FL", "L", "F", "R/FU", "B/UL", "D/LF")
elif variant == 7:
	bermuda_cube_lib.make_bermuda_cube("U/FL", "L", "F", "R/DF", "B/LD", "D")
else:
	f = tag_cycle("URF", "DLB")
	g = tag_cycle("UD", "RB", "FL")
	raw_list = ["U", "R", "RF", "F", "FL", "L", "LB", "B", "BR"]
	u_labels, u_names = make_choices(raw_list)
	u_type = u_names[input_buttons(*u_labels)]
	l_labels, l_names = make_choices((g @ f).transform(raw_list)[0])
	l_type = l_names[input_buttons(*l_labels)]
	f_labels, f_names = make_choices((f @ f).transform(raw_list)[0])
	f_type = f_names[input_buttons(*f_labels)]
	r_labels, r_names = make_choices(f.transform(raw_list)[0])
	r_type = r_names[input_buttons(*r_labels)]
	b_labels, b_names = make_choices((g @ f @ f).transform(raw_list)[0])
	b_type = b_names[input_buttons(*b_labels)]
	d_labels, d_names = make_choices(g.transform(raw_list)[0])
	d_type = d_names[input_buttons(*d_labels)]
	bermuda_cube_lib.make_bermuda_cube(u_type, l_type, f_type, r_type, b_type, d_type)
 