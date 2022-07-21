from .utils import *

class Move:

	def __init__(self, transform, pos_perm):
		self.transform = transform
		self.pos_perm = pos_perm

	def inverse(self):
		return Move(self.transform.inverse(), inverse_perm(self.pos_perm))
