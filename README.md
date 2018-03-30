# ECF Parser

## FAQ

### What is this?

The empyrion config files are really hard to work with because they're in a custom format, so I wrote a parser/generator to help work with them.  It includes a very limited object model which is really just an "Entry" to help you work with it in python.

### How do I use it?

Install with pip and use the command line, or use the utility functions as part of the package.

```bash

➜  pip install ecf_parser
Collecting ecf_parser
  Downloading ecf_parser-0.1.1.tar.gz
Building wheels for collected packages: ecf-parser
  Running setup.py bdist_wheel for ecf-parser ... done
  Stored in directory: /home/lostinplace/.cache/pip/wheels/75/bb/a2/2369889367dd61fba9303e98a0c006e9d2868c6368d305c027
Successfully built ecf-parser
Installing collected packages: ecf-parser
Successfully installed ecf-parser-0.1.2
➜  ecf2json Content/Configuration/Config_Example.ecf

```

Note that the command `json2ecf` is also available

### Do I have to run it?

Nope, I've included the json export of the example config in the sample dat folder in this repo
