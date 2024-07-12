#!/usr/bin/env python3
import networkx as nx
import matplotlib.pyplot as plt
from sys import argv

class GraphViz:

    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.visual = []
        for parent, children in edges.items():
            for child in children:
                self.visual.append([parent,child])

    def visualize(self):
        G = nx.DiGraph()
        G.add_edges_from(self.visual, minlen=1)
        nx.draw_networkx(
            G,
            pos={v: tuple(map(lambda x: float(x), v.split(", ", 1))) for v in self.vertices},
            arrows=True,
            arrowstyle="->",
            labels=self.vertices,
            node_color="#fff",
            node_size=500,
            width=2.0
        )
        plt.axis("off")
        plt.show()

# Init a graph object
G_dict = {}
G_vertices = {}

# Read graph file input
if len(argv) < 2:
    print("Missing graph file argument")
    exit(0)
gfile = open(argv[1], "r")

# Read graph
i = 0
lines = gfile.readlines()
nlines = len(lines)
while i < nlines:
    # Read vertex
    v = lines[i][1:].split(")", 1)[0]
    i+=1
    G_vertices[v] = "BS" if i<nlines and lines[i][0] == " " else "UE"
    G_dict[v] = []

    # Read edges starting from v
    while i < nlines and lines[i][0] == ' ':
        e_tmp = lines[i][2:].split(" -> (", 1)[1]
        e,w = e_tmp.split(") : ", 1)
        G_dict[v].append(e)
        i+=1

# Draw graph
G = GraphViz(G_vertices, G_dict)
G.visualize()
