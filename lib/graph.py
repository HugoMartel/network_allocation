from bisect import insort

class WeightedEdge:
    u:object
    v:object
    w:float

    def __init__(self, u:object, v:object, w:float):
        self.u = u
        self.v = v
        self.w = w

    def __lt__(self, e):
        return self.w < e.w

    def __str__(self):
        return f"{self.u} -> {self.v} : {self.w}"


class WeightedGraph:
    vertices:dict[object, float]
    edges:dict[object, list[WeightedEdge]]

    def __init__(self):
        """TODO
        """
        # Empty graph
        self.vertices = {}
        self.edges = {}

    def add_vertex(self, u:object, w:float):
        """TODO
        """
        self.vertices[u] = w # Be careful, previously set vertices will be overriden
        self.edges[u] = []

    def add_edge(self, u:object, v:object, w:float):
        """TODO
        """
        insort(self.edges[u], WeightedEdge(u, v, w))

    def __str__(self):
        """TODO
        """
        out = ""
        for u,wu in self.vertices.items():
            out += f"{u} ({wu}):\n"
            for e in self.edges[u]:
                out += f"  {e}\n"
        return out
