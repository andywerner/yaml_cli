from setuptools import setup, find_packages

exec(compile(open('yaml_cli/version.py', "rb").read(), 'yaml_cli/version.py', 'exec'))

def params():
	name = 'yaml_cli'  # This is the name of your PyPI-package.
	version = __version__
	# scripts = ['helloworld']  # The name of your scipt, and also the command you'll be using for calling it
	description = "A command line interface to read and manipulate YAML files. Based on python, distributed as pip."
	author = "Andy Werner"
	author_email = "andy@mr-beam.org"
	url = "https://github.com/Gallore/yaml_cli"
	# license = "proprietary"

	packages = find_packages()
	zip_safe = False # ?

	install_requires = [
		"PyYAML",
		"argparse"
	]

	entry_points = {
		"console_scripts": {
			"yaml_cli = yaml_cli.__init__:run"
		}
	}

	# non python files need to be specified in MANIFEST.in
	include_package_data = True

	return locals()

setup(**params())
