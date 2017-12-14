#!/usr/bin/python

import sys
import argparse
import yaml

from yaml_cli.version import __version__

ACTION_SET = 'set'
ACTION_RM  = 'rm'

BOOLEAN_VALUES_TRUE = ('1', 'true', 'True')
BOOLEAN_VALUES_FALSE = ('', '0', 'false', 'False')

HELP_KEY_SYNTAX = "mykey:subkey:subkey"

class YamlCli(object):
	DEBUG   = False
	VERBOSE = False

	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('file', type=str, help="yaml file to load")
		parser.add_argument('-o', '--output', type=str, help="Output file. If not provided output is written to STDOUT")
		parser.add_argument('-d', '--delete', action=RmKeyAction, help="Delete key: {}".format(HELP_KEY_SYNTAX))
		parser.add_argument('-s', '--string', action=KeyValueAction, help="Set key with string value: {} 'my value'".format(HELP_KEY_SYNTAX))
		parser.add_argument('-n', '--number', action=NumberKeyValueAction, help="Set key with number value: {} 3.7".format(HELP_KEY_SYNTAX))
		parser.add_argument('-b', '--boolean', action=BooleanKeyValueAction, help="Set key with number value: {} true (possible values: {} {})".format(HELP_KEY_SYNTAX, BOOLEAN_VALUES_TRUE, BOOLEAN_VALUES_FALSE))
		parser.add_argument('-l', '--list', action=ListKeyValueAction, help="Set key with value as list of strings: {} intem1 intem2 intem3".format(HELP_KEY_SYNTAX))
		parser.add_argument('--null', action=NullKeyAction, help="Set key with null value: {}".format(HELP_KEY_SYNTAX))
		parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
		parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
		parser.add_argument('--debug', action='store_true', help="Debug output")
		args = parser.parse_args()

		self.DEBUG = args.debug
		self.VERBOSE = args.verbose or args.debug
		self.log("Input argparse: {}".format(args), debug=True)

		myYaml = self.load_yaml(args.file)

		if args.set_keys:
			for elem in args.set_keys:
				if elem['action'] == ACTION_SET:
					self.log("setting key {}".format(elem))
					myYaml = self.set_key(myYaml, elem['key'], elem['val'])
				if elem['action'] == ACTION_RM:
					self.log("deleting key {}".format(elem))
					myYaml = self.rm_key(myYaml, elem['key'])

		print(yaml.dump(myYaml, default_flow_style=False))


	def load_yaml(self, name):
		res = None
		try:
			with open(name, 'r') as stream:
				try:
					return yaml.load(stream)
				except yaml.YAMLError as exc:
					print(exc)
					sys.exit(1)
		except IOError as e:
			print(e)
			sys.exit(1)

	def set_key(self, myYaml, key, value):
		self.log("set_key {} = {}".format(key, value), debug=True)
		if len(key) == 1:
			myYaml[key[0]] = value
		else:
			if not key[0] in myYaml:
				myYaml[key[0]] = {}
			myYaml[key[0]] = self.set_key(myYaml[key[0]], key[1:], value)
		return myYaml

	def rm_key(self, myYaml, key):
		self.log("delete_key {}".format(key), debug=True)
		if len(key) == 1:
			del myYaml[key[0]]
		elif key[0] in myYaml:
			myYaml[key[0]] = self.rm_key(myYaml[key[0]], key[1:])
		return myYaml


	def log(self, msg, debug=False):
		if self.VERBOSE or (debug and self.DEBUG):
			ds = 'DEBUG ' if debug else ''
			print("{debug}{msg}".format(debug=ds, msg=msg))


def run():
	YamlCli()

if __name__ == "__main__":
	run()




#############################################
####   ACTIONS
#############################################

class KeyValueAction(argparse.Action):
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(KeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.dest = 'set_keys'
		self.nargs = 2
		self.type = KeyValueType()
		self.metavar = 'KEY', 'VAL'

	def __call__(self, parser, namespace, values, option_string=None):
		entry = dict(
			key = values[0],
			val = values[1],
			action = ACTION_SET
		)
		data = getattr(namespace, self.dest)
		if data is None: data = []
		data.append(entry)
		setattr(namespace, self.dest, data)
		self.reset_type()

	def _string_to_key(self, string):
		arr = string.split(':')

	def reset_type(self):
		try:
			reset = self.type.reset
		except AttributeError:
			pass
		else:
			reset()


class NumberKeyValueAction(KeyValueAction):
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(NumberKeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.type = NumberKeyValueType()


class BooleanKeyValueAction(KeyValueAction):
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(BooleanKeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.type = BooleanKeyValueType()


class NullKeyAction(KeyValueAction):
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(NullKeyAction, self).__init__(option_strings, dest, **kwargs)
		self.nargs = 1
		self.type = KeyValueType()
		self.metavar = 'KEY'

	def __call__(self, parser, namespace, values, option_string=None):
		entry = dict(
			key = values[0],
			val = None,
			action = ACTION_SET
		)
		data = getattr(namespace, self.dest)
		if data is None: data = []
		data.append(entry)
		setattr(namespace, self.dest, data)
		self.reset_type()


class RmKeyAction(KeyValueAction):
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(RmKeyAction, self).__init__(option_strings, dest, **kwargs)
		self.nargs = 1
		self.type = KeyValueType()
		self.metavar = 'KEY'

	def __call__(self, parser, namespace, values, option_string=None):
		entry = dict(
			key = values[0],
			val = None,
			action = ACTION_RM
		)
		data = getattr(namespace, self.dest)
		if data is None: data = []
		data.append(entry)
		setattr(namespace, self.dest, data)
		self.reset_type()


class ListKeyValueAction(KeyValueAction):
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(ListKeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.nargs = '+'
		self.type = KeyValueType()

	def __call__(self, parser, namespace, values, option_string=None):
		entry = dict(
			key = values[0],
			val = values[1:],
			action = ACTION_SET
		)
		data = getattr(namespace, self.dest)
		if data is None: data = []
		data.append(entry)
		setattr(namespace, self.dest, data)
		self.reset_type()


#############################################
####   TYPES
#############################################

class KeyValueType(object):
	def __init__(self):
		self.key_expected = True
		self.last_key = None

	def __call__(self, string):
		if self.key_expected:
			self.key_expected = False
			self.last_key = string
			return self.verify_key(string)
		else:
			# self.key_expected = True
			return self.verify_val(string)

	def reset(self):
		self.key_expected = True
		self.last_key = None

	def verify_key(self, string):
		arr = string.split(':')
		if len(arr) != len(filter(None, arr)):
			msg = "'{}' is not a valid key".format(string)
			raise argparse.ArgumentTypeError(msg)
		else:
			return arr

	def verify_val(self, string):
		return string


class NumberKeyValueType(KeyValueType):
	def verify_val(self, string):
		try:
			return int(string)
		except Exception as e:
			pass
		try:
			return float(string)
		except Exception as e:
			msg = "'{}' is not a number for key {}".format(string, self.last_key)
			raise argparse.ArgumentTypeError(msg)


class BooleanKeyValueType(KeyValueType):
	def verify_val(self, string):
		if string in BOOLEAN_VALUES_FALSE:
			return False
		if string in BOOLEAN_VALUES_TRUE:
			return True
		msg = "'{}' is not a boolean for key {}".format(string, self.last_key)
		raise argparse.ArgumentTypeError(msg)





