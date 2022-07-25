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
		self.drag_modifier = None
		self.forbidden_pos = set()

	def add_move(self, move):
		for move0 in self.moves:
			if move.transform == move0.transform:
				for key, value in move.pos_perm.items():
					if key in move0.pos_perm:
						if move0.pos_perm[key] != value:
							raise RuntimeError('Conflicting moves')
					else:
						move0.pos_perm[key] = value
				return
			else:
				for key in move.pos_perm:
					if key in move0.pos_perm:
						raise RuntimeError('Conflicting moves')
		self.moves.append(move)

	def forbid(self, positions):
		self.forbidden_pos.update(positions)

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
		moves = []
		if isinstance(args[0], TransformSequence):
			pos_perm = {}
			for cycle in args[1:]:
				for i in range(len(cycle) - 1):
					pos_perm[cycle[i]] = cycle[i + 1]
				if isinstance(cycle, tuple):
					pos_perm[cycle[-1]] = cycle[0]
			moves.append(Move(args[0], pos_perm))
		else:
			for arg in args:
				if isinstance(arg, Move):
					moves.append(arg)
				elif isinstance(arg, list):
					moves.extend(arg)
				elif isinstance(arg, OperationHandle):
					moves.extend(self.puzzle.get_op(arg.name).moves)
		self.puzzle.op_add_move(self.name, moves)
		return self

	def forbid(self, *positions):
		if isinstance(positions[0], list):
			positions = positions[0]
		self.puzzle.op_forbid(self.name, positions)
		return self

	def click(self, *selectors):
		self.puzzle.op_click(self.name, selectors)
		return self

	def drag(self, modifier = ''):
		self.puzzle.op_set_drag(self.name, modifier)
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

	def add_click(self, selector, op_name):
		if selector in self.selector_map:
			self.selector_map[selector].add(op_name)
		else:
			self.selector_map[selector] = {op_name}

	def set_drag(self, op_name, modifier):
		self.get_op(op_name).drag_modifier = modifier

	def op_add_move(self, op_name, moves):
		arg_lists = self.sym_stack[-1].transform([op_name, moves])
		for arg_list in arg_lists:
			op = self.get_op(arg_list[0])
			for move in arg_list[1]:
				op.add_move(move)

	def op_forbid(self, op_name, positions):
		arg_lists = self.sym_stack[-1].transform([op_name, positions])
		for arg_list in arg_lists:
			self.get_op(arg_list[0]).forbid(arg_list[1])

	def op_click(self, op_name, selectors):
		arg_lists = self.sym_stack[-1].transform([op_name, selectors])
		for arg_list in arg_lists:
			op_name = arg_list[0]
			for selector in arg_list[1]:
				self.add_click(get_std_selector_string(selector), op_name)

	def op_set_drag(self, op_name, modifier):
		modifier = ''.join([
			's' if 's' in modifier else '',
			'c' if 'c' in modifier else '',
			'a' if 'a' in modifier else ''
		])
		arg_lists = self.sym_stack[-1].transform([op_name, modifier])
		for arg_list in arg_lists:
			self.set_drag(arg_list[0], arg_list[1])

	def op_set_cmd(self, op_name, cmd):
		arg_lists = self.sym_stack[-1].transform([op_name, cmd])
		for arg_list in arg_lists:
			self.get_op(arg_list[0]).set_cmd(arg_list[1])
