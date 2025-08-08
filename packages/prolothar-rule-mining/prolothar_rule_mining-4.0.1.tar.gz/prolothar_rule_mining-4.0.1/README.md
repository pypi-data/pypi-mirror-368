# Prolothar Rule Mining

Algorithms to learn classification and event sequence prediction rules for event sequence datasets such as process logs.

Based on the publication
> Boris Wiegand, Dietrich Klakow, and Jilles Vreeken.
> **Discovering Interpretable Data-to-Sequence Generators.**
> In: *Proceedings of the 36th AAAI Conference on Artificial Intelligence (AAAI), Virtual Event.* 2022, pp. 4237–4244.

## Prerequisites

Python 3.11+

## Usage

If you want to run the algorithms on your own data, follow the steps below.

### Installing

```bash
pip install prolothar-rule-mining
```

### Creating or reading a dataset of sequences with metadata

You can create datasets manually by

```python
from prolothar_common.models.dataset import TargetSequenceDataset
from prolothar_common.models.dataset.instance import TargetSequenceInstance

#define a list of categorical variables and a list of numeric variables
dataset = TargetSequenceDataset(['color'],['size'])

# add instances, where each instance has three parts:
# 1. a unique hashable ID (e.g. of type int or str)
# 2. a dictionary with attribute names and attribute values
# 3. a (potentially empty) list or tuple of events of type str
dataset.add_instance(TargetSequenceInstance(
    1, {'color': 'red', 'size': 100}, []
))
dataset.add_instance(TargetSequenceInstance(
    2, {'color': 'blue', 'size': 42}, ['A', 'B']
))
```

Alternatively, you can read a dataset from an .arff file:

```python
from prolothar_common.models.dataset import TargetSequenceDataset

with open('dataset.arff', 'r') as f:
   dataset = TargetSequenceDataset.create_from_arff(f.read(), 'sequence')
```

Exemplary .arff file:

```
@RELATION "TestDataset"

@ATTRIBUTE "color" {"blue","red"}
@ATTRIBUTE "size" NUMERIC
@ATTRIBUTE "sequence" {"[]","[A,B]"}

@DATA
"red",100,"[]"
"blue",42,"[A,B]"
```

### Discovering an Event-flow Graph Using ConSequence

```python
from prolothar_rule_mining.rule_miner.data_to_sequence.consequence import ConSequence

consequence = ConSequence()
rules_model = consequence.mine_rules(dataset)

#make predictions
for instance in dataset:
    print('=================')
    print(instance.get_target_sequence())
    print(rules_model.execute(instance))

#get and print the event flow graph
graph = rules_model.get_event_flow_graph()
graph.plot()
graph.plot(view=False, filepath='path_to_pdf')

#get and print the classification rule at each node
for node, router in rules_model.get_node_router_table().items():
    print('===============================')
    print(f'rule at node {node}')
    print(router.get_rule())
    # alternative: print(router.get_rule().to_html())
```

## Development

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Additional Prerequisites
- make (optional)

### Compile Cython code

```bash
make cython
```

### Running the tests

```bash
make test
```

### Deployment

1. Change the version in version.txt
2. Build and publish the package on pypi by
```bash
make clean_package
make package && make publish
```
3. Create and push a tag for this version by
```bash
git tag -a [version] -m "describe this version"
git push --tags
```

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

If you have any questions, feel free to ask one of our authors:

* **Boris Wiegand** - boris.wiegand@stahl-holding-saar.de
