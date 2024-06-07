import numpy as np
from bisect import insort
import json


def dist2(u:tuple[int,int], v:tuple[int,int]) -> float:
    return np.sqrt((u[0]-v[0])**2 + (u[1]-v[1])**2)


class WeightedEdge:
    v:tuple[int,int]
    w:float

    def __init__(self, v:tuple[int,int], w:float):
        self.v = v
        self.w = w

    def __lt__(self, e):
        return self.w < e.w

    def __str__(self):
        return f"-> {self.v} : {self.w}"


class WeightedGridGraph:
    vertices:set[tuple[int,int]]
    edges:dict[tuple[int,int], list[WeightedEdge]]

    def __init__(self):
        """TODO
        """
        # Empty graph
        self.edges = {}
        self.vertices = set()

    def __init__(self, grid:np.array):
        """Build a dumb clique G=(V,E) with #E = #V * (#V - 1)
        """
        # grid is a 2D numpy array
        self.edges = {}
        self.vertices = set()

        # Init vertices
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                self.vertices.add((x,y))
                self.edges[(x,y)] = []

        # Init edges & weights
        for u in self.vertices:
            for v in self.vertices:
                if u != v:
                    d:float = dist2(u,v)
                    insort(self.edges[u], WeightedEdge(v, d))
                    insort(self.edges[v], WeightedEdge(u, d))

    def __init__(self, grid:np.array, stations:list[tuple[int,int]]):
        """Build a graph G=(V,E) with less edges #E = #p * #V
        Only keep edges between pylons and user equipments
        """
        # grid is a 2D numpy array
        self.edges = {}
        self.vertices = set()

        # Init vertices
        for x in range(grid.shape[0]):
            for y in range(grid.shape[1]):
                self.vertices.add((x,y))
                self.edges[(x,y)] = []

        # Init edges & weights
        for u in stations:
            for v in self.vertices:
                # We suppose that there can't be a station on a user equipment
                # Which will not be the case in the real world
                if u != v and v not in stations and grid[v[0]][v[1]] > 0:
                    d:float = dist2(u,v)
                    insort(self.edges[u], WeightedEdge(v, d))
                    insort(self.edges[v], WeightedEdge(u, d))

    def get_adjacent(self, u):
        """TODO
        """
        return self.edges[u]

    def __str__(self):
        """TODO
        """
        out = ""
        for u in self.vertices:
            out += f"{u} {self.edges[u]}\n"
        return out


class AntennaModel:
    name: str
    gain: float
    bandwidth: float
    reach: float # range is a reserved keyword
    alpha: float

    def __init__(self, name:str, gain:float, bandwidth:float, reach:float, alpha:float):
        self.name = name
        self.gain = gain
        self.bandwidth = bandwidth
        self.reach = reach
        self.alpha = alpha


class Topology:
    height:int
    width:int
    grid:np.array # dim 2 array
    pylons:dict[tuple[int,int], int]
    antennas:list[AntennaModel]

    # Constants
    shadowing:float = 1.0

    def __init__(self, h:int, w:int):
        """Creates an empty Topology object.

        Parameters:
        width -- Width of the grid.
        height -- Height of the grid.
        """
        self.height = h
        self.width = w
        self.grid = np.zeros((self.width, self.height), float)

    def __init__(self, filename:str):
        """Loads a json topology file into a Topology object.

        Parameters:
        filename -- File path to load.
        """
        topo_json = json.load(open(filename, "r"))
        self.height = topo_json["height"]
        self.width = topo_json["width"]
        self.grid = np.zeros((self.width, self.height), float)
        for user in topo_json["end_users"]:
            self.grid[user["pos"]["x"]][user["pos"]["y"]] = user["qos"]

        self.pylons = {(pylon["pos"]["x"], pylon["pos"]["y"]): -1 for pylon in topo_json["pylons"]}

        self.antennas = [
            AntennaModel(
                model["name"],
                model["gain"],
                model["bandwidth"],
                model["range"],
                .5# Alpha, TODO
            ) for model in topo_json["antennas"]
        ]


def gain(topo:Topology, p:tuple[int,int], u:tuple[int,int]) -> float:
    """Gain received by the end user at position u from the pylon at position p.
    """
    antenna:AntennaModel = topo.antennas[topo.pylons[p]]
    return antenna.gain * topo.shadowing * dist2(p,u)**(-antenna.alpha)

def snr(topo:Topology, p:tuple[int,int], u:tuple[int,int]) -> float:
    """TODO
    """
    # The interference is not taken into account here
    return gain(topo, p, u) / (topo.antennas[topo.pylons[p]].bandwidth * topo.noise)
