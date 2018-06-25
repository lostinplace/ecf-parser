from setuptools import setup, find_packages

setup(
  name='ecf_parser',
  packages=find_packages(),
  entry_points={
    "console_scripts": [
        'ecf2json = ecf_parser.__init__:print_ecf2json',
        'json2ecf = ecf_parser.__init__:print_json2ecf'
    ]

  },
  version='0.1.3',
  description="Tools for parsing Empyrion's .ecf files",
  author='Chris Wheeler',
  author_email='cmwhee@gmail.com',
  url='https://github.com/lostinplace/ecf-parser',
  download_url='https://github.com/lostinplace/ecf-parser/archive/0.1.tar.gz', # I'll explain this in a second
  keywords=['empyrion', 'modding'],
  classifiers=[],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
  python_requires='>=3.6',

)