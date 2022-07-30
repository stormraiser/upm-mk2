import os
import numpy as np
import trimesh

class Model:

	def __init__(self, path):
		self.path = path
		mesh = trimesh.load(str(path))
		nf = mesh.faces.shape[0]
		self.vpos = np.array(mesh.vertices[mesh.faces.reshape(nf * 3)], dtype = np.float32)
		self.vnormal = np.array(mesh.face_normals.repeat(3, 0), dtype = np.float32)

	def init_gl(self, ctx):
		self.vbo_pos = ctx.buffer(self.vpos.tobytes())
		self.vbo_normal = ctx.buffer(self.vnormal.tobytes())

	def finalize_gl(self):
		self.vbo_pos.release()
		self.vbo_normal.release()

class PuzzleModelMixin:

	def get_model(self, path):
		path = str((self.puzzle_dir / path).resolve())
		if path in self.model_map:
			return self.model_map[path]
		else:
			new_model = Model(path)
			self.model_map[path] = new_model
			return new_model
