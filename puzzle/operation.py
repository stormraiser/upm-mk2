

from .transforms import Transform, TransformSequence
from .move import Move

def get_std_selector_string(selector_string):
	seg = selector_string.split('&')
	if len(seg) > 2:
		raise ValueError("Selector strings may only contain one '&'")
	selector = seg[0]
	modifier = seg[1] if len(seg) == 2 else ''
	seg = selector.split('.')
	if len(seg) > 2:
		raise ValueError("Selector strings may only contain one '.'")
	pos_name = seg[0]
	sel_name = seg[1] if len(seg) == 2 else '0'
	modifier = ''.join([
		'r' if 'r' in modifier else '',
		's' if 's' in modifier else '',
		'c' if 'c' in modifier else '',
		'a' if 'a' in modifier else ''
	])
	return pos_name + '.' + sel_name + '&' + modifier

class Operation:

	def __init__(self, puzzle, name):
		self.puzzle = puzzle
		self.name = name
		self.moves = []
		self.cmd = name

	def add_move(self, move):
		for key in list(move.pos_perm):
			for move0 in self.moves:
				if key in move0.pos_perm:
					del move.pos_perm[key]
					break
		if len(move.pos_perm) > 0:
			self.moves.append(move)

	def set_cmd(self, cmd):
		self.cmd = cmd

	def inverse(self):
		return [move.inverse() for move in self.moves]

class OperationHandle:

	def __init__(self, puzzle, name):
		self.puzzle = puzzle
		self.name = name

	def inverse(self):
		return self.puzzle.get_op(self.name).inverse()

	def add_moves(self, *args):
		if len(args) == 0:
			return self
		if isinstance(args[0], Transform):
			raise NotImplementedError
		moves = []
		for arg in args:
			if isinstance(arg, Move):
				moves.append(arg)
			elif isinstance(arg, list):
				moves.extend(arg)
			elif isinstance(arg, OperationHandle):
				moves.extend(self.puzzle.get_op(arg.name).moves)
		self.puzzle.op_add_move(self.name, moves)
		return self

	def add_selectors(self, *selectors):
		self.puzzle.op_add_selectors(self.name, selectors)
		return self

	def set_cmd(self, cmd):
		self.puzzle.op_set_cmd(self.name, cmd)
		return self

class PuzzleOperationMixin:

	def op(self, name):
		return OperationHandle(self, name)

	def get_op(self, name):
		if name in self.operations:
			return self.operations[name]
		else:
			new_op = Operation(self, name)
			self.operations[name] = new_op
			return new_op

	def add_selector(self, selector, op_name):
		if selector in self.selectors:
			if self.selectors[selector] != op_name:
				raise RuntimeError('Different operations cannot have the same selector')
		self.selectors[selector] = op_name

	def op_add_move(self, op_name, moves):
		arg_lists = self.sym_stack[-1].transform([op_name, moves])
		for arg_list in arg_lists:
			op = self.get_op(arg_list[0])
			for move in arg_list[1]:
				op.add_move(move)

	def op_add_selectors(self, op_name, selectors):
		arg_lists = self.sym_stack[-1].transform([op_name, selectors])
		for arg_list in arg_lists:
			op_name = arg_list[0]
			for selector in arg_list[1]:
				self.add_selector(get_std_selector_string(selector), op_name)

	def op_set_cmd(self, op_name, cmd):
		arg_lists = self.sym_stack[-1].transform([op_name, cmd])
		for arg_list in arg_lists:
			self.get_op(arg_list[0]).set_cmd(arg_list[1])
