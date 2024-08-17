from lib.topology import Topology, AntennaModel, Pylon, User
from lib.visualize import plot_topology_density, plot_topology_graph, plot_measures
from numpy import arange

if __name__ == '__main__':

    # Create an empty topology
    topo = Topology()

    # Samples amount
    n = 1000
    min_dist = 10
    max_dist = 1000

    # Init the topology by hand for measures
    ## Create antennas
    topo.antennas.append(AntennaModel(# 5G Macro Cell values
        "5G Antenna",
        60,
        17,
        10e6,
        700e6,
        1000000# Huge range to always allow computing the throughput
    ))

    ## Create pylons
    topo.pylons[(0,0)] = Pylon((0,0), 30, 0)

    ## Create users
    topo.width = max_dist
    topo.height = 1
    topo.density_grid = [[1 for _ in range(max_dist)]]
    topo.users = {
        (x,0): User((x,0), (0,0), 1e6)
        for x in arange(min_dist, max_dist+1, (max_dist-min_dist)/n)
    }

    # Checking if the topology is correctly created
    plot_topology_density(topo)
    plot_topology_graph(topo)

    # Plot the different measurements
    plot_measures(topo)
