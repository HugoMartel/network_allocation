# Network Allocation

This project was started for an internship in the LIP CS laboratory at ENS de Lyon in France. The projects consists of building a model and an algorithm to be able to decide when given towers locations, UEs locations and available antenna models as input if building a cellular network with those constraints was possible and possibly to find a 'good' infrastructure deployment!


## Installation

You need a few `python` dependencies to be able to run the different scripts and parts of the project

`pip install -r requirements.txt`

Or install each dependency only when you need it.

You will also need the command `wget` if you want to run the `init_lyon_data.sh` script.


## Usage

Example:
```sh
python -m algorithm.greedy --equipments data/equipments/toy.json --towers data/towers/toy.json --antennas data/antennas/default.json --pathloss fs
```

To get a list of available options, a `--help` is available for each python program accepting 2 or more arguments.

---

A shell script is available to retrieve everything from the internet and to prepare everything as JSON files to be ready to start actually using the Python code for the model and algorithm.

```sh
./init_lyon_data.sh
```

## Project organisation

Each part is independent and only linked with a `lib` folder containing the main computation codes and the cellular network model stuff. Most python files can either be run as a script or as a library to import functions from.

### Network

Loads a bunch of JSON files to create a network graph that can then be used for the bandwidth allocation algorithm as a structure

### Algorithm

Actual bandwidth allocation algorithms

### Visualization

Contains multiple scripts and functions used to generate plots and test parts of the code!

### Loaders

These scripts enable us to load data from the various databases files from ARCEP, ANFR and INSEE, to query them and to convert the results into JSON files (in the `data` folder).

### Data

Contains the JSONs that can be used as input for the different parts of the project.
