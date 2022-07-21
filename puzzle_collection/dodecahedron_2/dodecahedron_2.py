phi = (5 ** 0.5 + 1) / 2
ax = (phi ** 2 + phi * 2) / 5
ay = (phi ** 2 * 2 + phi * 2 + 1) / 5

x = rotate(-72, ax, ay, 0) @ tag_cycle("RFVCS", "GMLBE")
y = rotate(-72, 0, ax, ay) @ tag_cycle("URGMV", "SEDLC")

color("body", 0.15, 0.15, 0.15, 2)
color("U", 0.9, 0.9, 0.9)
color("D", 0.4, 0.4, 0.4)
color("F", 1, 0.5, 0.5)
color("B", 0.7, 0, 0)
color("R", 0.5, 0.85, 1)
color("L", 0, 0.2, 0.9)
color("C", 1, 0.9, 0.2)
color("G", 0.6, 0.55, 0)
color("M", 1, 0.75, 0.3)
color("S", 0.6, 0.3, 0)
color("E", 0.4, 1, 0.2)
color("V", 0, 0.5, 0)

m_corner = "corner_block.stl"
m_edge = "edge_block.stl"
m_center = "center_block.stl"
mf = "sticker.stl"
ms_0 = "selector_0.stl"
ms_1 = "selector_1.stl"

with group(x, y):
	block("F").add_part(m_center, "body")
	block("FU").add_part(m_edge, "body")

	merge("FUR", "URF").add_part(m_corner, "body")
	FUR = block("FUR").add_part(mf, "F")
	FUR.add_selectors(ms_0, ms_1)

	op("F").add_moves(y("FUR", "FU", "UF", "F")).add_selectors("URF.0")
	op("F'").add_moves(op("F").inverse()).add_selectors("RFU.1")
