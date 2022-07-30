import math
import numpy as np
import collections

from .utils import *
from .move import Move

teq_eps = 1e-3
req_eps = 0.1 / 180 * math.pi

def translation_mat(v, t = 1):
	return np.array([
		[1, 0, 0, v[0] * t],
		[0, 1, 0, v[1] * t],
		[0, 0, 1, v[2] * t],
		[0, 0, 0, 1]
	], dtype = np.float32)

def rotation_mat(v, angle, t = 1):
	c = math.cos(angle * t)
	s = math.sin(angle * t)
	x, y, z, _ = v
	return np.array([
		[(1 - c) * x * x +     c, (1 - c) * x * y - z * s, (1 - c) * x * z + y * s, 0],
		[(1 - c) * y * x + z * s, (1 - c) * y * y +     c, (1 - c) * y * z - x * s, 0],
		[(1 - c) * z * x - y * s, (1 - c) * z * y + x * s, (1 - c) * z * z +     c, 0],
		[0, 0, 0, 1]
	], dtype = np.float32)

class Transform:

	def __init__(self, mat = None, tag_perm = None):
		self.mat = np.eye(4, dtype = np.float32) if mat is None else mat
		self.tag_perm = {} if tag_perm is None else tag_perm

	def mat_t(self, t):
		raise NotImplementedError

	def __matmul__(self, other):
		return Transform(other.mat @ self.mat, compose_perm(self.tag_perm, other.tag_perm))

	def __eq__(self, other):
		return perm_equal(self.tag_perm, other.tag_perm)

	def transform(self, obj):
		if isinstance(obj, str):
			return perm_string(obj, self.tag_perm)
		elif isinstance(obj, TransformSequence):
			return TransformSequence(obj.puzzle, [self.transform(tr) for tr in obj.seq])
		elif isinstance(obj, Translation):
			return Translation(self.mat @ obj.v)
		elif isinstance(obj, Rotation):
			return Rotation(obj.angle, self.mat @ obj.v, self.mat @ obj.p)
		elif isinstance(obj, Transform):
			return Transform(self.mat @ obj.mat, perm_perm(self.tag_perm, obj.tag_perm))
		elif isinstance(obj, collections.abc.Iterable):
			return [self.transform(tr) for tr in obj]
		elif isinstance(obj, Move):
			tr = self.transform(obj.transform)
			pos_perm = transform_perm(self.tag_perm, obj.pos_perm)
			return Move(tr, pos_perm)
		else:
			return obj

class Translation(Transform):

	def __init__(self, v):
		super().__init__(translation_mat(v, 1))
		self.v = v

	def mat_t(self, t = 1):
		return translation_mat(self.v, t)

	def inverse(self):
		return Translation(-self.v)

	def __repr__(self):
		return 'translation({0:.3f}, {1:.3f}, {2:.3f})'.format(self.v[0], self.v[1], self.v[2])

	def __eq__(self, other):
		d = np.linalg.norm(self.v - other.v)
		return d <= teq_eps

class Rotation(Transform):

	def __init__(self, angle, v, p):
		super().__init__()
		self.p = p
		self.v = v
		self.v = self.v / np.linalg.norm(self.v)
		self.angle = angle
		self.mat = self.mat_t(1)

	def mat_t(self, t = 1):
		t1_mat = translation_mat(-self.p)
		rot_mat = rotation_mat(self.v, self.angle, t)
		t2_mat = translation_mat(self.p)
		return t2_mat @ rot_mat @ t1_mat

	def inverse(self):
		return Rotation(-self.angle, self.v, self.p)

	def __repr__(self):
		return 'rotation({0:.3f}, {1:.3f}, {2:.3f}, {3:.3f}, {4:.3f}, {5:.3f}, {6:.3f})'.format(self.angle, self.v[0], self.v[1], self.v[2], self.p[0], self.p[1], self.p[2])

	def __eq__(self, other):
		d = np.linalg.norm(self.p - other.p)
		if d > teq_eps:
			return False
		r1 = math.acos(min(1, max(-1, np.dot(self.v, other.v))))
		r2 = self.angle - other.angle
		if r1 <= req_eps:
			return abs(r2) <= req_eps or abs(r2 - math.pi * 2) <= req_eps or abs(r2 + math.pi * 2) <= req_eps
		elif r1 >= math.pi - req_eps:
			return abs(r2 - math.pi) <= req_eps or abs(r2 + math.pi) <= req_eps
		else:
			return False

