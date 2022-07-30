import math

import numpy as np

from .utils import *

class PosTreeNode:

	def __init__(self, children = None, name = None):
		self.name = name
		self.children = [] if children is None else children

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

		### assign id to puzzle elements

		model_items = sorted(self.model_map.items())
		self.model_list = [item[1] for item in model_items]
		self.model_invmap = {item[0]: k for k, item in enumerate(model_items)}
		del self.model_map

		texture_items = sorted(self.texture_map.items())
		self.texture_list = [item[1] for item in texture_items]
		self.texture_invmap = {item[0]: k for k, item in enumerate(texture_items)}
		del self.texture_map

		block_items = sorted(self.block_map.items())
		self.block_list = [item[1] for item in block_items]
		self.block_invmap = {item[0]: k for k, item in enumerate(block_items)}
		del self.block_map

		op_items = sorted(self.op_map.items())
		self.op_list = [item[1] for item in op_items]
		self.op_invmap = {item[0]: k for k, item in enumerate(op_items)}
		del self.op_map

		# pos ids here are provisional

		pos_set = set()
		for op in self.op_list:
			for move in op.moves:
				pos_set.update(move.pos_perm.keys())
				pos_set.update(move.pos_perm.values())
		pos_set.update(self.plink_map.keys())
		pos_set.update(self.plink_map.values())
		for block in self.block_list:
			pos_set.add(block.start_pos)
		tmp_pos_list = sorted(list(pos_set))
		self.pos_invmap = {pos: k for k, pos in enumerate(tmp_pos_list)}

		self.blink_list = np.full((len(self.block_list),), -1, dtype = np.int32)
		for key, value in self.blink_map.items():
			self.blink_list[self.block_invmap[key]] = self.block_invmap[value]
		del self.blink_map, self.blink_invmap

		tmp_plink_list = np.full((len(tmp_pos_list),), -1, dtype = np.int32)
		for key, value in self.plink_map.items():
			tmp_plink_list[self.pos_invmap[key]] = self.pos_invmap[value]
		del self.plink_map, self.plink_invmap

		for block in self.block_list:
			block.start_pos = self.pos_invmap[block.start_pos]
		for block0, block1 in enumerate(self.blink_list):
			if block1 != -1:
				pos0 = self.block_list[block0].start_pos
				pos1 = self.block_list[block1].start_pos
				if tmp_plink_list[pos0] == -1:
					tmp_plink_list[pos0] = pos1
				# asynchronous block links and position links are allowed here.
				# pos links can be finer than block links.
				# possible improvement: Check later that block ring is a sub-ring of pos ring

		### propagate operations and links
		# this part might be wrong. I really should find a rigorous method

		pos_op_to_move = np.full((len(tmp_pos_list), len(self.op_list)), -1, dtype = np.int32)
		pos_op_to_target = np.full((len(tmp_pos_list), len(self.op_list)), -1, dtype = np.int32)
		pos_op_to_invmove = np.full((len(tmp_pos_list), len(self.op_list)), -1, dtype = np.int32)
		pos_op_to_invtarget = np.full((len(tmp_pos_list), len(self.op_list)), -1, dtype = np.int32)
		for op_id, op in enumerate(self.op_list):
			for move_id, move in enumerate(op.moves):
				for key, value in move.pos_perm.items():
					pos0 = self.pos_invmap[key]
					pos1 = self.pos_invmap[value]
					pos_op_to_move[pos0, op_id] = move_id
					pos_op_to_target[pos0, op_id] = pos1
					pos_op_to_invmove[pos1, op_id] = move_id
					pos_op_to_invtarget[pos1, op_id] = pos0

		open_set = set(range(len(tmp_pos_list)))
		while len(open_set) > 0:
			pos = open_set.pop()
			pos_n = tmp_plink_list[pos]
			if pos_n >= 0:
				for op_id in range(len(self.op_list)):

					pos_t = pos_op_to_target[pos, op_id]
					if pos_t >= 0:
						pos_nt = pos_op_to_target[pos_n, op_id]
						pos_tn = tmp_plink_list[pos_t]
						if pos_nt >= 0:
							if pos_op_to_move[pos, op_id] != pos_op_to_move[pos_n, op_id]:
								raise ValueError("Incompatible position link and operations")
							if pos_tn >= 0:
								if pos_nt != pos_tn:
									raise ValueError("Incompatible position link and operations")
							else:
								tmp_plink_list[pos_t] = pos_nt
								open_set.add(pos_t)
								open_set.add(pos)
						else:
							if pos_tn >= 0:
								pos_op_to_target[pos_n, op_id] = pos_tn
								pos_op_to_move[pos_n, op_id] = pos_op_to_move[pos, op_id]
								pos_op_to_invtarget[pos_tn, op_id] = pos_n
								pos_op_to_invmove[pos_tn, op_id] = pos_op_to_invmove[pos_t, op_id]
								open_set.add(pos_n)
								open_set.add(pos)
								open_set.add(pos_tn)
								open_set.add(pos_t)
					
					pos_t = pos_op_to_invtarget[pos, op_id]
					if pos_t >= 0:
						pos_nt = pos_op_to_invtarget[pos_n, op_id]
						pos_tn = tmp_plink_list[pos_t]
						if pos_nt >= 0:
							if pos_op_to_invmove[pos, op_id] != pos_op_to_invmove[pos_n, op_id]:
								raise ValueError("Incompatible position link and operations")
							if pos_tn >= 0:
								if pos_nt != pos_tn:
									raise ValueError("Incompatible position link and operations")
							else:
								tmp_plink_list[pos_t] = pos_nt
								open_set.add(pos_t)
								open_set.add(pos)
						else:
							if pos_tn >= 0:
								pos_op_to_invtarget[pos_n, op_id] = pos_tn
								pos_op_to_invmove[pos_n, op_id] = pos_op_to_invmove[pos, op_id]
								pos_op_to_target[pos_tn, op_id] = pos_n
								pos_op_to_move[pos_tn, op_id] = pos_op_to_move[pos_t, op_id]
								open_set.add(pos_n)
								open_set.add(pos)
								open_set.add(pos_tn)
								open_set.add(pos_t)

		for k in range(tmp_plink_list.shape[0]):
			if tmp_plink_list[k] >= 0 and tmp_plink_list[tmp_plink_list[k]] == -1:
				raise ValueError("Incomplete ring of position links")

		for pos in range(pos_op_to_move.shape[0]):
			pos_n = tmp_plink_list[pos]
			if pos_n >= 0:
				for op_id in range(pos_op_to_move.shape[1]):
					pos_t = pos_op_to_target[pos, op_id]
					if pos_t >= 0:
						pos_nt = pos_op_to_target[pos_n, op_id]
						pos_tn = tmp_plink_list[pos_t]
						if pos_nt == -1 and pos_tn == -1:
							raise ValueError("Incomplete information for link & op propagation")

		### remove useless positions
		# also find orbits
		pos_checked_flag = np.zeros(len(tmp_pos_list), dtype = bool)
		tmp_pos_orbit = np.full((len(tmp_pos_list),), -1, dtype = np.int32)
		num_orbits = 0
		for block in self.block_list:
			pos0 = block.start_pos
			if not pos_checked_flag[pos0]:
				closed_set = []
				open_set = {pos0}
				while len(open_set) > 0:
					pos = open_set.pop()
					closed_set.append(pos)
					pos_checked_flag[pos] = True
					for op_id in range(len(self.op_list)):
						pos1 = pos_op_to_target[pos, op_id]
						if pos1 >= 0 and not pos_checked_flag[pos1]:
							open_set.add(pos1)
				if len(closed_set) > 1:
					for pos in closed_set:
						tmp_pos_orbit[pos] = num_orbits
					num_orbits += 1

		# assign new pos id

		m = 0
		new_pos_id = np.full((len(tmp_pos_list),), -1, dtype = np.int32)
		self.pos_list = []
		for i in range(len(tmp_pos_list)):
			if tmp_pos_orbit[i] >= 0:
				self.pos_list.append(tmp_pos_list[i])
				new_pos_id[i] = m
				m += 1
			else:
				new_pos_id[i] = -1
		self.start_state = np.full((len(self.pos_list),), -1, dtype = np.int32)

		for tmp_pos_id, pos_name in enumerate(tmp_pos_list):
			self.pos_invmap[pos_name] = new_pos_id[tmp_pos_id] if tmp_pos_orbit[tmp_pos_id] >= 0 else -1
		for k, block in enumerate(self.block_list):
			block.start_pos = new_pos_id[block.start_pos]
			if block.start_pos >= 0:
				self.start_state[block.start_pos] = k

		### build position tree
		# rings in the same orbit -> orbits -> orbits linked by rings -> classes

		orbit_list = [PosTreeNode() for k in range(num_orbits)]
		orbit_mergers = []
		pos_checked_flag = np.zeros(len(tmp_pos_list), dtype = bool)
		for k in range(len(tmp_pos_list)):
			orbit_id = tmp_pos_orbit[k]
			if orbit_id == -1:
				continue
			if pos_checked_flag[k]:
				continue
			pos_checked_flag[k] = True
			ring = PosTreeNode([new_pos_id[k]], tmp_pos_list[k])
			orbit_merger = {orbit_id}
			t = tmp_plink_list[k]
			if t == -1:
				orbit_mergers.append([orbit_merger])
				orbit_list[orbit_id].children.append(ring)
				continue
			while t != k:
				if tmp_pos_orbit[t] == orbit_id:
					pos_checked_flag[t] = True
					ring.children.append(new_pos_id[t])
				else:
					orbit_merger.add(tmp_pos_orbit[t])
				t = tmp_plink_list[t]
			orbit_mergers.append([orbit_merger])
			orbit_list[orbit_id].children.append(ring)
		for orbit in orbit_list:
			orbit.name = orbit.children[0].name

		orbit_mergers = merge_name_sets(orbit_mergers)
		orbit_mergers = sorted([sorted(t[0]) for t in orbit_mergers])

		group_list = [PosTreeNode([orbit_list[k] for k in orbit_merger]) for orbit_merger in orbit_mergers]
		for group in group_list:
			group.name = group.children[0].name

		block_name_to_group = {}
		for group_id, group in enumerate(group_list):
			for orbit in group.children:
				for ring in orbit.children:
					for pos_id in ring.children:
						block_id = self.start_state[pos_id]
						if block_id >= 0:
							block_name_to_group[self.block_list[block_id].name] = group_id

		group_mergers = [{block_name_to_group[name] for name in class_merger if name in block_name_to_group} for class_merger in self.class_mergers]
		group_mergers = [[t] for t in group_mergers if len(t) > 0]
		group_mergers.extend([[{k}] for k in range(len(group_list))])
		group_mergers = merge_name_sets(group_mergers)
		group_mergers = sorted([sorted(t[0]) for t in group_mergers])

		class_list = [PosTreeNode([group_list[k] for k in group_merger]) for group_merger in group_mergers]
		for pos_class in class_list:
			pos_class.name = pos_class.children[0].name

		self.pos_tree = PosTreeNode(class_list)

		### process op

		for op in self.op_list:
			for move in op.moves:
				move.pos_perm = []

		self.pos_to_op = [[] for k in range(len(self.pos_list))]
		for old_pos0 in range(len(tmp_pos_list)):
			if tmp_pos_orbit[old_pos0] >= 0:
				pos0 = new_pos_id[old_pos0]
				for op_id in range(len(self.op_list)):
					old_pos1 = pos_op_to_target[old_pos0, op_id]
					if old_pos1 >= 0 and tmp_pos_orbit[old_pos1] >= 0:
						pos1 = new_pos_id[old_pos1]
						move_id = pos_op_to_move[old_pos0, op_id]
						self.op_list[op_id].moves[move_id].pos_perm.append((pos0, pos1))
						self.pos_to_op[pos0].append((op_id, move_id))

		for op in self.op_list:
			op.click_list = []
			op.valid = True
			start_pos = set()
			end_pos = set()
			for move in op.moves:
				start_pos.update([t[0] for t in move.pos_perm])
				end_pos.update([t[1] for t in move.pos_perm])
			forbidden_pos = [self.pos_invmap[name] for name in op.forbidden_pos]
			forbidden_pos = [t for t in forbidden_pos if t >= 0]
			forbidden_pos.extend(end_pos - start_pos)
			op.forbidden_pos = sorted(forbidden_pos)
			required_pos = [self.pos_invmap[name] for name in op.required_pos]
			required_pos = [t for t in required_pos if t >= 0]
			op.required_pos = sorted(required_pos)

		### gather model instances

		self.total_parts = 0
		self.total_selectors = 0
		all_part_names = set()
		all_selector_names = set()
		for k, block in enumerate(self.block_list):
			self.total_parts += len(block.parts)
			self.total_selectors += len(block.selectors)
			all_part_names.update(block.parts.keys())
			all_selector_names.update(block.selectors.keys())
		self.all_part_names = sorted(all_part_names)
		self.all_selector_names = sorted(all_selector_names)
		self.part_invmap = {name: k for k, name in enumerate(self.all_part_names)}
		self.selector_invmap = {name: k for k, name in enumerate(self.all_selector_names)}
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
			model.tex_instances = [[] for i in range(len(self.texture_list))]
			model.selector_instances = []
		self.part_id_to_block_id = []

		for i, block in enumerate(self.block_list):
			block.part_list = [None] * self.num_part_names
			for part_name, (model, color, mat) in block.parts.items():
				model_id = self.model_invmap[model.path]
				k = self.part_invmap[part_name]
				block.part_list[k] = (model_id, color, mat, instance_id_to_pick_color(total_part_id))
				total_part_id += 1
				if isinstance(color, str) and self.clr_tex_map[color][0]:
					tex_id = self.texture_invmap[self.clr_tex_map[color][1]]
					self.model_list[model_id].tex_instances[tex_id].append((i, k))
				else:
					self.model_list[model_id].part_instances.append((i, k))
				self.part_id_to_block_id.append(i)
			del block.parts

			block.selector_list = [None] * self.num_selector_names
			for selector_name, (model, mat) in block.selectors.items():
				model_id = self.model_invmap[model.path]
				k = self.selector_invmap[selector_name]
				block.selector_list[k] = (model_id, mat, total_selector_id, instance_id_to_pick_color(total_selector_id + self.total_parts))
				total_selector_id += 1
				self.model_list[model_id].selector_instances.append((i, k))
			del block.selectors

		### TODO: clean these up

		for selector, op_name_list in self.selector_map.items():
			sel_string, modifier = selector.split('&')
			pos_name, sel_name = sel_string.split('.')
			pos_id = self.pos_invmap[pos_name]
			if pos_id >= 0:
				sel_id = self.selector_invmap[sel_name]
				mod_id = self.modifier_to_id[modifier]
				for op_name in op_name_list:
					op_id = self.op_invmap[op_name]
					self.op_list[op_id].click_list.append((pos_id, sel_id, mod_id))
		self.current_click_map = np.zeros((self.total_selectors, 16), dtype = np.int32)

		self.drag_list = [[] for k in range(8)]
		for k, op in enumerate(self.op_list):
			if op.drag_modifier is not None:
				op.drag_modifier = self.modifier_to_id[op.drag_modifier]
				self.drag_list[op.drag_modifier].append(k)
			else:
				op.drag_modifier = -1
