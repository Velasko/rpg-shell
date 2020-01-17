from cmd import Cmd
from subprocess import PIPE, Popen

import argparse
import os
import random
import re
import sys

if os.name != 'nt':
	BLUE = "\033[1;34;40m"
	GREEN = "\033[1;32;40m"
	WHITE = "\033[0;37;40m"
	RED = "\033[0;31;40m"
	PURPLE = "\033[0;35;40m"
else:
	BLUE = ""
	GREEN = ""
	WHITE = ""
	RED = ""
	PURPLE = ""

def cmdline(command):
	process = Popen(
		args=command,
		stdout=PIPE,
		shell=True
	)
	return process.communicate()[0]

class Roll(list):
	def __init__(self, d_type, rolls):
		super().__init__(rolls)
		self.sort(reverse = True)
		self.type = d_type
		self.value = sum(self)
		self.size = super().__len__()

	def min(self, n=1):
		self.size = min(n, super().__len__())
		self.value = sum(self[-self.size:])
		return self

	def max(self, n=1):
		self.size = min(n, super().__len__())
		self.value = sum(self[:self.size])
		return self

	def reroll(self):
		self.__init__(self.type, [random.randrange(s) + 1 for _ in range(n)])

	def get_rolls(self):
		return super().__repr__()

	def __str__(self):
		size = len(self)
		if size == 1:
			r = ''
		else:
			r = super().__repr__()
		return f'{size}d{self.type} = {self.value} {r}'

	def __repr__(self):
		return str(self)

	def __len__(self):
		return self.size

	def __add__(self, other):
		return other + self.value
	def __sub__(self, other):
		return other - self.value

def d(s, n=1):
	"""
	s: sides of die. Eg: 4, 6, 8, 10, 12, 20
	n: number of dice
	in
	"""
	if n == None:
		n = 1
	r = Roll(d_type=s, rolls=[random.randrange(s) + 1 for _ in range(n)])
	return r

def d_string(matchobj):
	_, s, m, n, t = matchobj.groups()
	if m is not None:
		if s is None:
			s = 1
		return (f'd(s={t}, n={n}).{m}({s})')
	return f'd(s={t}, n={n})'

d_pattern = "(([0-9]+ )?(min|max) )?([0-9]+)?d([0-9]+)"

class Prompt(Cmd):
	intro = '''
Welcome to RPG shell (0.1.0)
It has an integration with python shell so it's capable to execute calculations and define functions.
Type "help" or "?" for more information
	'''
	prompt = f'{PURPLE}rpg-shell> {WHITE}'
	shell_mode = False
	notes_created = []

	def default(self, inp):
		if Prompt.shell_mode:
			if inp.startswith('cd'):
				d = inp[3:]
				if d.startswith('/'):
					os.chdir(d)
				else:
					retval = os.getcwd()
					if d.startswith('./'): d = d[2:]
					os.chdir(f"{retval}/{d}")
					Prompt.prompt = f"{GREEN}sys-shell{WHITE}>{BLUE}{os.getcwd()}${WHITE} "
			else:
				os.system(inp)
			return

		i = 'a'
		while inp[-1] == ':' or i[0] in ('\t', ' '):
			sys.stdout.write(f'{PURPLE}block ...> {WHITE}')
			sys.stdout.flush()
			i = sys.stdin.readline()
			inp += f'\n{i}'
			if i == '': break

		inp = re.sub(d_pattern, d_string, inp)
		try:
			if 'os.' in inp:
				raise Exception()
			e = eval(inp)
			if e is not None: print(e)

		except Exception as e:
			try:
				exec(inp, globals())
			except Exception as e:
				name = re.match("<class '(.+)'>", str(type(e))).groups()[0]
				print(f'{RED}(Python) {name}: {e}{WHITE}')

	def do_EOF(self, inp):
		print("Ctrl + D")
		return self.do_exit(inp)

	def do_exit(self, inp):
		if Prompt.shell_mode:
			self.do_rpgmode(inp)
			return False
		for session in Prompt.notes_created:
			os.system(f"tmux kill-session -t {session}")
		print('Exit.')
		return True

	def do_cmdmode(self, inp):
		Prompt.prompt = f'{GREEN}sys-shell{WHITE}>{BLUE}{os.getcwd()}${WHITE} '
		Prompt.shell_mode = True
		files = cmdline('ls')
		print(files)

	def help_cmdmode(self):
		print("Executes system commands until rpgmode is called.")

	def do_rpgmode(self, inp):
		Prompt.prompt = f'{PURPLE}rpg-shell> {WHITE}'
		Prompt.shell_mode = False

	def help_rpgmode(self):
		print("Returns to the rpg-shell.")

	def help_nano(self):
		os.system('nano -h')

	def do_note(self, inp):
		if inp == 'open':
			print("Open notes: " + '\t'.join(Prompt.notes_created))
			return
		if inp is None: inp = 'default note'
		if not inp in Prompt.notes_created:
			cmdline(f"tmux new -d -s {inp} 'nano -m'")
			Prompt.notes_created.append(inp)
		output = cmdline(f"tmux a -t {inp}")
		if output == b'[exited]\n':
			Prompt.notes_created.remove(inp)

	def complete_note(self, text, line, begidx, endidx):
		if not text:
			return Prompt.notes_created
		else:
			return [e for e in Prompt.notes_created if e.startswith(text)]

	def help_note(self):
		return "Creates a new window with a text editor (nano)," + \
		" on which can be switched between with ctrl + b s.\n" + \
		"To return to the shell, ctrl + b d is used.\n" + \
		"The name of the note can be chosen by writing after the note command.\n" + \
		"\t Ex: \'note example\"." + \
		"\nReusing the note command with the same note will reopen the note.\n" + \
		"To check which notes are open, use \"note open\"."

	def do_clear(self, inp):
		if os.name == 'nt':
			os.system('cls')
		else:
			os.system('clear')

	def help_dice(self):
		print("A die roll is executed by typing 'xdy', on which x and y are integers.\n" + \
			"Example: 1d20")
		self.default('1d20')

	def help_dependencies(self):
		print("For this current version of the rpg-shell, for full functionality, " + \
			"it's required to run on linux and have the following programs installed:\n" + \
			"tmux\nnano")

	do_cls = do_clear

if __name__ == '__main__':
	Prompt().cmdloop()
