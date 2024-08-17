# Network Allocation

TODO: description

## Installation

You need a few `python` dependencies to be able to run the different scripts and parts of the project

`pip install -r requirements.txt`

Or install each dependency only when you need it.

You will also need the command `wget` if you want to run the `init_lyon_data.sh` script.


## Usage

Example:
```sh
python topology/build_graph.py --verbose --density ./data/topology/toy.json --antennas ./data/antennas/default.json --pathloss fs
```

To get a list of available options, a `--help` is available for each python program accepting 2 or more arguments.


## Project organisation

### Topology

Loads a bunch of JSON files to create a topology graph that can then be used for the bandwidth allocation algorithm

### Algorithm

Actual bandwidth allocation algorithm that takes a topology graph and antennas models in input to output an allocation for the network.

### Visualization

Contains multiple scripts used to generate plots and test parts of the code!

