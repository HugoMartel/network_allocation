from lib.topology import Topology, WeightedGridGraph
import numpy as np
from bisect import insort
from math import log10

def qos_density_grid(grid:np.array, x:int, y:int) -> float:
    min_y,min_x = 0,0
    max_y,max_x = grid.shape
    qos_sum:float = grid[x][y]
    if x != min_x:
        qos_sum += grid[x-1][y]
        if y != min_y:
            qos_sum += grid[x-1][y-1]
        if y != max_y:
            qos_sum += grid[x-1][y+1]
    if x != max_x:
        qos_sum += grid[x+1][y]
        if y != min_y:
            qos_sum += grid[x+1][y-1]
        if y != max_y:
            qos_sum += grid[x+1][y+1]
    if y != min_y:
        qos_sum += grid[x][y-1]
    if y != max_y:
        qos_sum += grid[x][y+1]
    return qos_sum / 8.


def qos_density_graph(topo:Topology, g:WeightedGridGraph, x:int, y:int) -> float:
    sum:float = 0.
    for e in g.edges[(x,y)]:
        sum += topo.grid[e.v] / e.w
    return sum / len(g.edges[(x,y)])


def Wcost(grid:np.array, u:tuple[int,int], p:tuple[int,int]) -> float:
    SNR = 10 # Signal to Noise Ratio, TODO
    return grid[u[0]][u[1]] / log10(1 + SNR)


def greedy_allocation(topo:Topology) -> dict[tuple[int,int],str]:
    """Greedy algorithm to allocate pylons to end users.

    Parameters:
    topo -- Topology object.

    Returns:
    dict -- Pylons allocation.
    """
    # Build the weighted grid graph associated to the given topology
    g:WeightedGridGraph = WeightedGridGraph(topo.grid, list(topo.pylons.keys()))
    print(g)

    # Compute the qos constraint density for each pylon
    # Simple formula : mean of all the qos constraints with all the neighbours
    pylons_density:dict[tuple[int,int], float] = {(x,y): qos_density_graph(topo, g, x, y) for (x,y) in topo.pylons.keys()}
    print(pylons_density)

    # Sort pylons by qos density
    sorted_pylons = sorted(pylons_density.items(), key=lambda x: x[1], reverse=True)
    print(sorted_pylons)

    antenna_model = 0 # Default 5G antenna model

    for p in sorted_pylons:
        topo.pylons[p[0]] = topo.antennas[antenna_model]
        Wmax = topo.antennas[antenna_model].bandwidth
        u = g.edges[p[0]][0].v
        Wc = Wcost(topo.grid, u, p)

        while Wmax > Wc:
            Wmax -= Wc
            g.edges[u] = []
            g.edges[p[0]].pop(0)
            u = g.edges[p[0]][0].v
            Wc = Wcost(topo.grid, u, p[0])

    for u in g.vertices:
        if g.edges[u] != [] and u not in topo.pylons.keys():
            return []
    return [ p for p,a in topo.pylons.items() if a != -1]

