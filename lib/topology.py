import numpy as np
import json
from typing import Callable
from lib.graph import WeightedGraph
from lib.writer import write_log


def dist2(u:tuple[int,int], v:tuple[int,int]) -> float:
    """Euclidian distance between two points.

    Parameters
    ----------
    u
        First point.
    v
        Second point.

    Returns
    -------
    Distance between the two points.
    """
    return ((u[0]-v[0])**2 + (u[1]-v[1])**2)**0.5


def sample_users(tile_size:tuple[float,float], density:int) -> np.ndarray:
    """Sample end users in a tile from a given density.

    Parameters
    ----------
    tile_size
        Size of a tile in meters by coord.
    density
        Number of end users per tile.

    Returns
    -------
    List of sampled end users.
    """
    return np.dstack((np.random.uniform(0, tile_size[0], density), np.random.uniform(0, tile_size[1], density)))[0]


class AntennaModel:
    """Antenna model class to store the characteristics of an antenna."""

    name: str
    """Name of the antenna model."""
    power:float
    """Power of the antenna in dBm."""
    gain: float
    """Gain of the antenna in dBi."""
    bandwidth: float
    """Bandwidth of the antenna in Hz."""
    reach: float
    """Reach of the antenna in meters (range is a reserved keyword)."""

    def __init__(self, name:str, power:float, gain:float, bandwidth:float, reach:float):
        """Constructor of the AntennaModel class."""
        self.name = name
        self.power = power
        self.gain = gain
        self.bandwidth = bandwidth
        self.reach = reach


class Pylon:
    """Class to store the characteristics of a fixed pylon."""

    pos:tuple[float,float]
    """(x,y) Position of the pylon in meters."""
    height:float
    """Effective height of the pylon in meters."""
    antenna_type:int
    """Index of the antenna model used by the pylon."""

    def __init__(self, pos:tuple[float,float], height:float, antenna_type:int):
        """Constructor of the Pylon class."""
        self.pos = pos
        self.height = height
        self.antenna_type = antenna_type


class User:
    """Class to store the characteristics of an end user."""

    pos:tuple[float,float]
    """(x,y) Position of the user in meters."""
    pylon:tuple[float,float]|None
    """(x,y) Position of the pylon associated to the user or None."""
    demand:float
    """Bandwidth demand of the user in Hz."""

    def __init__(self, pos:tuple[float,float], pylon:tuple[float,float]|None, demand:float):
        """Constructor of the User class."""
        self.pos = pos
        self.pylon = pylon
        self.demand = demand


class Topology:
    """Topology class to store the network configuration.
    """

    width:int
    """X size of the density grid."""
    height:int
    """Y size of the density grid."""
    tile_size:tuple[float,float]
    """(X,Y) size in meters of a density grid tile."""
    user_demand:float
    """Demand of a user equipment in Hz."""
    density_grid:np.array
    """2-dimensional density grid of end users."""
    graph:WeightedGraph
    """Graph representation of the network."""
    users:dict[tuple[float,float], User]
    """Users position and their associated User."""
    pylons:dict[tuple[float,float], Pylon]
    """Pylons position and their associated Pylon."""
    antennas:list[AntennaModel]
    """List of available antennas models."""

    def __init__(self, filename:str):
        """Loads a json topology file into a Topology object.

        Arguments
        ---------
        filename
            File path to load.
        """
        # Load the json file
        topo_json = json.load(open(filename, "r"))

        # Load all the given JSON data
        self.height = topo_json["height"]
        self.width = topo_json["width"]
        self.tile_size = (topo_json["tile_size"]["x"], topo_json["tile_size"]["y"])
        self.user_demand = topo_json["user_demand"]
        self.density_grid = np.array(topo_json["density"])

        self.pylons = {
            (pylon["pos"]["x"], pylon["pos"]["y"]): Pylon((pylon["pos"]["x"], pylon["pos"]["y"]), pylon["pos"]["h"], -1)
              for pylon in topo_json["pylons"]}

        self.antennas = [
            AntennaModel(
                model["name"],
                model["power"],
                model["gain"],
                model["bandwidth"],
                model["range"]
            ) for model in topo_json["antennas"]
        ]

        # Build the graph and sample end users using the density grid
        self.graph = WeightedGraph()
        users = []
        for x in range(self.width):
            for y in range(self.height):
                if self.density_grid[y][x] != 0:
                    su = list(map(
                        lambda u: (x*self.tile_size[0] + u[0], y*self.tile_size[1] + u[1]),
                        sample_users(self.tile_size, self.density_grid[y][x])
                    ))
                    for u in su:
                        # Add an unassociated user to the graph with a bandwidth cost of 0 (indicating no association)
                        self.graph.add_vertex(u, 0.)
                    users += su

        # Add users and their associated pylons (None in the first place)
        self.users = {tuple(u): User(tuple(u), None, self.user_demand) for u in users}

        max_reach:float = np.max(list(map(lambda a: a.reach, self.antennas)))

        for p in self.pylons.keys():
            self.graph.add_vertex(p, 0.)
            for u in users:
                d = dist2(p,u)
                if d <= max_reach:
                    self.graph.add_edge(p, u, d)

        write_log(self.graph)


