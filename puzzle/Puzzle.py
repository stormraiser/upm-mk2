from .transforms import Transform, TransformSet, PuzzleTransformMixin
from .block import PuzzleBlockMixin
from .model import PuzzleModelMixin
from .operation import PuzzleOperationMixin

class Puzzle(
	PuzzleTransformMixin,
	PuzzleBlockMixin,
	PuzzleModelMixin,
	PuzzleOperationMixin
):

	def __init__(self, root):
		self.tags = set()
		self.sym_stack = [TransformSet(self, [Transform()])]
		self.models = {}
		self.blocks = {}
		self.operations = {}
		self.selectors = {}
		self.block_merge_sets = []
		self.pos_colocate_sets = []
		self.root = root
		self.colors = {}

	def color(self, name, r, g, b, specular = 0):
		self.colors[name] = (r, g, b, specular)
