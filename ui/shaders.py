test_vertex_shader_code = '''
#version 330

in vec2 in_vpos;
in vec3 in_vcolor;

out vec3 vcolor;

void main() {
	vcolor = in_vcolor;
	gl_Position = vec4(in_vpos, 0.0, 1.0);
}
'''

test_fragment_shader_code = '''
#version 330

in vec3 vcolor;
out vec3 out_fcolor;

void main() {
	out_fcolor = vcolor;
}
'''

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
