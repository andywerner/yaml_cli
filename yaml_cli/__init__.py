#!/usr/bin/env python

import sys
import argparse
import fileinput
import sys
import os
import yaml

from yaml_cli.version import __version__

ACTION_SET = 'set'
ACTION_RM  = 'rm'

BOOLEAN_VALUES_TRUE = ('1', 'true', 'True', 'yes')
BOOLEAN_VALUES_FALSE = ('', '0', 'false', 'False', 'no')

HELP_KEY_SYNTAX = "mykey:subkey:subkey"


class YamlCli(object):
	DEBUG   = False
	VERBOSE = False

	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('-i', '--input',   type=str, metavar='FILE', help="YAML file to load. ")
		parser.add_argument('-o', '--output',  type=str, metavar='FILE', help="Output file. If not provided output is written to STDOUT")
		parser.add_argument('-f', '--file',    type=str, metavar='FILE', help="YAML file for inplace manipulation.")
		parser.add_argument('-d', '--delete',  action=RmKeyAction, help="Delete key: {}. Skipped silently if key doesn't exist.".format(HELP_KEY_SYNTAX))
		parser.add_argument('-s', '--string',  action=KeyValueAction, help="Set key with string value: {} 'my value'".format(HELP_KEY_SYNTAX))
		parser.add_argument('-n', '--number',  action=NumberKeyValueAction, help="Set key with number value: {} 3.7".format(HELP_KEY_SYNTAX))
		parser.add_argument('-b', '--boolean', action=BooleanKeyValueAction, help="Set key with number value: {} true (possible values: {} {})".format(HELP_KEY_SYNTAX, BOOLEAN_VALUES_TRUE, BOOLEAN_VALUES_FALSE))
		parser.add_argument('-l', '--list',    action=ListKeyValueAction, help="Set key with value as list of strings: {} intem1 intem2 intem3".format(HELP_KEY_SYNTAX))
		parser.add_argument('--null',          action=NullKeyAction, help="Set key with null value: {}".format(HELP_KEY_SYNTAX))
		parser.add_argument('-la', '--list-append', action='store_true', help="If a key to set already exists, do not replace it but instead create a list and append.")
		parser.add_argument('--version',       action='version', version='%(prog)s ' + __version__)
		parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")
		parser.add_argument('--debug',         action='store_true', help="Debug output")
		args = parser.parse_args()

		try:
			self.DEBUG = args.debug
			self.VERBOSE = args.verbose or args.debug
			self.log("Input argparse: {}".format(args), debug=True)

			append_mode = args.list_append

			infile =  args.input or args.file
			outfile = args.output or args.file

			myYaml = self.get_input_yaml(infile)

			if args.set_keys:
				for elem in args.set_keys:
					try:
						if elem['action'] == ACTION_SET:
							self.log("setting key {}".format(elem))
							myYaml = self.set_key(myYaml, elem['key'], elem['val'], append_mode)
						if elem['action'] == ACTION_RM:
							self.log("deleting key {}".format(elem))
							myYaml = self.rm_key(myYaml, elem['key'])
					except:
						log_exception("Exception while handling key {}".format(elem['key']))

			if outfile:
				self.save_yaml(outfile, myYaml)
			else:
				self.stdout_yaml(myYaml)
		except Exception:
			log_exception()

	def get_input_yaml(self, filename):
		"""
		Get YAML input either from file or from STDIN
		In case of any error, sys.exit(1) is called
		:param filename:
		:return: dict YAML data
		"""
		if filename:
			return self.load_yaml_from_file(filename)
		else:
			return self.read_yaml_from_sdtin()

	def load_yaml_from_file(self, name):
		"""
		load YAML file
		In case of any error, this function calls sys.exit(1)
		:param name: path & file name
		:return: YAML as dict
		"""
		try:
			with open(name, 'r') as stream:
				try:
					return yaml.safe_load(stream)
				except yaml.YAMLError as exc:
					print(exc)
					sys.exit(1)
		except IOError as e:
			print(e)
			sys.exit(1)

	def read_yaml_from_sdtin(self):
		if sys.stdin.isatty():
			return dict()
		res = sys.stdin.read()
		try:
			read = yaml.safe_load(res)
			# Let's find out why load(sometimes returns plain strings or None a if this has a good reason)
			if type(read) is dict:
				return read
			else:
				print("No valid YAML input: '%s'" % res)
				sys.exit(1)
		except yaml.YAMLError as exc:
			print(exc)
			sys.exit(1)

	def save_yaml(self, name, data):
		"""
		Saves given YAML data to file
		:param name: file path
		:param data: YAML data
		"""
		try:
			with open(name, 'w') as outfile:
				yaml.dump(data, outfile, default_flow_style=False)
		except IOError as e:
			print(e)
			sys.exit(1)

	def stdout_yaml(self, data):
		"""
		Prints YAML data to STDOUT
		:param data: YAML data
		:return:
		"""
		print(yaml.dump(data, default_flow_style=False))

	def set_key(self, myYaml, key, value, append_mode=False):
		"""
		Set or add a key to given YAML data. Call itself recursively.
		:param myYaml: YAML data to be modified
		:param key: key as array of key tokens
		:param value: value of any data type
		:param append_mode default is False
		:return: modified YAML data
		"""
		# self.log("set_key {} = {} | yaml: {}".format(key, value, myYaml), debug=True)
		if len(key) == 1:
			if not append_mode or not key[0] in myYaml:
				myYaml[key[0]] = value
			else:
				if type(myYaml[key[0]]) is not list:
					myYaml[key[0]] = [myYaml[key[0]]]
				myYaml[key[0]].append(value)
		else:
			if not key[0] in myYaml or type(myYaml[key[0]]) is not dict:
				# self.log("set_key {} = {} creating item".format(key, value, myYaml), debug=True)
				myYaml[key[0]] = {}
			myYaml[key[0]] = self.set_key(myYaml[key[0]], key[1:], value, append_mode)
		return myYaml

	def rm_key(self, myYaml, key):
		"""
		Remove a key and it's value from given YAML data structure.
		No error or such thrown if the key doesn't exist.
		:param myYaml: YAML data to be modified
		:param key: key as array of key tokens
		:return: modified YAML data
		"""
		# self.log("rm_key {} | yaml: {}".format(key, myYaml), debug=True)
		if len(key) == 1 and key[0] in myYaml:
			del myYaml[key[0]]
		elif key[0] in myYaml:
			myYaml[key[0]] = self.rm_key(myYaml[key[0]], key[1:])
		return myYaml


	def log(self, msg, debug=False):
		"""
		Write a message to STDOUT
		:param msg: the message to print
		:param debug: If True the message is only printed if --debug flag is set
		"""
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
	"""
	Action for pair of key and string value.
	Action that defines and handles a key value pair from command line where value is of type string.
	All key value pairs are stored in 'set_keys' in the resulting namespace object.
	Requires KeyValueType
	"""
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(KeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.dest = 'set_keys'
		self.nargs = 2
		self.type = KeyValueType()
		self.metavar = 'KEY', 'VAL'

	def __call__(self, parser, namespace, values, option_string=None):
		"""
		Gets called for each pair of arguments after they have been type checked.
		:param parser:
		:param namespace:
		:param values: holding the values read from command line
		:param option_string:
		"""
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

	def reset_type(self):
		"""
		All KeyValueTypes (self.type) need to be reset once all data values are read.
		This method silently fails if the type in self.type is not resettable.
		"""
		try:
			reset = self.type.reset
		except AttributeError:
			pass
		else:
			reset()


class NumberKeyValueAction(KeyValueAction):
	"""
	Action for pair of key and numeric value. (int and float)
	Requires NumberKeyValueType
	"""
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(NumberKeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.type = NumberKeyValueType()


class BooleanKeyValueAction(KeyValueAction):
	"""
	Action for pair of key and boolean value.
	Valid input to be interpreted as booleans are defined in BOOLEAN_VALUES_TRUE and BOOLEAN_VALUES_FALSE
	Requires BooleanKeyValueType
	"""
	def __init__(self, option_strings, dest, nargs=None, **kwargs):
		super(BooleanKeyValueAction, self).__init__(option_strings, dest, **kwargs)
		self.type = BooleanKeyValueType()


class NullKeyAction(KeyValueAction):
	"""
	Action for a key which value will be set to null.
	Expects only one argument namely the key.
	Requires KeyValueType
	"""
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
	"""
	Action for a key which value will be removed from YAML data.
	Expects only one argument namely the key.
	Requires KeyValueType
	"""
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
	"""
	Action for a key with one, multiple or none value.
	Can be provided with any number of values
	Requires KeyValueType
	"""
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
	"""
	Type to validate key value pairs.
	Unlike other types in argparse, this one validates different types.
	First it expects a value of type key followed by a value of type value.
	It needs to be reset to handle the next pair beginning with a key.
	"""
	def __init__(self):
		self.key_expected = True
		self.last_key = None

	def __call__(self, string):
		"""
		Called for each value.
		:param string:
		:return:
		"""
		if self.key_expected:
			self.key_expected = False
			self.last_key = string
			return self.verify_key(string)
		else:
			# self.key_expected = True
			return self.verify_val(string)

	def reset(self):
		"""
		resets its instance so that it can accept the next pair beginning with a key
		:return:
		"""
		self.key_expected = True
		self.last_key = None

	def verify_key(self, string):
		"""
		Tests if the given string is a valid key and tokenizes it.
		:param string: string read from command line
		:return: tokenized key as list
		"""
		arr = self._split_unescape(string)
		if len(arr) != len(filter(None, arr)):
			msg = "'{}' is not a valid key".format(string)
			raise argparse.ArgumentTypeError(msg)
		else:
			return arr

	def verify_val(self, string):
		"""
		Returns the value as it is.
		Can be overridden in inheriting classes.
		:param string:
		:return:
		"""
		return string

	@staticmethod
	def _split_unescape(s, delim=':', escape='\\', unescape=True):
		"""
		>>> split_unescape('foo,bar', ',')
		['foo', 'bar']
		>>> split_unescape('foo$,bar', ',', '$')
		['foo,bar']
		>>> split_unescape('foo$$,bar', ',', '$', unescape=True)
		['foo$', 'bar']
		>>> split_unescape('foo$$,bar', ',', '$', unescape=False)
		['foo$$', 'bar']
		>>> split_unescape('foo$', ',', '$', unescape=True)
		['foo$']
		from: https://stackoverflow.com/a/21882672/2631798
		"""
		ret = []
		current = []
		itr = iter(s)
		for ch in itr:
			if ch == escape:
				try:
					# skip the next character; it has been escaped!
					if not unescape:
						current.append(escape)
					current.append(next(itr))
				except StopIteration:
					if unescape:
						current.append(escape)
			elif ch == delim:
				# split! (add current to the list and reset it)
				ret.append(''.join(current))
				current = []
			else:
				current.append(ch)
		ret.append(''.join(current))
		return ret


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



def log_exception(msg='None', exit=True):
	print("{exc_type}: {exc_msg} ({f_name}:{l_num}) - Message: {msg}".format(
		exc_type=sys.exc_info()[0].__name__,
		exc_msg=sys.exc_info()[1],
		f_name=os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1],
		l_num=sys.exc_info()[2].tb_lineno,
		msg=msg
	))
	if exit:
		sys.exit(1)
