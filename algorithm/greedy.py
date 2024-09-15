from sys import argv
from numpy import max
from os.path import isfile
from json import load
from lib.topology import Topology, AntennaModel, Pylon, User, pathloss_oh, pathloss_fs, pathloss_simple
from lib.graph import WeightedGraph
from lib.util import dist2
from lib.arg_parser import parse_arguments
from lib.algorithms import greedy_allocation
from lib.writer import *

if __name__ == '__main__':
    args = parse_arguments(
        [
            ("--verbose", "Sets the verbosity of the program", None),
            ("--equipments", "Sets the JSON equipments file to read", str),
            ("--towers", "Sets the JSON towers file to read", str),
            ("--antennas", "Sets the JSON antenna models file to read", str),
            ("--pathloss", "Sets the pathloss model to use", str)
        ],
        argv,
        "== Python tool to visualize and build a network infracture =="
    )

    # Check the args
    if "--equipments" not in args:
        print("Missing --equipments argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--equipments"])
    if "--verbose" in args:
        print(f"Loading topology from {args['--topology']}...")

    if "--antennas" not in args:
        print("Missing --antennas argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--antennas"])
    if "--verbose" in args:
        print(f"Loading antenna models from {args['--antennas']}...")

    if "--towers" not in args:
        print("Missing --towers argument\nUse --help for more information about the usage of this program!")
        exit(0)
    assert isfile(args["--towers"])
    if "--verbose" in args:
        print(f"Loading towers from {args['--towers']}...")

    reset_output_files(["allocation.txt"])

    # Handle the pathloss arg
    pathloss = None
    if "--pathloss" in args:
        if args["--pathloss"].lower() == "oh":
            pathloss = pathloss_oh
        elif args["--pathloss"].lower() == "fs":
            pathloss = pathloss_fs
        elif args["--pathloss"].lower() == "simple":
            pathloss = pathloss_simple
        else:
            print("Invalid pathloss model, choose between 'oh', 'fs' or 'simple'!")
            exit(0)
    else:
        pathloss = pathloss_oh

    assert pathloss != None
    if "--verbose" in args:
        print(f"Using the {args['--pathloss']} pathloss model...")

    # Build the topology
    topo = Topology()

    topo.antennas = [
        AntennaModel(
            a["name"],
            a["power"],
            a["gain"],
            a["bandwidth"],
            a["frequency"],
            a["range"]
        )
        for a in load(open(args["--antennas"], "r"))
    ]
    topo.pylons = {
        (t["pos"]["x"], t["pos"]["y"]): Pylon(
            (t["pos"]["x"], t["pos"]["y"]),
            t["pos"]["h"],
            -1 # Antenna type has not been set yet
        )
        for t in load(open(args["--towers"], "r"))
    }
    topo.users = {
        (u["pos"]["x"], u["pos"]["y"]): User(
            (u["pos"]["x"], u["pos"]["y"]),
            None,# Unassociated user
            u["demand"]
        )
        for u in load(open(args["--equipments"], "r"))
    }

    # Build the network graph
    topo.graph = WeightedGraph()

    ## Add UEs to the graph
    for u in topo.users.keys():
        topo.graph.add_vertex(u, 0.)

    ## Add the edges to the graph and towers
    max_reach:float = max(list(map(lambda a: a.reach, topo.antennas)))

    for t in topo.pylons.keys():
        topo.graph.add_vertex(t, 0.)
        for u in topo.users.keys():
            d = dist2(t,u)
            if d <= max_reach:
                topo.graph.add_edge(t, u, d)

    # Run the greedy algorithm
    alloc = greedy_allocation(topo, pathloss)
    write_output(f"Placed antenna: type, remaining bandwidth/total available bandwidth\n", "allocation.txt")
    write_output(f"{alloc}\n", "allocation.txt")
