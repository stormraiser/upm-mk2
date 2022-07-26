from .transforms import Transform
from .utils import *

class Block:

	def __init__(self, puzzle, name):
		self.puzzle = puzzle
		self.name = name
		self.parts = {}
		self.unnamed_part_count = 0
		self.selectors = {}
		self.unnamed_selector_count = 0
		self.start_position = name

	def add_part(self, model_path, color, transform, name):
		if name == '':
			name = str(self.unnamed_part_count)
			self.unnamed_part_count += 1
		if name in self.parts:
			raise RuntimeError('Duplicated part names')
		self.parts[name] = (self.puzzle.get_model(model_path), color, transform.mat)

	def add_selector(self, model_path, name, transform):
		if name == '':
			name = str(self.unnamed_selector_count)
			self.unnamed_selector_count += 1
		if name in self.selectors:
			raise RuntimeError('Duplicated selector names')
		self.selectors[name] = (self.puzzle.get_model(model_path), transform.mat)

	def start_from(self, position_name):
		self.start_position = position_name

class BlockHandle:

	def __init__(self, puzzle, name):
		self.puzzle = puzzle
		self.name = name

	def add_part(self, model_path, color, transform = None, name = ''):
		transform = Transform() if transform is None else transform.transforms[0]
		self.puzzle.block_add_part(self.name, model_path, color, transform, name)
		return self

	def add_parts(self, *arg_lists):
		for arg_list in arg_lists:
			self.add_part(*arg_list)
		return self

	def add_selector(self, model_path, name = '', transform = None):
		transform = Transform() if transform is None else transform.transforms[0]
		self.puzzle.block_add_selector(self.name, model_path, name, transform)
		return self

	def add_selectors(self, *arg_lists):
		for arg_list in arg_lists:
			if isinstance(arg_list, str):
				self.add_selector(arg_list)
			else:
				self.add_selector(*arg_list)
		return self

	def start_from(self, position_name):
		self.puzzle.block_start_from(self.name, position_name)
		return self

	def remove(self):
		self.puzzle.block_remove(self.name)
		return self

	def exists(self):
		return self.name in self.puzzle.blocks

	def setattr(self, attr_name, value):
		self.puzzle.block_set_attr(self.name, attr_name, value)

	def getattr(self, attr_name):
		return getattr(self.puzzle.get_block(self.name), attr_name)

class MergedBlockHandle:

	def __init__(self, puzzle, names):
		self.puzzle = puzzle
		self.names = names

	def add_part(self, model_path, color, transform = None, name = ''):
		transform = Transform() if transform is None else transform.transforms[0]
		self.puzzle.block_merger_add_part(self.names, model_path, color, transform, name)
		return self

	def add_parts(self, *arg_lists):
		for arg_list in arg_lists:
			self.add_part(*arg_list)

class PuzzleBlockMixin:

	def block(self, name):
		return BlockHandle(self, name)

	def get_block(self, name):
		if name in self.blocks:
			return self.blocks[name]
		else:
			new_block = Block(self, name)
			self.blocks[name] = new_block
			return new_block

	def block_add_part(self, block_name, model_path, color, transform, name):
		arg_lists = self.sym_stack[-1].transform([block_name, model_path, color, transform, name])
		arg_lists = remove_duplicate(arg_lists)
		for arg_list in arg_lists:
			self.get_block(arg_list[0]).add_part(*arg_list[1:])

	def block_add_selector(self, block_name, model_path, name, transform):
		arg_lists = self.sym_stack[-1].transform([block_name, model_path, name, transform])
		arg_lists = remove_duplicate(arg_lists)
		for arg_list in arg_lists:
			self.get_block(arg_list[0]).add_selector(*arg_list[1:])

	def block_start_from(self, block_name, position_name):
		arg_lists = self.sym_stack[-1].transform([block_name, position_name])
		arg_lists = remove_duplicate(arg_lists)
		for arg_list in arg_lists:
			self.get_block(arg_list[0]).start_from(arg_list[1])

	def merge(self, *block_names):
		self.merge_blocks(block_names)
		return MergedBlockHandle(self, block_names)

	def merge_blocks(self, block_names):
		all_block_names = self.sym_stack[-1].transform([block_names])
		all_pos_names = [[[self.get_block(name).start_position for name in t[0]]] for t in all_block_names]
		self.block_merge_sets = merge_name_sets(self.block_merge_sets + all_block_names)
		self.pos_colocate_sets = merge_name_sets(self.pos_colocate_sets + all_pos_names)

	def block_merger_add_part(self, block_names, model_path, color, transform, name):
		arg_lists = self.sym_stack[-1].transform([block_names, model_path, color, transform, name])
		merged_arg_lists = merge_name_sets(arg_lists)
		for arg_list in merged_arg_lists:
			self.get_block(min(arg_list[0])).add_part(*arg_list[1:])

	def block_remove(self, block_name):
		# fix this later: sym and merge should propagate
		for mset in self.block_merge_sets:
			if block_name in mset[0]:
				block_names = mset[0]
				break
		else:
			block_names = [block_name]
		
		arg_lists = self.sym_stack[-1].transform(block_names)
		for arg_list in arg_lists:
			for name in arg_list:
				if name in self.blocks:
					del self.blocks[name]

	def block_setattr(self, block_name, attr_name, value):
		arg_lists = self.sym_stack[-1].transform([block_name, attr_name, value])
		for arg_list in arg_lists:
			setattr(self.get_block(block_name), attr_name, value)