def pathloss_oh(topo:Topology, p:tuple[float,float], u:tuple[float,float]) -> float:
    """Okumura-Hata path loss model.

    Parameters:
    TODO

    Returns:
    Path loss value in decibels.
    """
    # f = 3500 # 3.5 GHz - 5G urban model IN MHz
    f = 1500 # 1.5GHz - max bound of the Okumura-Hata model IN MHz
    H = topo.pylons[p].height # Effective antenna height of the BS in meters (given by ARCEP2021)
    d = dist2(p,u) / 1000 # Convert distance between BS and UE to kilometers
    return 69.55 + 26.16*np.log10(f) - 13.82*np.log10(H) + (44.9 - 6.55*np.log10(H)) * np.log10(d)


def pathloss_fs(topo:Topology, p:tuple[float,float], u:tuple[float,float]) -> float:
    """Free Space Path Loss model.

    Parameters
    ----------
    topo
        Topology object.
    p
        Position of the BS.
    u
        Position of the UE.

    Returns
    -------
    Path loss value in decibels.
    """
    alpha = 3. # Path loss exponent in an urban environment
    # f = 3.5e9 # 3.5 GHz - ARCEP 5G urban model IN Hz
    f = 1.5e9 # 1.5 GHz - Okumura-Hata model upper bound IN Hz
    PL0 = 10*np.log10((4*np.pi*f)/(3*10**8))
    d = dist2(p,u) # Convert distance between BS and UE in meters
    return alpha * (PL0 + 10 * np.log10(d))


def pathloss_simple(topo:Topology, p:tuple[float,float], u:tuple[float,float]) -> float:
    """Simple path loss model.

    Parameters:
    TODO

    Returns:
    float -- Path loss value in decibels.
    """
    eta = 3. # Loss factor
    f = 1500 # 1.5 GHz - Okumura-Hata model upper bound IN MHz
    H = topo.pylons[p].height # Effective antenna height of the BS in meters (given by ARCEP2021)
    d = 1 # 1km
    PL0 = 69.55 + 26.16*np.log10(f) - 13.82*np.log10(H) + (44.9 - 6.55*np.log10(H)) * np.log10(d)
    return PL0 + eta*np.log10(dist2(p,u))


def snr(topo:Topology, p:tuple[int,int], u:tuple[int,int], pathloss:Callable[[Topology, tuple[float,float], tuple[float,float]], float]) -> float:
    """Signal to Noise Ratio (SNR) not taking interferences between BS into account.

    Parameters
    ----------
    topo
        Topology object.
    p
        Position of the BS.
    u
        Position of the UE.
    pathloss
        Path loss model to use.

    Returns
    -------
    Linear SNR value.
    """
    antenna = topo.antennas[topo.pylons[p].antenna_type]
    N0 = -174 # dBm/Hz
    SdB = antenna.power + antenna.gain - pathloss(topo, p,u)
    NdB = N0 + 10*np.log10(antenna.bandwidth)
    return np.power(10, (SdB - NdB)/10)


def Wsimple(x:float, C:float, N0:float, S:float) -> float:
    """TODO

    Parameters
    ----------
    x
        Bandwidth to allocate in Hz.
    C
        User equipment demand in bits per second.
    N0
        Noise density in dBm/Hz.
    S
        Signal power in dB.

    Returns
    -------
    Cost value with static allocated BS bandwidth
    """
    W = 10e6
    return 10*np.log10(W*(np.power(2., C/x) - 1.)) - S + N0


def Wlimit(C:float, N0:float, S:float) -> float:
    """Compute the limit at infinity of the cost function.

    Parameters
    ----------
    C
        User equipment demand in bits per second.
    N0
        Noise density in dBm/Hz.
    S
        Signal power in dB.

    Returns
    -------
    Limit value.
    """
    return 10*np.log10(C*np.log(2)) - S + N0


def Wcost(w:float, C:float, N0:float, S:float) -> float:
    """Compute the cost function for given topology parameters.

    Parameters
    ----------
    w
        Bandwidth to allocate in Hz.
    C
        User equipment demand in bits per second.
    N0
        Noise density in dBm/Hz.
    S
        Signal power in dB.

    Returns
    -------
    Cost value.
    """
    print(f"CALL f({w})")
    return 10*np.log10(w*(np.power(2, C/w) - 1)) - S + N0


def Wcost_prime(w:float, C:float, N0:float, S:float) -> float:
    """Compute the derivative of the cost function for given topology parameters.

    Parameters
    ----------
    w
        Bandwidth to allocate in Hz.
    C
        User equipment demand in bits per second.
    N0
        Noise density in dBm/Hz.
    S
        Signal power in dB.

    Returns
    -------
    Derivative of the cost function.
    """
    return 10/np.log(10) * ( 1/w - C*np.log(2) / (w*w) * ( 1 + 1 / (np.power(2, C/w) - 1)) )
