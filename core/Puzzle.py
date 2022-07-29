import importlib, sys, pathlib

from .transforms import Transform, TransformSet, PuzzleTransformMixin
from .block import PuzzleBlockMixin
from .model import PuzzleModelMixin
from .operation import PuzzleOperationMixin
from .postprocess import PuzzlePostprocessMixin
from .runtime import PuzzleRuntimeMixin
from .texture import PuzzleTextureMixin

export_names = [
	'translate',
	'rotate',
	'tag_cycle',
	'group',
	'block',
	'merge',
	'color',
	'op',
	'texture',
	'input_buttons'
]

class SourceFileLoaderWithExtraGlobals(importlib.machinery.SourceFileLoader):

	def __init__(self, fullname, path):
		super().__init__(fullname, path)

	def exec_module(self, module):
		module.__dict__.update(Puzzle.extra_globals)
		super().exec_module(module)

class Puzzle(
	PuzzleTransformMixin,
	PuzzleBlockMixin,
	PuzzleModelMixin,
	PuzzleOperationMixin,
	PuzzlePostprocessMixin,
	PuzzleRuntimeMixin,
	PuzzleTextureMixin
):

	current_active_puzzle = None

	def __init__(self, window, puzzle_path, lib_dir):
		#print(self)
		self.window = window
		self.tags = set()
		self.sym_stack = [TransformSet(self, [Transform()])]
		self.models = {}
		self.textures = {}
		self.blocks = {}
		self.operations = {}
		self.selector_map = {}
		self.block_merge_sets = []
		self.pos_colocate_sets = []
		self.clr_tex_map = {}
		self.puzzle_dir = puzzle_path.parent

		modifiers = ['']
		for s in ['a', 'c', 's', 'r']:
			modifiers = modifiers + [s + t for t in modifiers]
		self.modifier_to_id = {name: k for k, name in enumerate(modifiers)}
		self.modifiers = modifiers

		self.load_puzzle(puzzle_path, lib_dir)
		self.postprocess()
		self.reset()

	def color(self, name, r, g, b, specular = 0):
		self.clr_tex_map[name] = (False, r, g, b, specular)

	def load_puzzle(self, puzzle_path, lib_dir):
		Puzzle.current_active_puzzle = self

		export_dict = {}
		for name in export_names:
			export_dict[name] = getattr(self, name)
		Puzzle.current_extra_globals = export_dict

		def make_loader(fullname, path):
			return SourceFileLoaderWithExtraGlobals(fullname, path)
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

	def input_buttons(self, *labels):
		return self.window.get_input_buttons(labels[0], labels[1:])

	@staticmethod
	def _translate(*args):
		return Puzzle.current_active_puzzle.translate(*args)

	@staticmethod
	def _rotate(*args):
		return Puzzle.current_active_puzzle.rotate(*args)

	@staticmethod
	def _tag_cycle(*args):
		return Puzzle.current_active_puzzle.tag_cycle(*args)

	@staticmethod
	def _group(*args):
		return Puzzle.current_active_puzzle.group(*args)

	@staticmethod
	def _block(*args):
		return Puzzle.current_active_puzzle.block(*args)

	@staticmethod
	def _merge(*args):
		return Puzzle.current_active_puzzle.merge(*args)

	@staticmethod
	def _color(*args):
		Puzzle.current_active_puzzle.color(*args)

	@staticmethod
	def _op(*args):
		return Puzzle.current_active_puzzle.op(*args)

	@staticmethod
	def _texture(*args):
		Puzzle.current_active_puzzle.texture(*args)

	@staticmethod
	def _input_buttons(*args):
		return Puzzle.current_active_puzzle.input_buttons(*args)

Puzzle.extra_globals = {
	'translate': Puzzle._translate,
	'rotate': Puzzle._rotate,
	'tag_cycle': Puzzle._tag_cycle,
	'group': Puzzle._group,
	'block': Puzzle._block,
	'merge': Puzzle._merge,
	'color': Puzzle._color,
	'op': Puzzle._op,
	'texture': Puzzle._texture,
	'input_buttons': Puzzle._input_buttons
}