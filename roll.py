import random

class Roll(list):
	def __init__(self, d_type, rolls, mod=0):
		super().__init__(rolls)
		self.sort(reverse = True)
		self.type = d_type
		self.mod = mod
		self.value = sum(self) + mod
		self.size = super().__len__()

		self.minmax = 0

	def min(self, n=1):
		self.size = min(n, super().__len__())
		self.value = sum(self[-self.size:]) + self.mod
		self.minmax = -1
		return self

	def max(self, n=1):
		self.size = min(n, super().__len__())
		self.value = sum(self[:self.size]) + self.mod
		self.minmax = 1
		return self

	def reroll(self):
#		print(other)
		r = [random.randrange(self.type) + 1 for _ in range(super().__len__())]
		for n, item in enumerate(r):
			self[n] = item

		if self.minmax == -1:
			return self.min(n=self.size)
		elif self.minmax == 1:
			return self.max(n=self.size)
		else:
			self.value = sum(self) + self.mod
			return self

	def get_rolls(self):
		return super().__repr__()

	def __str__(self):
		size = super().__len__()
		if size == 1:
			r = ''
		else:
			r = super().__repr__()

		mod = ""
		if self.mod != 0:
			mod = f" + ({self.mod})"
		elif self.mod < 0:
			mod = f" - {str(self.mod)[1:]}"

		minmax = ""
		if self.minmax == -1:
			minmax = f"{len(self)} min "
		elif self.minmax == +1:
			minmax = f"{len(self)} max "

		return f'{minmax}{size}d{self.type}{mod} = {self.value} {r}'

	def __repr__(self):
		return str(self)

	def __len__(self):
		return self.size

	def __add__(self, other):
		return other + self.value
	def __sub__(self, other):
		return other - self.value

def d(s, n=1, mod=0):
	"""
	s: sides of die. Eg: 4, 6, 8, 10, 12, 20
	n: number of dice
	in
	"""
	if n == None:
		n = 1
	r = Roll(d_type=s, rolls=[random.randrange(s) + 1 for _ in range(n)], mod=mod)
	return r

def d_string(matchobj):
	_, s, m, n, t, mod = matchobj.groups()

	mod_str = ''
	if mod is not None:
		mod_str += f', mod={mod}'

	if m is not None:
		if s is None:
			s = 1
		return (f'roll.d(s={t}, n={n}{mod_str}).{m}({s})')
	return f'roll.d(s={t}, n={n}{mod_str})'

d_pattern = "(([0-9]*) *(min|max))? *([0-9]*)d([0-9]+) *([\+|-] *[0-9]+)*"

if __name__ == '__main__':
	import re

	tests = ['1d20 + 3 - 4', '2d20', '3max4d6', '3   max   4d6', '1d6 + 3']
	for inp in tests:
		print(re.sub(d_pattern, d_string, inp))