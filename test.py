import os, math, time, sys, struct
import importlib, builtins, pathlib

import numpy as np
import pyglet
import moderngl

from mat_utils import *
import core

vertex_shader_code = '''
#version 330

in vec3 in_vpos;
in vec3 in_vnormal;
in vec4 in_vcolor;
in mat4 mmat;
in mat4 mvp;
in vec3 in_light_pos;

out vec3 vpos;
out vec3 vnormal;
out vec4 vcolor;
out vec3 light_pos;

void main() {
	vpos = vec3(mmat * vec4(in_vpos, 1.0));
	vnormal = vec3(mmat * vec4(in_vnormal, 0.0));
	vcolor = in_vcolor;
	light_pos = in_light_pos;
	gl_Position = mvp * vec4(in_vpos, 1.0);
}
'''

fragment_shader_code = '''
#version 330

in vec3 vpos;
in vec3 vnormal;
in vec4 vcolor;
in vec3 light_pos;

out vec3 out_fcolor;

void main() {
	vec3 d = light_pos - vpos;
	float sqdis = dot(d, d);
	vec3 d_n = d / sqrt(sqdis);
	float t = max(dot(d_n, vnormal), 0);
	t = (t + pow(t, 10) * vcolor[3]) / sqdis;
	out_fcolor = vec3(vcolor) * (t * 550000 + 0.2);
}
'''

tex_vertex_shader_code = '''
#version 330

in vec3 in_vpos;
in vec3 in_vnormal;
in mat4 mmat;
in mat4 mvp;
in mat4 tcmat;
in vec3 in_light_pos;
in vec2 in_highlight;

out vec3 vpos;
out vec3 vnormal;
out vec3 light_pos;
out vec2 tex_coord;
out vec2 highlight;

void main() {
	vpos = vec3(mmat * vec4(in_vpos, 1.0));
	vnormal = vec3(mmat * vec4(in_vnormal, 0.0));
	tex_coord = vec2(tcmat * vec4(in_vpos, 1.0));
	light_pos = in_light_pos;
	highlight = in_highlight;
	gl_Position = mvp * vec4(in_vpos, 1.0);
}
'''

tex_fragment_shader_code = '''
#version 330

in vec3 vpos;
in vec3 vnormal;
in vec3 light_pos;
in vec2 tex_coord;
in vec2 highlight;

uniform sampler2D tex;

out vec3 out_fcolor;

void main() {
	vec3 vcolor = vec3(texture(tex, tex_coord)) * highlight[0] + highlight[1];
	vec3 d = light_pos - vpos;
	float sqdis = dot(d, d);
	vec3 d_n = d / sqrt(sqdis);
	float t = max(dot(d_n, vnormal), 0) / sqdis;
	out_fcolor = vcolor * (t * 550000 + 0.2);
}
'''

picker_vertex_shader_code = '''
#version 330

in vec3 in_vpos;
in vec3 in_vcolor;
in mat4 mvp;

out vec3 vcolor;

void main() {
	vcolor = in_vcolor;
	gl_Position = mvp * vec4(in_vpos, 1.0);
}
'''

picker_fragment_shader_code = '''
#version 330

in vec3 vcolor;

out vec3 out_fcolor;

void main() {
	out_fcolor = vcolor;
}
'''

window_w = 640
window_h = 480
short_side = min(window_w, window_h)
animation_time = 0.5
base_path = pathlib.Path(__file__).resolve()
sys.path.append(str(base_path.parent / 'lib'))
puzzle_path = pathlib.Path(sys.argv[1]).resolve()
sys.path.append(str(puzzle_path.parent))

