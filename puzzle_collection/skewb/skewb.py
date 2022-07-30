x = rotate(-90, 1, 0, 0) @ tag_cycle("FUBD", "WHKX", "ZIJY")
f = rotate(-120, 1, 1, 1) @ tag_cycle("URF", "DLB", "KWI", "ZJX")

color("body", 0.15, 0.15, 0.15, 2)
color("U", 0.85, 0.85, 0.85)
color("F", 1, 0, 0)
color("R", 0, 0.2, 1)
color("D", 1, 0.9, 0)
color("B", 1, 0.5, 0)
color("L", 0, 0.8, 0)

m_center = "center_block.stl"
m_corner = "corner_block.stl"
mf_center = "center_sticker.stl"
mf_corner = "corner_sticker.stl"
ms_center_0 = "center_selector_0.stl"
ms_center_1 = "center_selector_1.stl"
ms_corner_0 = "corner_selector_0.stl"
ms_corner_1 = "corner_selector_1.stl"

with group(x, f):
	link_block("U/RF", "U/FL").add_parts((m_center, "body"), (mf_center, "U"))
	block("U/RF").add_selectors(ms_center_0, ms_center_1)

	link_block("URF", "RFU").add_part(m_corner, "body")
	URF = block("URF").add_part(mf_corner, "U")
	URF.add_selectors(ms_corner_0, ms_corner_1)

	op("H").add_moves(f("U/RF", "URF", "UFL")).click("UBR.0", "U/BR.0").drag()
	op("H'").add_moves(op("H").inverse()).click("UFL.1", "U/FL.1").drag()
