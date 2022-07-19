import os
import numpy as np
import trimesh

class Model:

	def __init__(self, model_path):
		mesh = trimesh.load(model_path)
		nf = mesh.faces.shape[0]
		self.vpos = np.array(mesh.vertices[mesh.faces.reshape(nf * 3)], dtype = np.float32)
		self.vnormal = np.array(mesh.face_normals.repeat(3, 0), dtype = np.float32)

class PuzzleModelMixin:

	def get_model(self, path):
		path = os.path.join(self.root, path)
		if path in self.models:
			return self.models[path]
		else:
			new_model = Model(path)
			self.models[path] = new_model
			return new_model
