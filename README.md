# PyMaJORME

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/hyperium/hyper/master/LICENSE)
[![Python version](https://img.shields.io/badge/python-3.4-orange.svg)](https://www.python.org/)

PyMaJORME is an acronyme for **Py**thon **Ma**kes **J**ava **O**bject-**R**elational **M**apping **E**asy.

The idea behind this project is to provide an environment to a developer for faster and bugfree developing of ORM layer for Java applications. As this job can be very annoying when implementing in Java from scratch, idea for this project came along. Who says that no good things come out from using Java. :)

PyMaJORME is an easy to use python tool based on DSLs for generating ORM layer for Java applications. It is implemented entirely in Python and provides specifically created DSL for describing Java entities and their relations. Then, entire ORM layer with model classes using appropriate JPA annotations, and optionally DAO layer, can be generated along with necessary configuration files.

This project is also used as a final project for *Domain Specific Languages* course taught by Prof. [Igor Dejanović](https://github.com/igordejanovic "Igor Dejanović's GitHub profile") on master studies at *Software Engineering and Informational Technologies* study programme at Faculty of Technical Sciences, University of Novi Sad, Serbia.

PyMaJORME is written in [Python v3.4](https://www.python.org "Official Python page"). DSL is built using [Arpeggio](https://github.com/igordejanovic/Arpeggio "Arpeggio GitHub page") and [TextX](https://github.com/igordejanovic/textX "TextX GitHub page") frameworks for language specification. It also uses [Jinja2](https://github.com/mitsuhiko/jinja2 "Jinja 2 GitHub page") for generating output Java code.

# Installation

git clone the repository: `git clone https://github.com/danielkupco/PyMaJORME.git`

In the repository's home directory (.../PyMaJORMe/pymajorme) run: `pip install .`

And you should have your pymajorme installed as a Python package. :)
Run `pymajorme --help` to see the usage of program. You can use code in "examples" directory to test it out.

# Basic DSL usage

It should be seen from "examples/entities.jorm" file, but basic two types of DSL are entity and a relation. Relation must use previously defined entities. It is possible to define aditional JPA attributes along with entity/relation, such as cascade type, or an id.

### Authors:
* [Daniel Kupčo](https://github.com/danielkupco "Daniel Kupčo's GitHub profile")
* [Rade Radišić](https://github.com/RadeKornjaca "Rade Radišić's GitHub profile")
