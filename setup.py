from setuptools import setup, find_packages
import os

# execfile('yaml_cli/version.py')

def params():
	name = 'yaml_cli'
	
	# Get the version from a VERSION file
	version_file = open(os.path.join("./", 'VERSION'))
	version = version_file.read().strip()

	description = "A command line interface to read and manipulate YAML files. Based on python, distributed as pip."
	author = "Andy Werner"
	author_email = "andy@mr-beam.org"
	url = "https://github.com/Gallore/yaml_cli"
	license = 'MIT License'

	packages = find_packages()
	zip_safe = True # http://peak.telecommunity.com/DevCenter/setuptools#setting-the-zip-safe-flag

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