# Python Bindings for DisjointForest

This directory contains Python bindings for the C++ DisjointForest library using pybind11.

## Features

- **Node**: Python wrapper for any Python object
- **DisjointForest**: Single class that works with any Python object type
- **Type Flexibility**: Can handle integers, strings, lists, dictionaries, custom objects, etc.

## Requirements

- Python 3.6+
- pybind11
- setuptools

## Installation

### Automatic (recommended)
From the main project directory:
```bash
make python-bindings
```

### Manual
```bash
cd python
pip install -r requirements.txt
python setup.py build_ext --inplace
```

## Usage

```python
import disjoint_forest

# Create a forest for any Python objects
forest = disjoint_forest.DisjointForest(10)

# Create some sets
node1 = forest.make_set(42)
node2 = forest.make_set("hello")
node3 = forest.make_set([1, 2, 3])

# Union the sets
forest.union_sets(node1, node2)

# Find the representative
rep = forest.find(node1)
print(f"Representative: {rep.data}")

# Check if they're in the same set
same_set = forest.find(node1) == forest.find(node2)
print(f"Same set: {same_set}")
```

## Available Methods

### DisjointForest

- `make_set(data)`: Create a new set with the given data
- `find(node)`: Find the representative of the set containing the node
- `union_sets(node1, node2)`: Union two sets
- `expand(additional_capacity)`: Increase the forest's capacity
- `contract(node)`: Remove a node from the forest
- `clear()`: Remove all nodes
- `size()`: Get the current number of nodes
- `capacity()`: Get the current capacity
- `is_empty()`: Check if the forest is empty
- `get_all_nodes()`: Get a list of all nodes
- `get_all_data()`: Get a list of all data values from nodes

## Union Operators

The `DisjointForest` class supports Python's union operators for combining forests:

### `|` Operator (Union)
Creates a new forest containing all nodes from both forests:
```python
forest1 = disjoint_forest.DisjointForest()
forest1.make_set("A")
forest1.make_set("B")

forest2 = disjoint_forest.DisjointForest()
forest2.make_set("C")
forest2.make_set("D")

# Create union forest
union_forest = forest1 | forest2
print(union_forest.get_all_data())  # ['A', 'B', 'C', 'D']
```

### `|=` Operator (In-place Union)
Adds all nodes from the second forest to the first forest:
```python
forest1 |= forest2
print(forest1.get_all_data())  # ['A', 'B', 'C', 'D']
```

**Note**: The union operators create forests with all nodes but do not preserve the union relationships between nodes. They are useful for combining collections of data rather than merging set structures.

## Examples

Run the included example:
```bash
make python-example
```

Or manually:
```bash
cd python
python example.py
```

## Building

The Python module is built as a shared library (`.so` on Linux, `.pyd` on Windows) that can be imported directly in Python.

## Testing

Test that the bindings work:
```bash
make python-test
```

## Cleanup

Remove build artifacts:
```bash
make clean  # From main directory
# or
cd python && make clean
``` 