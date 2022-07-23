import importlib, sys, pathlib

from .transforms import Transform, TransformSet, PuzzleTransformMixin
from .block import PuzzleBlockMixin
from .model import PuzzleModelMixin
from .operation import PuzzleOperationMixin
from .postprocess import PuzzlePostprocessMixin
from .runtime import PuzzleRuntimeMixin

export_names = [
	'translate',
	'rotate',
	'tag_cycle',
	'group',
	'block',
	'merge',
	'color',
	'op'
]

class SourceFileLoaderWithExtraGlobals(importlib.machinery.SourceFileLoader):

	def __init__(self, fullname, path, extra_globals):
		super().__init__(fullname, path)
		self.extra_globals = extra_globals

	def exec_module(self, module):
		module.__dict__.update(self.extra_globals)
		super().exec_module(module)

class Puzzle(
	PuzzleTransformMixin,
	PuzzleBlockMixin,
	PuzzleModelMixin,
	PuzzleOperationMixin,
	PuzzlePostprocessMixin,
	PuzzleRuntimeMixin
):

	def __init__(self, puzzle_path, lib_dir):
		self.tags = set()
		self.sym_stack = [TransformSet(self, [Transform()])]
		self.models = {}
		self.blocks = {}
		self.operations = {}
		self.selector_map = {}
		self.block_merge_sets = []
		self.pos_colocate_sets = []
		self.colors = {}
		self.puzzle_dir = puzzle_path.parent
		self.drag_ops = {}

		modifiers = ['']
		for s in ['a', 'c', 's', 'r']:
			modifiers = modifiers + [s + t for t in modifiers]
		for modifier in modifiers[:8]:
			self.drag_ops[modifier] = []
		self.modifier_to_id = {name: k for k, name in enumerate(modifiers)}

		self.load_puzzle(puzzle_path, lib_dir)
		self.postprocess()
		self.reset()

	def color(self, name, r, g, b, specular = 0):
		self.colors[name] = (r, g, b, specular)

	def load_puzzle(self, puzzle_path, lib_dir):
		export_dict = {}
		for name in export_names:
			export_dict[name] = getattr(self, name)

		def make_loader(fullname, path):
			return SourceFileLoaderWithExtraGlobals(fullname, path, export_dict)
		def puzzle_path_hook(path):
			path_t = pathlib.Path(path).resolve()
			if path_t.is_relative_to(lib_dir) or path_t.is_relative_to(puzzle_path.parent):
				return importlib.machinery.FileFinder(path, (make_loader, importlib.machinery.SOURCE_SUFFIXES))
			else:
				raise ImportError
		sys.path_hooks.insert(0, puzzle_path_hook)

		with open(puzzle_path) as code_file:
			pcode = code_file.read()
		exec(pcode, export_dict)

		sys.path_hooks.remove(puzzle_path_hook)
