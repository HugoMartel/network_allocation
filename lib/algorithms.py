from lib.topology import Topology, AntennaModel
from lib.graph import WeightedGraph, WeightedEdge
from math import log10


def qos_density_graph(topo:Topology, p:tuple[float,float]) -> float:
    """Computes the QoS demand density for a given pylon in the topology.
    The formula is arbitrary.

    Parameters:
    topo -- Topology object.
    p    -- Pylon to compute the density of.

    Returns:
    float -- Density value.
    """
    sum:float = 0.
    for e in topo.graph.edges[p]:
        sum += topo.graph.vertices[e.v] / e.w
    return sum / len(topo.graph.edges[p])


def Wcost(topo:Topology, u:tuple[float,float], p:tuple[float,float]) -> float:
    """TODO
    """
    SNR = 10 # Signal to Noise Ratio, TODO
    return topo.graph.vertices[u] / log10(1 + SNR)


def get_closest_unallocated_ue(g:WeightedGraph, p:tuple[float,float]) -> WeightedEdge:
    """TODO
    """
    # Check if we still have edges to handle
    if g.edges[p] == []:
        return None
    # If there is an outgoing edge from e.v, then the ue is already served
    e = g.edges[p][0]
    while g.edges[e.v] != []:
        g.edges[p].pop(0)
        # Check if we still have edges to handle
        if g.edges[p] == []:
            return None
        e = g.edges[p][0]
    return e



def greedy_eu_bandwidth_allocation(topo:Topology, p:tuple[float,float], model: AntennaModel) -> float:
    """Given an antenna, allocate bandwidth greedily starting with the closest EU.

    Parameters:
    topo  -- Topology object.
    p     -- Pylon that will allocate its bandwidth.
    model -- Antenna model to use for the given pylon.

    Returns:
    The unallocated bandwidth of the Base Station
    """
    topo.pylons[p] = topo.antennas[model]
    Wmax = topo.antennas[model].bandwidth
    e = get_closest_unallocated_ue(topo.graph, p)
    if e == None:
        return Wmax
    Wc = Wcost(topo, e.v, p)

    # TODO: add a check if the vertex's contraint is already satisfied by another antenna

    while Wmax > Wc:
        Wmax -= Wc
        # Reverse the edge to keep the allocation information
        topo.users[e.v] = p
        topo.graph.edges[p].pop(0)
        e = get_closest_unallocated_ue(topo.graph, p)
        if e == None:
            return Wmax
        Wc = Wcost(topo, e.v, p)
    # Remove the remaining edges since the BS is already saturated
    topo.graph.edges[p] = []
    return Wmax


def greedy_allocation(topo:Topology) -> dict[tuple[float,float],str]:
    """Greedy algorithm to allocate pylons to end users.

    Parameters:
    topo -- Topology object.

    Returns:
    dict -- Pylons allocation.
    """
    # Compute the qos constraint density for each pylon
    # Simple formula : mean of all the qos constraints with all the neighbours
    pylons_density:dict[tuple[float,float], float] = {p: qos_density_graph(topo, p) for p in topo.pylons.keys()}
    print(pylons_density)

    # Sort pylons by qos density
    sorted_pylons = sorted(pylons_density.items(), key=lambda x: x[1], reverse=True)
    print(sorted_pylons)

    antenna_model = 0 # Default 5G antenna model

    left_bandwidth:float = greedy_eu_bandwidth_allocation(topo, sorted_pylons[0][0], antenna_model)
    return {sorted_pylons[0][0]: (topo.antennas[antenna_model].name, left_bandwidth)}
    #for p in sorted_pylons:
    #    greedy_eu_bandwidth_allocation(topo, p[0], antenna_model)

    # TODO: redo and rethink it
    #for u in topo.graph.vertices:
    #    if topo.graph.edges[u] != [] and u not in topo.pylons.keys():
    #        return []
    #return [ p for p,a in topo.pylons.items() if a != -1]

