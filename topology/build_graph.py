from sys import argv
import json
import numpy as np
from datetime import datetime
from os import path
from os.path import isfile
from lib.graph import WeightedGraph
from lib.util import sample_users, dist2
from lib.arg_parser import parse_arguments


if __name__ == '__main__':
    args = parse_arguments(
        [
            ("--verbose", "Sets the verbosity of the program", None),
            ("--density", "Sets the JSON population density file to read", str),
            ("--antennas", "Sets the JSON antenna models file to read", str),
            ("--out", "Sets the output file to write the graph into", str)
        ],
        argv,
        "== Python tool create a network topology graph from JSON files =="
    )

    # Check input arguments
    ### POPULATION DENSITY GRID
    if "--density" not in args:
        print("Missing --density argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--density"])
    if "--verbose" in args:
        print(f"Loading topology from {args['--density']}...")
    ### ANTENNA MODELS
    if "--antennas" not in args:
        print("Missing --antennas argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--antennas"])
    if "--verbose" in args:
        print(f"Loading antenna models from {args['--antennas']}...")
    ### OUTPUT FILE
    out_file = args["--out"] if "--out" in args else path.join(path.dirname(__file__), f"output/{datetime.now().isoformat()}_graph.txt")
    print(out_file)#! DEBUG

    # Load the json files
    topo_json = json.load(open(args["--density"], "r"))
    antennas_json = json.load(open(args["--antennas"], "r"))

    # Read useful values
    height = topo_json["height"]
    width = topo_json["width"]
    tile_size = (topo_json["tile_size"]["x"], topo_json["tile_size"]["y"])
    user_demand = topo_json["user_demand"]
    density_grid = np.array(topo_json["density"])
    pylons = [ (pylon["pos"]["x"], pylon["pos"]["y"])
               for pylon in topo_json["pylons"] ]

    # Load the topology and the structure
    graph = WeightedGraph()
    users = []
    for x in range(width):
        for y in range(height):
            if density_grid[y][x] != 0:
                su = list(map(
                    lambda u: (x*tile_size[0] + u[0], y*tile_size[1] + u[1]),
                    sample_users(tile_size, density_grid[y][x])
                ))
                for u in su:
                    # Add an unassociated user to the graph with a bandwidth cost of 0 (indicating no association)
                    graph.add_vertex(u, 0.)
                users += su

    max_reach:float = np.max([ model["range"] for model in antennas_json ])

    for p in pylons:
        graph.add_vertex(p, 0.)
        for u in users:
            d = dist2(p,u)
            if d <= max_reach:
                graph.add_edge(p, u, d)

    # Export the graph
    with open(out_file, "w") as f:
        f.write(f"{graph}")
