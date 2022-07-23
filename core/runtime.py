import numpy as np

class PuzzleRuntimeMixin:

	def reset(self):
		self.state = list(self.start_state)
		self.animation_op = -1
		for block in self.block_list:
			block.position = block.start_position
			block.current_transform = np.eye(4, dtype = np.float32)
			block.next_transform = np.eye(4, dtype = np.float32)
			block.highlight = False
		self.update_click_map()

	def check_op_validity(self):
		for op in self.op_list:
			op.valid = True

	def update_click_map(self):
		self.check_op_validity()
		self.current_click_map.fill(-1)
		for op_id, op in enumerate(self.op_list):
			if op.valid:
				for pos_id, sel_id, mod_id in op.click_list:
					total_selector_id = self.block_list[self.state[pos_id]].selector_list[sel_id][2]
					if self.current_click_map[total_selector_id, mod_id] >= 0:
						raise RuntimeError('Multiple operations with the same selector active simultaneously')
					self.current_click_map[total_selector_id, mod_id] = op_id

	def init_vbo(self, ctx):
		for model in self.model_list:
			model.vbo_pos = ctx.buffer(model.vpos.tobytes())
			model.vbo_normal = ctx.buffer(model.vnormal.tobytes())

	def start_op(self, op_id):
		self.current_op = self.op_list[op_id]

	def animate(self, t):
		for move in self.current_op.moves:
			mat = move.transform.mat_t(t)
			for pos_id, _ in move.pos_perm:
				block = self.block_list[self.state[pos_id]]
				block.next_transform = mat @ block.current_transform

	def finish_op(self):
		new_state = []
		for move in self.current_op.moves:
			mat = move.transform.mat_t(1)
			for pos_id, target in move.pos_perm:
				block_id = self.state[pos_id]
				block = self.block_list[block_id]
				block.position = target
				block.next_transform = mat @ block.current_transform
				block.current_transform = block.next_transform
				new_state.append((target, block_id))
			for pos_id, block_id in new_state:
				self.state[pos_id] = block_id
		self.update_click_map()

	def set_highlight(self, op_ids):
		for block in self.block_list:
			block.highlight = False
		for op_id in op_ids:
			op = self.op_list[op_id]
			for move in op.moves:
				for pos_id, _ in move.pos_perm:
					self.block_list[self.state[pos_id]].highlight = True
