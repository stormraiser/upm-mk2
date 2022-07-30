import itertools

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
		self.start_pos = name

	def add_part(self, model_path, color, transform, name):
		if name == '':
			name = str(self.unnamed_part_count)
			self.unnamed_part_count += 1
		if name in self.parts:
			raise ValueError('Duplicated part names')
		self.parts[name] = (self.puzzle.get_model(model_path), color, transform.mat)

	def add_selector(self, model_path, name, transform):
		if name == '':
			name = str(self.unnamed_selector_count)
			self.unnamed_selector_count += 1
		if name in self.selectors:
			raise ValueError('Duplicated selector names')
		self.selectors[name] = (self.puzzle.get_model(model_path), transform.mat)

	def start_from(self, pos_name):
		self.start_pos = pos_name

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

	def start_from(self, pos_name):
		self.puzzle.block_start_from(self.name, pos_name)
		return self

	def touch(self):
		self.puzzle.touch_block(self.name)
		return self

	def remove(self):
		self.puzzle.remove_block(self.name)
		return self

	def exists(self):
		return self.name in self.puzzle.block_map

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

	def merge_classes(self, block_names):
		self.class_mergers.append(block_names)

	def block(self, name):
		return BlockHandle(self, name)

	def get_block(self, name):
		if name in self.block_map:
			return self.block_map[name]
		else:
			new_block = Block(self, name)
			self.block_map[name] = new_block
			return new_block

	def block_add_part(self, block_name, model_path, color, transform, name):
		arg_lists = self.sym_stack[-1].transform([block_name, model_path, color, transform, name])
		self.merge_classes([t[0] for t in arg_lists])
		arg_lists = remove_duplicate(arg_lists)
		for arg_list in arg_lists:
			self.get_block(arg_list[0]).add_part(*arg_list[1:])

	def block_add_selector(self, block_name, model_path, name, transform):
		arg_lists = self.sym_stack[-1].transform([block_name, model_path, name, transform])
		self.merge_classes([t[0] for t in arg_lists])
		arg_lists = remove_duplicate(arg_lists)
		for arg_list in arg_lists:
			self.get_block(arg_list[0]).add_selector(*arg_list[1:])

	def block_start_from(self, block_name, pos_name):
		arg_lists = self.sym_stack[-1].transform([block_name, pos_name])
		self.merge_classes([t[0] for t in arg_lists])
		check_dict = {}
		for block_name, pos_name in arg_lists:
			if block_name in check_dict:
				if check_dict[block_name] != pos_name:
					raise ValueError('Conflicting starting positions')
			else:
				check_dict[block_name] = pos_name
		for block_name, pos_name in check_dict.items():
			self.get_block(block_name).start_from(pos_name)

	def link_block(self, *block_names):
		self.sym_link_block(block_names)
		return MergedBlockHandle(self, block_names)

	def link_pos(self, *pos_names):
		self.sym_link_pos(pos_names)

	def sym_link_block(self, block_names):
		all_links = self.sym_stack[-1].transform(block_names)
		self.merge_classes(itertools.chain(*all_links))
		for one_link in all_links:
			for block_name in one_link:
				self.get_block(block_name)
			for i in range(len(one_link) - 1):
				if one_link[i] in self.blink_map:
					if self.blink_map[one_link[i]] != one_link[i + 1]:
						raise ValueError('Conflicting block links')
				else:
					self.blink_map[one_link[i]] = one_link[i + 1]
				if one_link[i + 1] in self.blink_invmap:
					if self.blink_invmap[one_link[i + 1]] != one_link[i]:
						raise ValueError('Conflicting block links')
				else:
					self.blink_invmap[one_link[i + 1]] = one_link[i]

	def sym_link_pos(self, pos_names):
		all_links = self.sym_stack[-1].transform(pos_names)
		for one_link in all_links:
			for i in range(len(one_link) - 1):
				if one_link[i] in self.plink_map:
					if self.plink_map[one_link[i]] != one_link[i + 1]:
						raise ValueError('Conflicting position links')
				else:
					self.plink_map[one_link[i]] = one_link[i + 1]
				if one_link[i + 1] in self.plink_invmap:
					if self.plink_invmap[one_link[i + 1]] != one_link[i]:
						raise ValueError('Conflicting position links')
				else:
					self.plink_invmap[one_link[i + 1]] = one_link[i]

	def block_merger_add_part(self, block_names, model_path, color, transform, name):
		arg_lists = self.sym_stack[-1].transform([block_names, model_path, color, transform, name])
		merged_arg_lists = merge_name_sets(arg_lists)
		for arg_list in merged_arg_lists:
			self.get_block(min(arg_list[0])).add_part(*arg_list[1:])

	def touch_block(self, block_name):
		block_names = self.sym_stack[-1].transform(block_name)
		self.merge_classes(block_names)
		for block_name in block_names:
			self.get_block(block_name)

	def remove_block(self, block_name):
		all_removals = set()
		open_set = {block_name}
		while len(open_set) > 0:
			block_name = open_set.pop()
			all_removals.add(block_name)
			if block_name in self.blink_map:
				next_block_name = self.blink_map[block_name]
				if not next_block_name in all_removals:
					open_set.add(next_block_name)
			if block_name in self.blink_invmap:
				next_block_name = self.blink_invmap[block_name]
				if not next_block_name in all_removals:
					open_set.add(next_block_name)
			sym_names = self.sym_stack[-1].transform(block_name)
			for sym_name in sym_names:
				if not sym_name in all_removals:
					open_set.add(sym_name)
		
		for block_name in all_removals:
			if block_name in self.block_map:
				del self.block_map[block_name]
			if block_name in self.blink_map:
				del self.blink_map[block_name]
			if block_name in self.blink_invmap:
				del self.blink_invmap[block_name]

	def block_setattr(self, block_name, attr_name, value):
		arg_lists = self.sym_stack[-1].transform([block_name, attr_name, value])
		self.merge_classes([t[0] for t in arg_lists])
		for arg_list in arg_lists:
			setattr(self.get_block(block_name), attr_name, value)
