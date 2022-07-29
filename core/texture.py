from PIL import Image
import numpy as np
from PySide6 import QtOpenGL, QtGui

class Texture:

	def __init__(self, path):
		self.image = QtGui.QImage(str(path))

	def init_gl(self, ctx):
		self.gl_tex = QtOpenGL.QOpenGLTexture(self.image)
		self.gl_tex.setMinificationFilter(QtOpenGL.QOpenGLTexture.LinearMipMapLinear)
		self.gl_tex.setMagnificationFilter(QtOpenGL.QOpenGLTexture.Linear)

	def finalize_gl(self):
		self.gl_tex.release()
		self.gl_tex.destroy()

class PuzzleTextureMixin:

	def load_texture(self, path):
		path = str((self.puzzle_dir / path).resolve())
		if not path in self.textures:
			new_texture = Texture(path)
			self.textures[path] = new_texture
		return path

	def texture(self, name, path, ux, uy, uz, vx, vy, vz, uoffset, voffset):
		path = self.load_texture(path)
		uv_mat = np.array([
			[ux, uy, uz, uoffset],
			[vx, vy, vz, voffset],
			[0, 0, 0, 0],
			[0, 0, 0, 0]
		], dtype = np.float32)
		self.clr_tex_map[name] = (True, path, uv_mat)
