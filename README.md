# yaml_cli
A command line interface to read and manipulate YAML files. Based on python, distributed as pip.

## Installation

```
git clone https://github.com/Gallore/yaml_cli
cd yaml_cli
pip install .
```


## Examples

How to set a key:

```bash
> yaml_cli -s key:subkey value
key:
  subkey: value
```

Support of different data types:

```bash
> yaml_cli \
    -n andy:test:number 5 \                             # number value
    -b andy:test:bolean_value true \                    # boolean value
    -s andy:test:a_string 'Text with whitespaces' \     # string value
    -l andy:test:basic_list_support item1 and2 and3 \   # list value
    --null andy:test:null_value                         # null value
andy:
  test:
    a_string: Text with whitespaces
    basic_list_support:
    - item1
    - and2
    - and3
    bolean_value: true
    null_value: null
    number: 5
```

Delete keys:
```bash
> yaml_cli 
    -s andy:subkey_one foo 
    -s andy:subkey_two will_be_deleted                  # add key andy:subkey_two ... 
    -d andy:subkey_two                                  # ... rend removing it again
andy:
  subkey_one: foo
  ```
  
  
## Usage

```text
usage: yaml_cli [-h] [-i INPUT] [-o OUTPUT] [-d KEY] [-s KEY VAL] [-n KEY VAL]
                [-b KEY VAL] [-l KEY [VAL ...]] [--null KEY] [--version] [-v]
                [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        YAML file to load. Of not provided an empty YAML will
                        be the base for all operations.
  -o OUTPUT, --output OUTPUT
                        Output file. If not provided output is written to
                        STDOUT
  -d KEY, --delete KEY  Delete key: mykey:subkey:subkey. Skipped silently if
                        key doesn't exist.
  -s KEY VAL, --string KEY VAL
                        Set key with string value: mykey:subkey:subkey 'my
                        value'
  -n KEY VAL, --number KEY VAL
                        Set key with number value: mykey:subkey:subkey 3.7
  -b KEY VAL, --boolean KEY VAL
                        Set key with number value: mykey:subkey:subkey true
                        (possible values: ('1', 'true', 'True', 'yes') ('',
                        '0', 'false', 'False', 'no'))
  -l KEY [VAL ...], --list KEY [VAL ...]
                        Set key with value as list of strings:
                        mykey:subkey:subkey intem1 intem2 intem3
  --null KEY            Set key with null value: mykey:subkey:subkey
  --version             show program's version number and exit
  -v, --verbose         Verbose output
  --debug               Debug output
```
  
  
  
  
  
  
  