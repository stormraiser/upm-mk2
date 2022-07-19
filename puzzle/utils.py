def split_all_tags(s):
	if s == '':
		return []
	if not (s.isalpha() and s.isascii()):
		raise ValueError("Tag cycle strings may only contain letters")
	if s[0].islower():
		raise ValueError("Tag cycle strings must start with an uppercase letter")
	ret = []
	l = 0
	for k in range(1, len(s) + 1):
		if k == len(s) or s[k].isupper():
			t = s[l : k]
			if t in ret:
				raise ValueError("Tag cycle strings must not conain duplicate tags")
			ret.append(t)
			l = k
	return ret

def split_tags(s, tags):
	tokens0 = [s]
	for tag in tags:
		tokens1 = []
		for seg in tokens0:
			seg_t = seg
			while True:
				l = seg_t.find(tag)
				if l == -1:
					break
				if l > 0:
					tokens1.append(seg_t[:l])
				tokens1.append(tag)
				seg_t = seg_t[l + len(tag):]
			tokens1.append(seg_t)
		tokens0 = tokens1
	return tokens0

def perm_string(s, perm):
	tokens = split_tags(s, perm)
	for k in range(len(tokens)):
		if tokens[k] in perm:
			tokens[k] = perm[tokens[k]]
	return ''.join(tokens)

def cycle_to_perm(cycle):
	perm = {}
	for t1, t2 in zip(cycle, cycle[1:] + cycle[:1]):
		perm[t1] = t2
	return perm

def compose_perm(perm1, perm2):
	perm = {}
	for key, value in perm2.items():
		if key not in perm1:
			perm[key] = value
	for key, value in perm1.items():
		if value in perm2:
			perm[key] = perm2[value]
		else:
			perm[key] = value
	return perm

def perm_perm(perm1, perm2):
	perm = {}
	for key, value in perm2.items():
		key_t = perm1.get(key, key)
		value_t = perm1.get(value, value)
		perm[key_t] = value_t
	return perm

def transform_perm(perm1, perm2):
	perm = {}
	for key, value in perm2.items():
		perm[perm_string(key, perm1)] = perm_string(value, perm1)
	return perm

def inverse_perm(perm):
	inv_perm = {}
	for key, value in perm.items():
		inv_perm[value] = key
	return inv_perm

def perm_equal(perm1, perm2):
	for key, value in perm1.items():
		if key != value:
			if (key not in perm2) or perm2[key] != value:
				return False
	for key, value in perm2.items():
		if key != value:
			if (key not in perm1) or perm1[key] != value:
				return False
	return True

def remove_duplicate(arg_lists):
	names = set()
	ret = []
	for arg_list in arg_lists:
		if arg_list[0] not in names:
			ret.append(arg_list)
			names.add(arg_list[0])
	return ret

def merge_name_sets(name_sets):
	if len(name_sets) == 0:
		return []
	if isinstance(name_sets[0][0], list):
		f_list = True
		name_sets = [[set(t[0])] + t[1:] for t in name_sets]
	else:
		f_list = False
	merged_name_sets = []
	while len(name_sets) > 0:
		arg0 = name_sets.pop(0)
		for arg1 in name_sets:
			if not arg0[0].isdisjoint(arg1[0]):
				arg1[0].update(arg0[0])
				break
		else:
			merged_name_sets.append(arg0)
	if f_list:
		merged_name_sets = [[list(t[0])] + t[1:] for t in merged_name_sets]
	return merged_name_sets
