import os, math, time, sys
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
	//gl_Position = in_vpos;
	//gl_Position = in_vpos;
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
	out_fcolor = vec3(vcolor) * (t * 250000 + 0.25);
	//out_fcolor = vec3(1, 1, 0);
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

		self.near = 10
		self.far = 500
		self.view_h = math.tan(30 / 180 * math.pi)
		self.aspect = 4 / 3
		self.proj_mat = make_proj_mat(math.atan(self.view_h), self.aspect, self.near, self.far)

		self.ctx = moderngl.create_context()
		self.ctx.enable(moderngl.DEPTH_TEST)
		self.shader_program = self.ctx.program(
			vertex_shader = vertex_shader_code,
			fragment_shader = fragment_shader_code
		)
		self.picker_shader_program = self.ctx.program(
			vertex_shader = picker_vertex_shader_code,
			fragment_shader = picker_fragment_shader_code
		)

		self.puzzle.init_vbo(self.ctx)

		self.light_pos = np.array([200, 400, 300], dtype = np.float32)
		self.vbo_light_pos = self.ctx.buffer(self.light_pos.tobytes())

		self.time0 = time.time()

		self.picker_buffer = self.ctx.simple_framebuffer((window_w, window_h))
		self.mmat_t = np.eye(4, dtype = np.float32)

		self.shift_down = False
		self.ctrl_down = False
		self.alt_down = False

		self.lhighlight = -1
		self.rhighlight = -1
		self.last_mouse_x = 0
		self.last_mouse_y = 0
		self.mouse_move_after_down = False

		self.animating = False
		self.animation_start = 0

	def pixel_to_trackball(self, px, py):
		l = min(window_w, window_h) / 2
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

	def update_active_selector(self, x, y):
		if self.animating:
			return

		self.picker_buffer.use()
		self.ctx.clear(0, 0, 0)
		self.picker_buffer.scissor = (x, y, 1, 1)

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
			modifier = (4 if self.shift_down else 0) + (2 if self.ctrl_down else 0) + (1 if self.alt_down else 0)
			self.lhighlight = self.puzzle.current_click_map[picked_selector, modifier]
			self.rhighlight = self.puzzle.current_click_map[picked_selector, modifier + 8]
		else:
			self.lhighlight = -1
			self.rhighlight = -1

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.last_mouse_x = x
		self.last_mouse_y = y
		self.mouse_move_after_down = True
		if buttons & pyglet.window.mouse.LEFT:
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
		elif buttons & pyglet.window.mouse.RIGHT:
			l = min(window_w, window_h) / 2
			t = (dx * self.view_mat[0, :3] + dy * self.view_mat[1, :3]) / l * 50
			self.mmat_t = core.translation_mat(t) @ self.mmat_t
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

	def on_mouse_release(self, x, y, button, modifiers):
		if self.mouse_move_after_down:
			self.mouse_move_after_down = False
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
						color = np.array(self.puzzle.colors[color], dtype = np.float32)
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

screen = pyglet.canvas.get_display().get_default_screen()
config = pyglet.gl.Config(double_buffer = 1, sample_buffers = 1, samples = 4, depth_size = 24)
config = screen.get_best_config(config)
window = PuzzleWindow(width = window_w, height = window_h, config = config)

pyglet.clock.schedule_interval(window.update, 1 / 60)
pyglet.app.run()
