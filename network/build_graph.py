from io import TextIOWrapper
from sys import argv
import json
import numpy as np
from datetime import datetime
from math import log10
from os.path import isfile, join, dirname
from lib.graph import WeightedGraph, WeightedEdge
from lib.util import  dist2
from lib.arg_parser import parse_arguments


if __name__ == '__main__':
    args = parse_arguments(
        [
            ("--verbose", "Sets the verbosity of the program", None),
            ("--equipments", "Sets the JSON user equipments file to read", str),
            ("--towers", "Sets the JSON towers file to read", str),
            ("--antennas", "Sets the JSON antenna models file to read", str),
            ("--out", "Sets the output file to write the graph into", str)
        ],
        argv,
        "== Python tool create a network graph from JSON files =="
    )

    # Check input arguments
    ### USER EQUIPMENTS LOCATIONS AND DEMAND
    if "--equipments" not in args:
        print("Missing --equipments argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--equipments"])
    if "--verbose" in args:
        print(f"Loading user-equipments from {args['--equipments']}...")
    ### TOWERS LOCATIONS
    if "--towers" not in args:
        print("Missing --towers argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--towers"])
    if "--verbose" in args:
        print(f"Loading towers from {args['--towers']}...")
    ### ANTENNA MODELS
    if "--antennas" not in args:
        print("Missing --antennas argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--antennas"])
    if "--verbose" in args:
        print(f"Loading antenna models from {args['--antennas']}...")
    ### OUTPUT FILE
    out_file = args["--out"] if "--out" in args else join(dirname(__file__), f"output/{datetime.now().isoformat()}_graph.txt")
    print(out_file)#! DEBUG

    # Load the json files
    equipments_json:list[object] = json.load(open(args["--equipments"], "r"))
    towers_json:list[object]     = json.load(open(args["--towers"], "r"))
    antennas_json:list[object]   = json.load(open(args["--antennas"], "r"))

    # Create the graph
    graph = WeightedGraph()

    # Open the output file
    f:TextIOWrapper = open(out_file, "w")

    # Create the user-equipments nodes
    users:list[tuple[float,float]] = []
    for ue in equipments_json:
        pos = (ue['pos']['x'], ue['pos']['y'])
        qos = ue['demand']
        graph.add_vertex(pos, qos)
        users.append(pos)

    # Export user nodes
    f.write(f"{graph}")

    if "--verbose" in args:
        print(f"Wrote {len(users)} weighted nodes for UEs")

    # Create the towers nodes
    max_reach:float = np.max([ model["range"] for model in antennas_json ])

    # Verbose variables
    i=1
    towers_len:int = len(towers_json)
    towers_log:int = int(log10(towers_len)+1)
    users_len:int = len(users)
    users_log:int = int(log10(users_len)+1)

    if "--verbose" in args:
        print(f"\rAdding towers vertices ({i:{towers_log}}/{towers_len}) - ({0:{users_log}}/{users_len})", end='')
    for tower in towers_json:
        t = (tower['pos']['x'], tower['pos']['y'])
        graph.add_vertex(t, 0.)# weight is for the allocated bandwidth
        if "--verbose" in args:
            print(f"\rAdding towers vertices ({i:{towers_log}}/{towers_len}) - ({0:{users_log}}/{users_len})", end='')
        # Export tower node and its edges
        f.write(f"{t} ({0.}):\n")
        for j,u in enumerate(users):
            d = dist2(t, u)
            if d <= max_reach:
                f.write(f"  {WeightedEdge(t, u, 0.)}\n")
                # graph.add_edge(t, u, d)
                if "--verbose" in args:
                    print(f"\rAdding towers vertices ({i:{towers_log}}/{towers_len}) - ({j:{users_log}}/{users_len})", end='')

        # Remove added tower from the graph object to reduce memory usage

        i+=1
    if "--verbose" in args:
        print('')

    if "--verbose" in args:
        print(f"Wrote {towers_len} weighted nodes for BSs")
        print(f"Wrote {towers_len*users_len} weighted edges")

    # Export the graph
    # with open(out_file, "w") as f:
    #     f.write(f"{graph}")
    #     print(f"Wrote graph file to {out_file}")
