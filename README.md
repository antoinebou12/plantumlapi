# py-plantuml
Python interface with the  plantuml web
PlantUML is a library for generating UML diagrams from a simple text markup language.
Python-PlantUML is a simple remote client interface to a PlantUML server using the same custom encoding used by most other PlantUML clients.
Python was missing from the list, and while there are other PlantUML Python libraries like sphinxcontrib-plantuml, they require downloading and installing the Java executable and spawning shell subprocesses.

https://github.com/dougn/python-plantuml

This client defaults to the public PlantUML server but can be used against any server. To install, run the following command:

bash
Copy code
pip install git+https://github.com/antoinebou12/py-plantuml
Note that at some point, this newer version will be uploaded to PyPI, at which point you can simply use the command:

Copy code
pip install py-plantuml

Command line help:

vbnet
Copy code
usage: plantuml.py [-h] [-o OUT] [-s SERVER] filename [filename ...]

Generate images from PlantUML defined files using PlantUML server

positional arguments:
  filename              file(s) to generate images from

optional arguments:
  -h, --help            show this help message and exit
  -o OUT, --out OUT     directory to put the files into
  -s SERVER, --server SERVER
                        server to generate from; defaults to plantuml.com
Project Links:

Documentation
- PyPI
- GitHub
