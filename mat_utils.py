import math
import numpy as np

def make_view_mat(cam_pos, look_at, y_vec):
	z_vec = cam_pos - look_at
	z_vec = z_vec / np.linalg.norm(z_vec)
	x_vec = np.cross(y_vec, z_vec)
	x_vec = x_vec / np.linalg.norm(x_vec)
	y_vec = np.cross(z_vec, x_vec)
	view_mat = np.eye(4, dtype = np.float32)
	R = np.stack((x_vec, y_vec, z_vec), 0, out = view_mat[:3, :3])
	np.matmul(R, -cam_pos, out = view_mat[:3, 3])
	return view_mat

def make_proj_mat(fovy, aspect, near, far):
	t = 1 / math.tan(fovy / 2)
	return np.array([
	    [t / aspect, 0, 0, 0],
	    [0, t, 0, 0],
	    [0, 0, (near + far) / (near - far), 2 * near * far / (near - far)],
	    [0, 0, -1, 0]
	], dtype = np.float32)
