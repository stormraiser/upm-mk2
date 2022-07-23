import math

import numpy as np

class PuzzlePostprocessMixin:

	def pick_color_to_instance_id(self, r, g, b, selector = False):
		m = self.pick_color_steps
		r = r * m // 255
		g = g * m // 255
		b = b * m // 255
		k = r * m * m + g * m + b
		if selector:
			k = k - self.total_parts - 1
			if k < 0 or k >= self.total_selectors:
				return -1
			else:
				return k
		else:
			if k == 0 or k >= self.total_parts + 1:
				return -1
			else:
				return k - 1

	def postprocess(self):
		model_list = sorted(self.models.items())
		self.model_list = [t[1] for t in model_list]
		self.model_path_to_id = {model_list[k][0]: k for k in range(len(model_list))}
		del self.models

		block_list = sorted(self.blocks.items())
		self.block_list = [t[1] for t in block_list]
		self.block_name_to_id = {block_list[k][0]: k for k in range(len(block_list))}
		del self.blocks

		op_list = sorted(self.operations.items())
		self.op_list = [t[1] for t in op_list]
		self.op_name_to_id = {op_list[k][0]: k for k in range(len(op_list))}
		del self.operations

		pos_set = set()
		for block in self.block_list:
			pos_set.add(block.start_position)
		for op in self.op_list:
			for move in op.moves:
				pos_set.update(move.pos_perm.keys())
		self.pos_list = sorted(pos_set)
		self.pos_name_to_id = {pos: k for k, pos in enumerate(self.pos_list)}

		self.total_parts = 0
		self.total_selectors = 0
		self.start_state = [-1] * len(self.pos_list)
		all_part_names = set()
		all_selector_names = set()
		for k, block in enumerate(self.block_list):
			self.total_parts += len(block.parts)
			self.total_selectors += len(block.selectors)
			t = self.pos_name_to_id[block.start_position]
			self.start_state[t] = k
			block.start_position = t
			all_part_names.update(block.parts.keys())
			all_selector_names.update(block.selectors.keys())
		self.all_part_names = sorted(all_part_names)
		self.all_selector_names = sorted(all_selector_names)
		self.part_name_to_id = {name: k for k, name in enumerate(self.all_part_names)}
		self.selector_name_to_id = {name: k for k, name in enumerate(self.all_selector_names)}
		self.num_part_names = len(self.all_part_names)
		self.num_selector_names = len(self.all_selector_names)

		self.total_instances = self.total_parts + self.total_selectors
		m = math.ceil((self.total_instances + 2) ** (1 / 3))
		self.pick_color_steps = m
		def instance_id_to_pick_color(p):
			m = self.pick_color_steps
			r = ((p + 1) // m // m + 0.5) / m
			g = ((p + 1) // m % m + 0.5) / m
			b = ((p + 1) % m + 0.5) / m
			return r, g, b

		total_part_id = 0
		total_selector_id = 0
		for model in self.model_list:
			model.part_instances = []
			model.selector_instances = []
		self.part_id_to_block_id = []

		for i, block in enumerate(self.block_list):
			block.part_list = [None] * self.num_part_names
			for part_name, (model, color, mat) in block.parts.items():
				model_id = self.model_path_to_id[model.path]
				k = self.part_name_to_id[part_name]
				block.part_list[k] = (model_id, color, mat, instance_id_to_pick_color(total_part_id))
				total_part_id += 1
				self.model_list[model_id].part_instances.append((i, k))
				self.part_id_to_block_id.append(i)
			del block.parts

			block.selector_list = [None] * self.num_selector_names
			for selector_name, (model, mat) in block.selectors.items():
				model_id = self.model_path_to_id[model.path]
				k = self.selector_name_to_id[selector_name]
				block.selector_list[k] = (model_id, mat, total_selector_id, instance_id_to_pick_color(total_selector_id + self.total_parts))
				#print(total_selector_id, instance_id_to_pick_color(self.total_parts + total_selector_id))
				total_selector_id += 1
				self.model_list[model_id].selector_instances.append((i, k))
			del block.selectors

		self.op_by_pos = [[] for k in range(len(self.pos_list))]
		for k, op in enumerate(self.op_list):
			op.click_list = []
			op.valid = True
			for j, move in enumerate(op.moves):
				move.pos_perm = [(self.pos_name_to_id[key], self.pos_name_to_id[value]) for key, value in move.pos_perm.items()]
				for p, _ in move.pos_perm:
					self.op_by_pos[p].append((k, j))

		for selector, op_name_list in self.selector_map.items():
			sel_string, modifier = selector.split('&')
			pos_name, sel_name = sel_string.split('.')
			pos_id = self.pos_name_to_id[pos_name]
			sel_id = self.selector_name_to_id[sel_name]
			mod_id = self.modifier_to_id[modifier]
			for op_name in op_name_list:
				op_id = self.op_name_to_id[op_name]
				self.op_list[op_id].click_list.append((pos_id, sel_id, mod_id))
		self.current_click_map = np.zeros((self.total_selectors, 16), dtype = np.int32)

		self.drag_list = [[] for k in range(8)]
		for k, op in enumerate(self.op_list):
			if op.drag_modifier is not None:
				op.drag_modifier = self.modifier_to_id[op.drag_modifier]
				self.drag_list[op.drag_modifier].append(k)
			else:
				op.drag_modifier = -1