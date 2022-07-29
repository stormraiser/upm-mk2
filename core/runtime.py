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
			for pos_id in op.forbidden_pos:
				if self.state[pos_id] >= 0:
					op.valid = False
					break
			else:
				op.valid = True

	def update_click_map(self):
		self.check_op_validity()
		self.current_click_map.fill(-1)
		for op_id, op in enumerate(self.op_list):
			if op.valid:
				for pos_id, sel_id, mod_id in op.click_list:
					selector_info = self.block_list[self.state[pos_id]].selector_list[sel_id]
					if selector_info is not None:
						total_selector_id = selector_info[2]
						if self.current_click_map[total_selector_id, mod_id] >= 0:
							raise RuntimeError('Multiple operations with the same selector active simultaneously')
						self.current_click_map[total_selector_id, mod_id] = op_id

	def init_gl(self, ctx):
		for model in self.model_list:
			model.init_gl(ctx)
		for texture in self.texture_list:
			texture.init_gl(ctx)

	def finalize_gl(self):
		for model in self.model_list:
			model.finalize_gl()
		for texture in self.texture_list:
			texture.finalize_gl()

	def start_op(self, op_id):
		self.current_op = self.op_list[op_id]

	def animate(self, t):
		for move in self.current_op.moves:
			mat = move.transform.mat_t(t)
			for pos_id, _ in move.pos_perm:
				block_id = self.state[pos_id]
				if block_id >= 0:
					block = self.block_list[block_id]
					block.next_transform = mat @ block.current_transform

	def finish_op(self):
		new_state = []
		for move in self.current_op.moves:
			mat = move.transform.mat_t(1)
			for pos_id, target in move.pos_perm:
				block_id = self.state[pos_id]
				if block_id >= 0:
					block = self.block_list[block_id]
					block.position = target
					block.next_transform = mat @ block.current_transform
					block.current_transform = block.next_transform
				self.state[pos_id] = -1
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
					block_id = self.state[pos_id]
					if block_id >= 0:
						self.block_list[block_id].highlight = True

	def get_drag_matching_path(self, block_id, drag_point, mod_id, num_segments = 20):
		pos_id = self.block_list[block_id].position
		valid_ops = []
		for op_id, move_id in self.op_by_pos[pos_id]:
			if self.op_list[op_id].valid and self.op_list[op_id].drag_modifier == mod_id:
				valid_ops.append((op_id, move_id))
		output_paths = []
		for op_id, move_id in valid_ops:
			transform = self.op_list[op_id].moves[move_id].transform
			path = np.stack([transform.mat_t(t) @ drag_point for t in np.linspace(0, 1, num_segments + 1)], 0)
			output_paths.append((op_id, path))
		return output_paths
