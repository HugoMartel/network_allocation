from sys import argv
from os.path import isfile
from lib.topology import Topology
from lib.visualize import plot_topology_allocation, plot_topology_density, plot_topology_graph
from lib.arg_parser import parse_arguments
from lib.algorithms import greedy_allocation
from lib.writer import *

if __name__ == '__main__':
    args = parse_arguments(
        [
            ("--topology", "Sets the topology file to read", str),
            ("--out", "Sets the output file to write to", str),
            ("--verbose", "Sets the verbosity of the program", None),
        ],
        argv,
        "== Python tool to visualize and build a network infracture =="
    )

    if ("--topology" not in args):
        print("Missing --topology argument\nUse --help for more information about the usage of this program!")
        exit(0)

    assert(isfile(args["--topology"]))

    reset_output_files(["allocation.txt"])

    # Load the topology and the structure
    topo = Topology(args["--topology"])
    plot_topology_density(topo)
    plot_topology_graph(topo)

    # Run the greedy algorithm
    alloc = greedy_allocation(topo)
    write_output(f"Placed antenna: type, remaining bandwidth/total available bandwidth\n", "allocation.txt")
    write_output(f"{alloc}\n", "allocation.txt")
