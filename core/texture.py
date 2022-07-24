from PIL import Image
import numpy as np

class Texture:

	def __init__(self, path):
		self.image = Image.open(str(path)).convert('RGB')

	def init_gl(self, ctx):
		self.gl_tex = ctx.texture(
			(self.image.width, self.image.height),
			3, self.image.tobytes()
		)
		self.gl_tex.build_mipmaps()

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
