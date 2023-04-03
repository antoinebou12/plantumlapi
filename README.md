# PyPlantuml

Python interface with the PlantUML web. PlantUML is a library for generating UML diagrams from a simple text markup language. 

Python-PlantUML is a simple remote client interface to a PlantUML server using the same custom encoding used by most other PlantUML clients. 

This client defaults to the public PlantUML server but can be used against any server. 

## Installation

To install, run the following command:

```bash
pip install pyplantuml
```

```bash
pip install git+https://github.com/antoinebou12/py-plantuml
```

## Command Line Usage

```bash
usage: plantuml.py [-h] [-o OUT] [-s SERVER] filename [filename ...]

Generate images from PlantUML defined files using PlantUML server

positional arguments: 
  filename            file(s) to generate images from

optional arguments: 
  -h, --help          show this help message and exit 
  -o OUT, --out OUT   directory to put the files into 
  -s SERVER, --server SERVER 
                      server to generate from; defaults to plantuml.com 
```

