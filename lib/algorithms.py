import numpy as np
from scipy.optimize import root_scalar
from lib.topology import Topology, pathloss_oh, Wcost, Wcost_prime
from lib.graph import WeightedGraph, WeightedEdge
from lib.writer import write_log
from lib.visualize import plot_allocated_bandwidth, plot_topology_allocation
from typing import Callable


def qos_density_graph(topo:Topology, p:tuple[float,float]) -> float:
    """Computes the QoS demand density for a given pylon in the topology.
    The formula is arbitrary.

    Parameters
    ----------
    topo
        Topology object.
    p
        Pylon to compute the density of.

    Returns
    -------
    Density value.
    """
    sum:float = 0.
    for e in topo.graph.edges[p]:
        sum += topo.users[e.v].demand / e.w
    return sum / len(topo.graph.edges[p])


def compute_W_allocation(topo:Topology, u:tuple[float,float], p:tuple[float,float], pathloss:Callable[[Topology, tuple[float,float], tuple[float,float]], float]) -> float:
    """TODO
    """
    Q = topo.users[u].demand
    PL = pathloss(topo, p, u)
    N0 = -174
    antenna = topo.antennas[topo.pylons[p].antenna_type]

    f = lambda x: Wcost(x, Q, N0, antenna.power + antenna.gain - PL)
    df = lambda x: Wcost_prime(x, Q)

    opt_res = root_scalar(f, fprime=df, x0=0.3/2*Q, bracket=[0.001, antenna.bandwidth])
    #opt_res = root_scalar(f, x0=0.3/2*Q, bracket=[0.001, antenna.bandwidth])

    if not opt_res.converged or opt_res.root < 0:
        print(f"ERROR WHEN CALLING THE SOLVER")
        write_log(f"ERROR WHEN CALLING THE SOLVER\n")
        write_log(f"{opt_res.flag}\n")
        return 0
    return opt_res.root


def get_closest_unallocated_ue(g:WeightedGraph, p:tuple[float,float]) -> WeightedEdge:
    """Get the closest unallocated user equipment from a given pylon.

    Parameters
    ----------
    g
        Graph object.
    p
        Pylon to consider.

    Returns
    -------
    Closest unallocated user equipment.
    """
    # Check if we still have edges to handle
    if g.edges[p] == []:
        return None
    # Skip already served user equipments by checking if the vertex already has allocated bandwidth
    e = g.edges[p][0]
    while g.vertices[e.v] != 0.:
        g.edges[p].pop(0)
        # Check if we still have edges to handle
        if g.edges[p] == []:
            return None
        e = g.edges[p][0]
    # Return the non empty edge
    return e


def greedy_eu_bandwidth_allocation(topo:Topology, p:tuple[float,float], model:int, pathloss:Callable[[Topology, tuple[float,float], tuple[float,float]], float]) -> float:
    """Given an antenna, allocate bandwidth greedily starting with the closest EU.

    Parameters
    ----------
    topo
        Topology object.
    p
        Pylon id that will allocate its bandwidth.
    model
        Antenna model id to use for the given pylon.

    Returns
    -------
    The unallocated bandwidth of the Base Station
    """
    # Set the antenna type and max bandwidth to allocate for the handled pylon
    topo.pylons[p].antenna_type = model
    Wmax = topo.antennas[model].bandwidth

    e = get_closest_unallocated_ue(topo.graph, p)
    if e == None:
        return Wmax
    Wc = compute_W_allocation(topo, e.v, p, pathloss)

    plot_allocated_bandwidth(topo, p, e.v)

    # While we have enough bandwidth to allocate
    while Wmax > Wc:
        write_log(f"Allocating {Wc:.2f}/{Wmax:.2f} Hz of bandwidth to {e.v}")
        Wmax -= Wc
        # Reverse the edge to keep the allocation information
        topo.users[e.v].pylon = p
        topo.graph.vertices[e.v] = Wc
        topo.graph.edges[p].pop(0)
        e = get_closest_unallocated_ue(topo.graph, p)
        if e == None:
            return Wmax
        Wc = compute_W_allocation(topo, e.v, p, pathloss)
    # Remove the remaining edges since the BS is already saturated
    topo.graph.edges[p] = []
    write_log(f"Can't allocate {Wc:.2f} Hz of bandwidth to {e.v}")# DEBUG
    return Wmax


def greedy_allocation(topo:Topology, pathloss:Callable[[Topology, tuple[float,float], tuple[float,float]], float]) -> dict[tuple[float,float],str]:
    """Greedy algorithm to allocate pylons to end users.

    Parameters
    ----------
    topo
        Topology object.

    Returns
    -------
    dict
        Pylons allocation.
    """
    # Compute the qos constraint density for each pylon
    # Simple formula : mean of all the qos constraints with all the neighbours
    pylons_density:dict[tuple[float,float], float] = {p: qos_density_graph(topo, p) for p in topo.pylons.keys()}
    write_log("--- Pylons' qos density ---")
    write_log(pylons_density)

    # Sort pylons by qos density
    sorted_pylons = sorted(pylons_density.items(), key=lambda x: x[1], reverse=True)
    write_log("--- Pylons sorted by qos density ---")
    write_log(sorted_pylons)

    antenna_model = 0 # Default 5G antenna model

    #left_bandwidth:float = greedy_eu_bandwidth_allocation(topo, sorted_pylons[0][0], antenna_model, True)
    #return {sorted_pylons[0][0]: (topo.antennas[antenna_model].name, left_bandwidth, topo.antennas[antenna_model].bandwidth)}

    for p in sorted_pylons:
        # Allocate and write the remaining bandwidth in the graph
        topo.graph.vertices[p[0]] = greedy_eu_bandwidth_allocation(topo, p[0], antenna_model, pathloss)
        plot_topology_allocation(topo)

    for ue in topo.users.values():
        if ue.pylon == None:
            print("Allocation was unsuccessful...")
            return {}

    # Print pylons information
    tmp_pylons_info = {p: 0 for p in topo.pylons.keys()}
    for u in topo.users.values():
        if u.pylon != None:
            tmp_pylons_info[u.pylon] += 1
    for p, pylon in topo.pylons.items():
        print(f"{p}: Serving {tmp_pylons_info[p]} users, {topo.antennas[pylon.antenna_type].bandwidth-topo.graph.vertices[p]:.2f}/{topo.antennas[pylon.antenna_type].bandwidth:.2f}")

    return {
        p: f"{topo.antennas[pylon.antenna_type].name}: Serving {tmp_pylons_info[p]} users, {topo.antennas[pylon.antenna_type].bandwidth-topo.graph.vertices[p]:.2f}/{topo.antennas[pylon.antenna_type].bandwidth:.2f}"
        for p, pylon in topo.pylons.items() }
