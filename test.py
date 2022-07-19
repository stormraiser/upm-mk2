import os, math, time

import numpy as np
import pyglet
import moderngl

from mat_utils import *
import puzzle

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
base_dir = os.path.dirname(__file__)

class PuzzleWindow(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.puzzle = puzzle.Puzzle(os.path.join(base_dir, 'cube_3'))
        export_dict = {}
        for name in puzzle.export_names:
            export_dict[name] = getattr(self.puzzle, name)

        with open(os.path.join(base_dir, 'cube_3.py')) as code_file:
            pcode = code_file.read()
        exec(pcode, export_dict)

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

        self.light_pos = np.array([200, 400, 300], dtype = np.float32)
        self.vbo_light_pos = self.ctx.buffer(self.light_pos.tobytes())

        for model_name, model in self.puzzle.models.items():
            model.vbo_pos = self.ctx.buffer(model.vpos.tobytes())
            model.vbo_normal = self.ctx.buffer(model.vnormal.tobytes())
            model.instance_info = []
        self.puzzle.selector_list = sorted(list(self.puzzle.selectors.items()))
        self.puzzle.current_state = {}
        for block_name, block in self.puzzle.blocks.items():
            self.puzzle.current_state[block.start_position] = block_name
            block.current_transform = np.eye(4, dtype = np.float32)
            block.next_transform = np.eye(4, dtype = np.float32)

        self.time0 = time.time()

        self.picker_buffer = self.ctx.simple_framebuffer((window_w, window_h))
        self.mmat_t = np.eye(4, dtype = np.float32)

        self.shift_down = False
        self.ctrl_down = False
        self.alt_down = False

        self.lhighlight = None
        self.rhighlight = None
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_move_after_down = False

        self.animating = False
        self.animation_op = None
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
                self.update_state()
                self.update_active_selector(self.last_mouse_x, self.last_mouse_y)
            else:
                self.update_state(t = (current_time - self.animation_start) / animation_time)

    def update_active_selector(self, x, y):
        if self.animating:
            return
        active_selectors = {}
        active_possel = set()
        for selector, op_name in self.puzzle.selector_list:
            pos_and_sel, modifier = selector.split('&')
            pos_name, sel_name = pos_and_sel.split('.')
            if (('s' in modifier) == self.shift_down) and (('c' in modifier) == self.ctrl_down) and (('a' in modifier) == self.alt_down):
                block = self.puzzle.get_block(self.puzzle.current_state[pos_name])
                model, mat = block.selectors[sel_name]
                mat = block.current_transform @ mat
                active_selectors[(pos_and_sel, 'r' in modifier)] = (model, mat, op_name)
                active_possel.add(pos_and_sel)
        merged_selectors = []
        for possel in active_possel:
            if (possel, True) in active_selectors:
                model, mat, rop_name = active_selectors[(possel, True)]
                if (possel, False) in active_selectors:
                    lop_name = active_selectors[(possel, False)][2]
                else:
                    lop_name = None
                merged_selectors.append((model, mat, lop_name, rop_name))
            else:
                if (possel, False) in active_selectors:
                    model, mat, lop_name = active_selectors[(possel, False)]
                    merged_selectors.append((model, mat, lop_name, None))
        #
        n = len(merged_selectors)
        m = math.ceil((n + 2) ** (1 / 3))
        for model_name, model in self.puzzle.models.items():
            model.instance_info = []
        for k in range(n):
            r = ((k + 1) // m // m + 0.5) / m
            g = ((k + 1) // m % m + 0.5) / m
            b = ((k + 1) % m + 0.5) / m
            color = np.array([r, g, b], dtype = np.float32)
            merged_selectors[k][0].instance_info.append((color, merged_selectors[k][1]))

        self.picker_buffer.use()
        self.ctx.clear(0, 0, 0)
        self.picker_buffer.scissor = (x, y, 1, 1)

        for model_name, model in self.puzzle.models.items():
            if len(model.instance_info) > 0:
                all_inst_data = []
                for inst in model.instance_info:
                    mvp = self.proj_mat @ self.view_mat @ self.mmat_t @ inst[1]
                    inst_data = np.concatenate((inst[0], mvp.transpose().reshape(16)), 0)
                    all_inst_data.append(inst_data)
                vbo_inst = self.ctx.buffer(np.stack(all_inst_data, 0).tobytes())
                vao = self.ctx.vertex_array(
                    self.picker_shader_program,
                    [
                        (model.vbo_pos, "3f /v", "in_vpos"),
                        (vbo_inst, "3f 16f /i", "in_vcolor", "mvp")
                    ]
                )
                vao.render(moderngl.TRIANGLES, instances = len(model.instance_info))
                vbo_inst.release()
                vao.release()

        r, g, b = self.picker_buffer.read(viewport = (x, y, 1, 1))
        r = math.floor(r / 255 * m)
        g = math.floor(g / 255 * m)
        b = math.floor(b / 255 * m)
        k = r * m * m + g * m + b
        if k == 0 or k >= n + 1:
            k = -1
        else:
            k -= 1

        if k >= 0:
            self.lhighlight = merged_selectors[k][2]
            self.rhighlight = merged_selectors[k][3]
        else:
            self.lhighlight = None
            self.rhighlight = None
        #print(self.lhighlight or '*', self.rhighlight or '*')

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
            self.mmat_t = puzzle.rotation_mat(n, angle) @ self.mmat_t
        elif buttons & pyglet.window.mouse.RIGHT:
            l = min(window_w, window_h) / 2
            t = (dx * self.view_mat[0, :3] + dy * self.view_mat[1, :3]) / l * 50
            self.mmat_t = puzzle.translation_mat(t) @ self.mmat_t
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
            op = self.lhighlight
        elif button & pyglet.window.mouse.RIGHT:
            op = self.rhighlight
        if op is None:
            return
        self.animation_op = op
        self.animating = True
        self.animation_start = time.time()

    def update_state(self, t = 1):
        op = self.puzzle.get_op(self.animation_op)
        new_state = {}
        for move in op.moves:
            mat = move.transform.mat_t(t)
            for pos, new_pos in move.pos_perm.items():
                block_name = self.puzzle.current_state[pos]
                block = self.puzzle.get_block(block_name)
                block.next_transform = mat @ block.current_transform
                if not self.animating:
                    block.current_transform = block.next_transform
                    new_state[new_pos] = block_name
        if not self.animating:
            self.puzzle.current_state.update(new_state)

    def on_draw(self):
        self.ctx.screen.use()
        self.ctx.clear(0.7, 0.7, 0.7)

        for block_name, block in self.puzzle.blocks.items():
            block.highlight = False
        ops = []
        if self.lhighlight is not None:
            ops.append(self.puzzle.get_op(self.lhighlight))
        if self.rhighlight is not None:
            ops.append(self.puzzle.get_op(self.rhighlight))
        for op in ops:
            for move in op.moves:
                for pos in move.pos_perm:
                    self.puzzle.get_block(self.puzzle.current_state[pos]).highlight = True

        for model_name, model in self.puzzle.models.items():
            model.instance_info = []

        for block_name, block in self.puzzle.blocks.items():
            for part_name, part_info in block.parts.items():
                model, color, model_mat = part_info
                model_mat = self.mmat_t @ block.next_transform @ model_mat
                color = np.array(self.puzzle.colors[color], dtype = np.float32)
                if block.highlight:
                    #color = color * 0.7 + 0.3
                    color = color * 0.85 + 0.25
                mvp = self.proj_mat @ self.view_mat @ model_mat
                model.instance_info.append((color, model_mat, mvp))

        for model_name, model in self.puzzle.models.items():
            if len(model.instance_info) > 0:
                all_inst_data = []
                for inst in model.instance_info:
                    inst_data = np.concatenate((inst[0], inst[1].transpose().reshape(16), inst[2].transpose().reshape(16)), 0)
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
                vao.render(moderngl.TRIANGLES, instances = len(model.instance_info))
                vbo_inst.release()
                vao.release()

screen = pyglet.canvas.get_display().get_default_screen()
config = pyglet.gl.Config(double_buffer = 1, sample_buffers = 1, samples = 2, depth_size = 24)
config = screen.get_best_config(config)
window = PuzzleWindow(width = window_w, height = window_h, config = config)

pyglet.clock.schedule_interval(window.update, 1 / 15)
pyglet.app.run()