class PuzzleWindow(pyglet.window.Window):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.puzzle = core.Puzzle(puzzle_path, base_path.parent / 'lib')

		self.cam_pos = np.array([150, 150, 150], dtype = np.float32)
		self.look_at = np.array([0, 0, 0], dtype = np.float32)
		self.y_vec = np.array([0, 1, 0], dtype = np.float32)
		self.view_mat = make_view_mat(self.cam_pos, self.look_at, self.y_vec)
		self.inv_view_mat = np.linalg.inv(self.view_mat)

		self.near = 100
		self.far = 400
		self.view_h = math.tan(25 / 180 * math.pi)
		self.aspect = 4 / 3
		self.proj_mat = make_proj_mat(math.atan(self.view_h), self.aspect, self.near, self.far)

		self.ctx = moderngl.create_context()
		self.ctx.enable(moderngl.DEPTH_TEST)
		self.shader_program = self.ctx.program(
			vertex_shader = vertex_shader_code,
			fragment_shader = fragment_shader_code
		)
		self.tex_shader_program = self.ctx.program(
			vertex_shader = tex_vertex_shader_code,
			fragment_shader = tex_fragment_shader_code
		)
		self.picker_shader_program = self.ctx.program(
			vertex_shader = picker_vertex_shader_code,
			fragment_shader = picker_fragment_shader_code
		)

		self.puzzle.init_gl(self.ctx)

		self.light_pos = np.array([300, 600, 450], dtype = np.float32)
		self.vbo_light_pos = self.ctx.buffer(self.light_pos.tobytes())

		self.time0 = time.time()

		self.picker_buffer = self.ctx.simple_framebuffer((window_w, window_h))
		self.mmat_t = np.eye(4, dtype = np.float32)
		self.inv_mmat_t = np.eye(4, dtype = np.float32)

		self.shift_down = False
		self.ctrl_down = False
		self.alt_down = False

		self.lhighlight = -1
		self.rhighlight = -1
		self.picked_block = -1
		self.picked_pos = None
		self.last_mouse_x = 0
		self.last_mouse_y = 0
		self.mouse_down_x = 0
		self.mouse_down_y = 0
		self.mouse_down_block = -1
		self.mouse_down_pos = None
		self.mouse_move_after_down = False
		self.drag_path = []

		self.animating = False
		self.animation_start = 0

	def pixel_to_trackball(self, px, py):
		l = short_side / 2
		x = (px - window_w / 2 + 0.5) / l
		y = (py - window_h / 2 + 0.5) / l
		r = x * x + y * y
		z = (2 - r) ** 0.5 if r <= 1 else 1 / r ** 0.5
		return x, y, z

	def update(self, dt):
		if self.animating:
			current_time = time.time()
			if current_time - self.animation_start >= animation_time:
				self.animating = False
				self.puzzle.finish_op()
				self.update_active_selector(self.last_mouse_x, self.last_mouse_y)
			else:
				self.puzzle.animate(t = (current_time - self.animation_start) / animation_time)

	def unproject(self, x, y, depth):
		depth = depth * 2 - 1
		px = (x - window_w / 2 + 0.5) / window_w * 2
		py = (y - window_h / 2 + 0.5) / window_h * 2
		vz = -2 * self.near * self.far / ((self.near - self.far) * depth + self.near + self.far)
		pw = -vz
		vx = pw * px / self.proj_mat[0, 0]
		vy = pw * py / self.proj_mat[1, 1]
		vpos = np.array([vx, vy, vz, 1], dtype = np.float32)
		ppos = self.proj_mat @ vpos
		ppos = ppos[:3] / ppos[3]
		return self.inv_mmat_t @ (self.inv_view_mat @ vpos)

	def drag_match(self, drag_path, drag_matching_paths):
		if len(drag_matching_paths) == 0:
			return -1
		h = max(1, len(drag_path) // 20)
		dpath = np.array(drag_path[::h], dtype = np.float32)
		min_dis = 1e10
		min_id = -1
		for op_id, path in drag_matching_paths:
			mpath = ((self.proj_mat @ self.view_mat @ self.mmat_t) @ path.transpose()).transpose()
			mpath = mpath[:, :2] / mpath[:, 3:]
			mx = (mpath[:, 0] + 1) / 2 * window_w - 0.5
			my = (mpath[:, 1] + 1) / 2 * window_h - 0.5
			mpath = np.stack((mx, my), 1)
			diff = np.expand_dims(dpath, 1) - np.expand_dims(mpath, 0)
			dis = np.sqrt(np.power(diff, 2).sum(2))
			min_point_dis = np.amin(dis, 1)
			total_dis = min_point_dis.sum()
			if total_dis < min_dis:
				min_dis = total_dis
				min_id = op_id
		return min_id

	def update_active_selector(self, x, y):
		if self.animating:
			return

		self.picker_buffer.use()
		self.ctx.clear(0, 0, 0)
		self.picker_buffer.scissor = (x, y, 1, 1)

		for model in self.puzzle.model_list:
			part_instances = sum(model.tex_instances, start = model.part_instances)
			if len(part_instances) > 0:
				all_inst_data = []
				for block_id, part_id in part_instances:
					block = self.puzzle.block_list[block_id]
					part = block.part_list[part_id]
					color = np.array(part[3], dtype = np.float32)
					mvp = self.proj_mat @ self.view_mat @ self.mmat_t @ block.next_transform @ part[2]
					inst_data = np.concatenate((color, mvp.transpose().reshape(16)), 0)
					all_inst_data.append(inst_data)
				vbo_inst = self.ctx.buffer(np.stack(all_inst_data, 0).tobytes())
				vao = self.ctx.vertex_array(
					self.picker_shader_program,
					[
						(model.vbo_pos, "3f /v", "in_vpos"),
						(vbo_inst, "3f 16f /i", "in_vcolor", "mvp")
					]
				)
				vao.render(moderngl.TRIANGLES, instances = len(part_instances))
				vbo_inst.release()
				vao.release()

		r, g, b = self.picker_buffer.read(viewport = (x, y, 1, 1))
		depth = self.picker_buffer.read(attachment = -1, viewport = (x, y, 1, 1), dtype = 'f4')
		depth = struct.unpack('f', depth)[0]
		picked_part = self.puzzle.pick_color_to_instance_id(r, g, b)
		if picked_part >= 0:
			self.picked_block = self.puzzle.part_id_to_block_id[picked_part]
			self.picked_pos = self.unproject(x, y, depth)
		else:
			self.picked_block = -1

		for model in self.puzzle.model_list:
			if len(model.selector_instances) > 0:
				all_inst_data = []
				for block_id, selector_id in model.selector_instances:
					block = self.puzzle.block_list[block_id]
					selector = block.selector_list[selector_id]
					color = np.array(selector[3], dtype = np.float32)
					mvp = self.proj_mat @ self.view_mat @ self.mmat_t @ block.next_transform @ selector[1]
					inst_data = np.concatenate((color, mvp.transpose().reshape(16)), 0)
					all_inst_data.append(inst_data)
				vbo_inst = self.ctx.buffer(np.stack(all_inst_data, 0).tobytes())
				vao = self.ctx.vertex_array(
					self.picker_shader_program,
					[
						(model.vbo_pos, "3f /v", "in_vpos"),
						(vbo_inst, "3f 16f /i", "in_vcolor", "mvp")
					]
				)
				vao.render(moderngl.TRIANGLES, instances = len(model.selector_instances))
				vbo_inst.release()
				vao.release()

		r, g, b = self.picker_buffer.read(viewport = (x, y, 1, 1))
		picked_selector = self.puzzle.pick_color_to_instance_id(r, g, b, selector = True)
		if picked_selector >= 0:
			mid_id = (4 if self.shift_down else 0) + (2 if self.ctrl_down else 0) + (1 if self.alt_down else 0)
			self.lhighlight = self.puzzle.current_click_map[picked_selector, mid_id]
			self.rhighlight = self.puzzle.current_click_map[picked_selector, mid_id + 8]
		else:
			self.lhighlight = -1
			self.rhighlight = -1

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.drag_path.append((x, y))
		self.last_mouse_x = x
		self.last_mouse_y = y
		self.mouse_move_after_down = True
		if buttons & pyglet.window.mouse.RIGHT:
			vv0 = np.array(self.pixel_to_trackball(x - dx, y - dy), dtype = np.float32)
			wv0 = self.view_mat[:3, :3].transpose() @ vv0
			wv0 = wv0 / np.linalg.norm(wv0)
			vv1 = np.array(self.pixel_to_trackball(x, y), dtype = np.float32)
			wv1 = self.view_mat[:3, :3].transpose() @ vv1
			wv1 = wv1 / np.linalg.norm(wv1)
			n = np.cross(wv0, wv1)
			n = n / np.linalg.norm(n)
			n = np.array([n[0], n[1], n[2], 0], dtype = np.float32)
			angle = math.acos(min(1, np.dot(wv0, wv1))) * 1.5
			self.mmat_t = core.rotation_mat(n, angle) @ self.mmat_t
			self.inv_mmat_t = np.linalg.inv(self.mmat_t)
		elif buttons & pyglet.window.mouse.MIDDLE:
			l = short_side / 2
			t = (dx * self.view_mat[0, :3] + dy * self.view_mat[1, :3]) / l * 50
			self.mmat_t = core.translation_mat(t) @ self.mmat_t
			self.inv_mmat_t = np.linalg.inv(self.mmat_t)
		#self.update_active_selector(x, y)

	def on_key_press(self, symbol, modifiers):
		if symbol in [pyglet.window.key.LSHIFT, pyglet.window.key.RSHIFT]:
			self.shift_down = True
		elif symbol in [pyglet.window.key.LCTRL, pyglet.window.key.RCTRL]:
			self.ctrl_down = True
		elif symbol in [pyglet.window.key.LALT, pyglet.window.key.RALT]:
			self.alt_down = True
		self.update_active_selector(self.last_mouse_x, self.last_mouse_y)

	def on_key_release(self, symbol, modifiers):
		if symbol in [pyglet.window.key.LSHIFT, pyglet.window.key.RSHIFT]:
			self.shift_down = False
		elif symbol in [pyglet.window.key.LCTRL, pyglet.window.key.RCTRL]:
			self.ctrl_down = False
		elif symbol in [pyglet.window.key.LALT, pyglet.window.key.RALT]:
			self.alt_down = False
		self.update_active_selector(self.last_mouse_x, self.last_mouse_y)

	def on_mouse_press(self, x, y, button, modifiers):
		if button == pyglet.window.mouse.LEFT:
			self.mouse_down_x = x
			self.mouse_down_y = y
			self.mouse_down_block = self.picked_block
			self.mouse_down_pos = self.picked_pos
			self.drag_path = [(x, y)]

	def on_mouse_release(self, x, y, button, modifiers):
		if self.mouse_move_after_down:
			self.mouse_move_after_down = False
			if (button == pyglet.window.mouse.LEFT) and (self.mouse_down_block >= 0):
				move_dis = ((x - self.mouse_down_x) ** 2 + (y - self.mouse_down_y) ** 2) ** 0.5
				if move_dis >= short_side / 50:
					self.lhighlight = -1
					self.rhighlight = -1
					self.picked_block = -1
					mid_id = (4 if self.shift_down else 0) + (2 if self.ctrl_down else 0) + (1 if self.alt_down else 0)
					drag_matching_paths = self.puzzle.get_drag_matching_path(self.mouse_down_block, self.mouse_down_pos, mid_id)
					op_id = self.drag_match(self.drag_path, drag_matching_paths)
					if op_id >= 0:
						self.puzzle.start_op(op_id)
						self.animating = True
						self.animation_start = time.time()
						return
			self.update_active_selector(x, y)
		else:
			self.on_mouse_click(x, y, button)

	def on_mouse_motion(self, x, y, dx, dy):
		self.last_mouse_x = x
		self.last_mouse_y = y
		self.update_active_selector(x, y)

	def on_mouse_click(self, x, y, button):
		if self.animating:
			return
		if button & pyglet.window.mouse.LEFT:
			op_id = self.lhighlight
		elif button & pyglet.window.mouse.RIGHT:
			op_id = self.rhighlight
		if op_id == -1:
			return
		self.puzzle.start_op(op_id)
		self.animating = True
		self.animation_start = time.time()

	def on_draw(self):
		self.ctx.screen.use()
		self.ctx.clear(0.7, 0.7, 0.7)

		highlight_ops = []
		if self.lhighlight >= 0:
			highlight_ops.append(self.lhighlight)
		if self.rhighlight >= 0:
			highlight_ops.append(self.rhighlight)
		self.puzzle.set_highlight(highlight_ops)

		for model in self.puzzle.model_list:
			if len(model.part_instances) > 0:
				all_inst_data = []
				for block_id, part_id in model.part_instances:
					block = self.puzzle.block_list[block_id]
					part = block.part_list[part_id]
					color = part[1]
					if isinstance(color, str):
						color = np.array(self.puzzle.clr_tex_map[color][1:], dtype = np.float32)
					if block.highlight:
						color = np.concatenate((color[:3] * 0.85 + 0.25, color[3:]), 0)
					model_mat = self.mmat_t @ block.next_transform @ part[2]
					mvp = self.proj_mat @ self.view_mat @ model_mat
					inst_data = np.concatenate((color, model_mat.transpose().reshape(16), mvp.transpose().reshape(16)), 0)
					all_inst_data.append(inst_data)
				vbo_inst = self.ctx.buffer(np.stack(all_inst_data, 0).tobytes())
				vao = self.ctx.vertex_array(
					self.shader_program,
					[
						(model.vbo_pos, "3f /v", "in_vpos"),
						(model.vbo_normal, "3f /v", "in_vnormal"),
						(vbo_inst, "4f 16f 16f /i", "in_vcolor", "mmat", "mvp"),
						(self.vbo_light_pos, "3f /r", "in_light_pos")
					]
				)
				vao.render(moderngl.TRIANGLES, instances = len(model.part_instances))
				vbo_inst.release()
				vao.release()

			for k, one_tex_instances in enumerate(model.tex_instances):
				if len(one_tex_instances) > 0:
					self.puzzle.texture_list[k].gl_tex.use()
					all_inst_data = []
					for block_id, part_id in one_tex_instances:
						block = self.puzzle.block_list[block_id]
						part = block.part_list[part_id]
						if block.highlight:
							highlight = np.array([0.85, 0.25], dtype = np.float32)
						else:
							highlight = np.array([1, 0], dtype = np.float32)
						tcmat = self.puzzle.clr_tex_map[part[1]][2]
						tcmat = tcmat @ part[2]
						model_mat = self.mmat_t @ block.next_transform @ part[2]
						mvp = self.proj_mat @ self.view_mat @ model_mat
						inst_data = np.concatenate((
							model_mat.transpose().reshape(16),
							mvp.transpose().reshape(16),
							tcmat.transpose().reshape(16),
							highlight
						), 0)
						all_inst_data.append(inst_data)
					vbo_inst = self.ctx.buffer(np.stack(all_inst_data, 0).tobytes())
					vao = self.ctx.vertex_array(
						self.tex_shader_program,
						[
							(model.vbo_pos, "3f /v", "in_vpos"),
							(model.vbo_normal, "3f /v", "in_vnormal"),
							(vbo_inst, "16f 16f 16f 2f /i", "mmat", "mvp", "tcmat", "in_highlight"),
							(self.vbo_light_pos, "3f /r", "in_light_pos")
						]
					)
					vao.render(moderngl.TRIANGLES, instances = len(one_tex_instances))
					vbo_inst.release()
					vao.release()

screen = pyglet.canvas.get_display().get_default_screen()
config = pyglet.gl.Config(double_buffer = 1, sample_buffers = 1, samples = 4, depth_size = 24)
config = screen.get_best_config(config)
window = PuzzleWindow(width = window_w, height = window_h, config = config)

pyglet.clock.schedule_interval(window.update, 1 / 60)
pyglet.app.run()