class TagPerm(Transform):

	def __init__(self, puzzle, cycles):
		super().__init__()
		for s in cycles:
			cycle = split_all_tags(s)
			for tag in cycle:
				puzzle.add_tag(tag)
			self.tag_perm = compose_perm(self.tag_perm, cycle_to_perm(cycle))

class TransformSet:

	def __init__(self, puzzle, transforms = None):
		self.puzzle = puzzle
		self.transforms = [] if transforms is None else transforms

	def __matmul__(self, other):
		ret = TransformSet(self.puzzle)
		for tr1 in self.transforms:
			for tr2 in other.transforms:
				tr = tr1 @ tr2
				if not tr in ret.transforms:
					ret.transforms.append(tr)
		return ret

	def __or__(self, other):
		ret = TransformSet(self.puzzle)
		ret.transforms.extend(self.transforms)
		for tr in other.transforms:
			if not tr in ret.transforms:
				ret.transforms.append(tr)

	def __enter__(self):
		self.puzzle.push_sym(self)

	def __exit__(self, exc_type, exc_value, traceback):
		self.puzzle.pop_sym()
		return False

	def transform(self, obj):
		return [tr.transform(obj) for tr in self.transforms]

class TransformSequence(TransformSet):

	def __init__(self, puzzle, seq):
		super().__init__(puzzle)
		self.seq = seq
		tr0 = Transform()
		for tr in self.seq:
			tr0 = tr0 @ tr
		self.transforms.append(tr0)

	def mat_t(self, t = 1):
		mat = np.eye(4, dtype = np.float32)
		for tr in self.seq:
			mat = tr.mat_t(t) @ mat
		return mat

	def __matmul__(self, other):
		return TransformSequence(self.puzzle, self.seq + other.seq)

	def inverse(self):
		if len(self.seq) > 1:
			print("check inverse move sequence")
		seq = []
		for i in range(len(self.seq)):
			tr = self.seq[i]
			for j in range(i + 1, len(self.seq)):
				tr = self.seq[j].transform(tr)
			seq.append(tr.inverse())
		return TransformSequence(self.puzzle, seq)

	def __call__(self, *positions):
		geom_tr = []
		tag_perm = Transform()
		for tr in self.seq:
			if isinstance(tr, (Translation, Rotation)):
				geom_tr.append(tr)
			else:
				tag_perm = tag_perm @ tr
		target = tag_perm.transform(positions)
		geom_tr = TransformSequence(self.puzzle, geom_tr)
		pos_perm = dict(zip(positions, target))
		return Move(geom_tr, pos_perm)

	def __eq__(self, other):
		return self.seq == other.seq

class PuzzleTransformMixin:

	def push_sym(self, tr_set):
		self.sym_stack.append(self.sym_stack[-1] @ tr_set)

	def pop_sym(self):
		self.sym_stack.pop()

	def translate(self, x, y, z):
		return TransformSequence(self, [Translation(np.array([x, y, z, 0], dtype = np.float32))])

	def rotate(self, angle_deg, x, y, z, x0 = 0, y0 = 0, z0 = 0):
		return TransformSequence(self, [Rotation(
			angle_deg / 180 * math.pi,
			np.array([x, y, z, 0], dtype = np.float32),
			np.array([x0, y0, z0, 1], dtype = np.float32)
		)])

	def tag_cycle(self, *args):
		tag_perm = {}
		for s in args:
			cycle = split_all_tags(s)
			for tag in cycle:
				self.add_tag(tag)
			tag_perm = compose_perm(tag_perm, cycle_to_perm(cycle))
		return TransformSequence(self, [Transform(tag_perm = tag_perm)])

	def group(self, *args):
		ret = TransformSet(self)
		gen = []
		for tr_set in args:
			for tr in tr_set.transforms:
				if tr not in gen:
					gen.append(tr)
		open_list = [Transform()]
		while len(open_list) > 0:
			tr0 = open_list.pop(0)
			for tr in gen:
				tr1 = tr0 @ tr
				if tr1 not in ret.transforms:
					ret.transforms.append(tr1)
					open_list.append(tr1)
		return ret

	def add_tag(self, new_tag):
		for tag in self.tag_set:
			if tag == new_tag:
				return
			if tag.startswith(new_tag) or new_tag.startswith(tag):
				raise ValueError("A tag cannot contain another tag as prefix")
		self.tag_set.add(new_tag)
