'''
    This file is part of Prolothar-Rule-Mining (More Info: https://github.com/shs-it/prolothar-rule-mining).

    Prolothar-Rule-Mining is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Prolothar-Rule-Mining is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Prolothar-Rule-Mining. If not, see <https://www.gnu.org/licenses/>.
'''
#import order is important!
import pathlib
from setuptools import setup, find_namespace_packages
from distutils.extension import Extension
from Cython.Build import cythonize
import os

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / "LICENSE").read_text()

with open(HERE / 'requirements.txt', 'r') as f:
    install_reqs = [
        s for s in [
            line.split('#', 1)[0].strip(' \t\n') for line in f
        ] if '==' in s
    ]

with open(HERE / 'version.txt', 'r') as f:
    version = f.read().strip()

def make_extension_from_pyx(path_to_pyx: str) -> Extension:
    return Extension(
        path_to_pyx.replace('/', '.').replace('.pyx', ''),
        sources=[path_to_pyx], language='c++')

if os.path.exists('prolothar_rule_mining/rule_miner/data_to_sequence/rules/mdl.pyx'):
    extensions = [
        make_extension_from_pyx("prolothar_rule_mining/rule_miner/data_to_sequence/rules/mdl.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/rule_miner/data_to_sequence/rules/rule.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/rule_miner/data_to_sequence/rules/list_of_rules.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/rule_miner/classification/rce/strategy/abstract.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/node.pyx"),
        #alignment
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/alignment/alignment_finder.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/alignment/a_star.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/alignment/path_enumeration.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/alignment/partial_alignment.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/alignment/alignment.pyx"),
        make_extension_from_pyx("prolothar_rule_mining/models/event_flow_graph/alignment/heuristics.pyx"),
        #conditions
        make_extension_from_pyx("prolothar_rule_mining/models/conditions.pyx"),
    ]
else:
    extensions = []

# This call to setup() does all the work
setup(
    name="prolothar-rule-mining",
    version=version,
    description="algorithms for prediction and rule mining on event sequences",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/shs-it/prolothar-rule-mining",
    author="Boris Wiegand",
    author_email="boris.wiegand@stahl-holding-saar.de",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_namespace_packages(
        include=['prolothar_rule_mining*']
    ),
    include_package_data=True,
    package_data={
        "prolothar_rule_mining": [
            '*','*/*','*/*/*','*/*/*/*','*/*/*/*/*',
            '*/*/*/*/*/*','*/*/*/*/*/*/*','*/*/*/*/*/*/*/*'
        ]
    },
    exclude_package_data={"": ['*.pyc']},
    ext_modules=cythonize(extensions, language_level = "3"),
    zip_safe=False,
    install_requires=install_reqs
)
