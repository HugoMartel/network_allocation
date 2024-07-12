from sys import argv
from os.path import isfile
from lib.topology import Topology, pathloss_oh, pathloss_fs, pathloss_simple
from lib.visualize import plot_topology_allocation, plot_topology_density, plot_topology_graph
from lib.arg_parser import parse_arguments
from lib.algorithms import greedy_allocation
from lib.writer import *

if __name__ == '__main__':
    args = parse_arguments(
        [
            ("--verbose", "Sets the verbosity of the program", None),
            ("--topology", "Sets the JSON topology file to read", str),
            ("--antennas", "Sets the JSON antenna models file to read", str),
            ("--pathloss", "Sets the pathloss model to use", str)
        ],
        argv,
        "== Python tool to visualize and build a network infracture =="
    )

    # Handle the topology arg
    if "--topology" not in args:
        print("Missing --topology argument\nUse --help for more information about the usage of this program!")
        exit(0)

    assert isfile(args["--topology"])
    if "--verbose" in args:
        print(f"Loading topology from {args['--topology']}...")

    assert isfile(args["--antennas"])
    if "--verbose" in args:
        print(f"Loading antenna models from {args['--antennas']}...")

    reset_output_files(["allocation.txt"])

    # Load the topology and the structure
    topo = Topology(args["--topology"], args["--antennas"])
    plot_topology_density(topo)
    plot_topology_graph(topo)

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

    # Run the greedy algorithm
    alloc = greedy_allocation(topo, pathloss)
    write_output(f"Placed antenna: type, remaining bandwidth/total available bandwidth\n", "allocation.txt")
    write_output(f"{alloc}\n", "allocation.txt")
