import numpy as np
import json
from lib.graph import WeightedGraph
from math import log10


def dist2(u:tuple[int,int], v:tuple[int,int]) -> float:
    return np.sqrt((u[0]-v[0])**2 + (u[1]-v[1])**2)


def sample_users(tile_size:tuple[float,float], density:int) -> np.ndarray:
    """Sample end users in a tile from a given density.

    Parameters:
    tile_size -- Size of a tile in meters by coord.
    density -- Number of end users per tile.

    Returns:
    List of sampled end users.
    """
    return np.dstack((np.random.uniform(0, tile_size[0], density), np.random.uniform(0, tile_size[1], density)))[0]


class AntennaModel:
    name: str
    power:float
    gain: float
    bandwidth: float
    reach: float # range is a reserved keyword
    alpha: float

    def __init__(self, name:str, power:float, gain:float, bandwidth:float, reach:float, alpha:float):
        self.name = name
        self.power = power
        self.gain = gain
        self.bandwidth = bandwidth
        self.reach = reach
        self.alpha = alpha


class Topology:
    height:int
    width:int
    tile_size:tuple[float,float] # in meters
    density_grid:np.array # dim 2 array
    graph:WeightedGraph
    users:dict[tuple[float,float], tuple[float,float]|None]
    pylons:dict[tuple[float,float], int]
    antennas:list[AntennaModel]

    # Constants
    user_demand:float = 1e6 # Constant demand across all end users
    shadowing:float = 1.0 # TODO: check usefullness
    loss_factor:float = 1.0 # TODO: check

    def __init__(self, filename:str):
        """Loads a json topology file into a Topology object.

        Parameters:
        filename -- File path to load.
        """
        # Load the json file
        topo_json = json.load(open(filename, "r"))

        # Load all the given JSON data
        self.height = topo_json["height"]
        self.width = topo_json["width"]
        self.tile_size = (topo_json["tile_size"], topo_json["tile_size"])
        self.user_demand = topo_json["user_demand"]
        self.density_grid = np.array(topo_json["density"])

        self.pylons = {(pylon["pos"]["x"]*self.tile_size[0], pylon["pos"]["y"]*self.tile_size[1]): -1 for pylon in topo_json["pylons"]}

        self.antennas = [
            AntennaModel(
                model["name"],
                model["power"],
                model["gain"],
                model["bandwidth"],
                model["range"],
                .5# Alpha, TODO
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
                        self.graph.add_vertex(u, self.user_demand)
                    users += su

        # Add users and their associated pylons (None in the first place)
        self.users = {tuple(u): None for u in users}

        max_reach:float = np.max(list(map(lambda a: a.reach, self.antennas)))

        for p in self.pylons.keys():
            self.graph.add_vertex(p, 0.)
            for u in users:
                d = dist2(p,u)
                if d <= max_reach:
                    self.graph.add_edge(p, u, d)

        print(self.graph)

# TODO: check everything
def gain(topo:Topology, p:tuple[int,int], u:tuple[int,int]) -> float:
    """Gain received by the end user at position u from the pylon at position p.

    TODO: currently taken from Anthony's paper
    """
    antenna:AntennaModel = topo.antennas[topo.pylons[p]]
    return antenna.gain * topo.shadowing * dist2(p,u)**(-antenna.alpha)


def pathloss(topo:Topology, p:tuple[float,float], u:tuple[float,float]) -> float:
    """Okumura-Hata path loss model

    TODO
    """
    f = topo.antennas[topo.pylons[p]].bandwidth / 2 # ?
    H = 375 # Average altitude in France (source wikipedia)
    d = topo.graph.edges[u].w
    c = -5 # Suburban value found in the RF design book section 4.6.6
    return 69.55 + 26.16*log10(f) - 13.82*log10(H) + (44.9 - 6.55*log10(H)) * log10(d) + c



def snr(topo:Topology, p:tuple[int,int], u:tuple[int,int]) -> float:
    """Signal to noise ratio not taking interferences between BS into account.

    TODO
    """
    antenna = topo.antennas[topo.pylons[p]]
    # How to take the `#{antennas}` into account since it modifies itself with resource allocation :/
    S = antenna.power + 10*log10(len(topo.pylons)) + antenna.gain - pathloss(p,u) - topo.loss_factor*log10(dist2(p,u))
    N = -174 + 10*log10(antenna.bandwidth)
    return S / N
