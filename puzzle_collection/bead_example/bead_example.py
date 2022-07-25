import math

y = rotate(-120, 0, 1, 0) @ tag_cycle("RYB")

h0 = 4
r0 = 12
bead_r = r0 * math.sin(math.pi / 12)

color("body", 0.15, 0.15, 0.15, 2)
color("R", 0.9, 0, 0, 2)
color("Y", 0.9, 0.8, 0, 2)
color("B", 0, 0.25, 1, 2)

ms = "selector.stl"

block("frame").add_part("frame.stl", "body")
block("rotor").add_part("rotor.stl", "body", rotate(-60, 0, 1, 0)).start_from("rotor_0")

block("s_M").add_selector(ms, '', translate(0, h0 * 2 + bead_r, 0))
with group(y):
	block("s_R").add_selector(ms, '', translate(-r0, h0 * 2 + bead_r, -r0 * 3 ** 0.5))
	for i in range(12):
		block("R" + str(i)).add_part("bead.stl", "R", translate(-r0 * 1.5, h0 * 2, -r0 * 0.5 * 3 ** 0.5) @ rotate(-30 * (i + 0.5), 0, 1, 0, -r0, 0, -r0 * 3 ** 0.5))

	op("M").add_moves(rotate(-60, 0, 1, 0), ("rotor_0", "rotor_1"))
	for i in range(8, 12):
		op("M").add_moves(rotate(-60, 0, 1, 0), ["R" + str(i), "R" + str(i) + ":M+1", "Y" + str(i)])

	op("R").add_moves(rotate(-30, 0, 1, 0, -r0, 0, -r0 * 3 ** 0.5), tuple("R" + str(i) for i in range(12)))
	op("R").forbid("rotor_1").click("s_R")
	op("R'").add_moves(op("R").inverse()).forbid("rotor_1").click("s_R&r")

	op("P").add_moves(rotate(-30, 0, 1, 0, -r0, 0, -r0 * 3 ** 0.5), ["R" + str(i) for i in range(8)])
	op("P").add_moves(rotate(30, 0, 1, 0, r0, 0, -r0 * 3 ** 0.5), ["R" + str(i) + ":M+1" for i in range(11, 7, -1)])
	op("P").add_moves(translate(2 * bead_r * math.tan(math.pi / 24), 0, 2 * bead_r), ["R7", "R11:M+1"])
	op("P").add_moves(translate(r0 - bead_r * 2, 0, -r0 * math.cos(math.pi / 12) * 2 + r0 * 3 ** 0.5), ["R8:M+1", "Y0"])
	op("P").click("s_R")
	op("P'").click("s_R&r")

op("M").click("s_M")
op("M'").add_moves(op("M").inverse()).click("s_M&r")
op("P").forbid("rotor_0")
op("P'").add_moves(op("P").inverse()).forbid("rotor_0")