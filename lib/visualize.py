import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import seaborn as sns
import numpy as np
from lib.topology import Topology

# Global setup
plt.ioff()
sns.set_theme(font_scale=1.8)
plt.rcParams.update({'font.size': 20})


def plot_topology_density(topo:Topology) -> None:
    fig = plt.figure()
    ax = fig.add_subplot()

    im = ax.imshow(topo.density_grid, cmap='viridis', origin='lower')
    fig.colorbar(im, ax=ax, label='Density of end users')

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.grid(False)
    ax.set_title(
        "Density of end users",
        loc='left',
        weight='bold'
    )

    plt.show()


def plot_topology_graph(topo:Topology) -> None:
    fig = plt.figure()
    ax = fig.add_subplot()

    x,y = zip(*topo.pylons.keys())
    ax.scatter(x, y, [10 for _ in x], c='red', label='Base stations')
    x,y = zip(*topo.users.keys())
    ax.scatter(x, y, [5 for _ in x], c='black', label='User Equipments')

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.grid(True)
    ax.legend()
    ax.set_title(
        "Topology of the network",
        loc='left',
        weight='bold'
    )

    plt.show()


def plot_topology_allocation(topo:Topology):
    fig = plt.figure()
    ax = fig.add_subplot()

    # Plot allocations
    edges = [ (u,p) for u,p in topo.users.items() if p != None ]
    lc = LineCollection(edges, linewidths=1, colors=["black"])
    ax.add_collection(lc)

    # Plot points
    x,y = zip(*topo.pylons.keys())
    ax.scatter(x, y, [10 for _ in x], c='red', label='Base stations')
    x,y = zip(*topo.users.keys())
    ax.scatter(x, y, [5 for _ in x], c='black', label='User Equipments')

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.grid(True)
    ax.legend()
    ax.set_title(
        "BS/UE allocation of the network",
        loc='left',
        weight='bold'
    )

    plt.show()
