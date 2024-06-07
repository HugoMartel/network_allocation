import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from lib.topology import Topology

# Global setup
plt.ioff()
sns.set_theme(font_scale=1.8)
plt.rcParams.update({'font.size': 20})


def plot_topology(topo:Topology) -> None:
    fig = plt.figure(figsize=(16,6))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    # Grid
    x,y = np.meshgrid(
        np.linspace(0, topo.height-1, topo.height),
        np.linspace(0, topo.width-1, topo.width))

    # End Users
    z = np.array(topo.grid)
    ax1.plot_surface(
        x,
        y,
        z,
        #marker='o',
        color='blue',
        label='End users QoS constraint',
    )
    ax1.set_xlabel('x position')
    ax1.set_ylabel('y position')
    ax1.set_zlabel('QoS (bps)')
    #ax1.grid(True)
    #ax1.legend()
    ax1.set_title(
        "End users qos constraints",
        loc='left',
        weight='bold'
    )


    # Pylons
    z = np.array([ [ 1 if (int(x),int(y)) in topo.pylons.keys() else 0 for y in range(topo.height) ] for x in range(topo.width) ])
    ax2.plot_surface(
        x,
        y,
        z,
        #marker='o',
        color='red',
        label='Pylons locations',
    )
    ax2.set_xlabel('x position')
    ax2.set_ylabel('y position')
    ax2.set_zlabel('QoS (bps)')
    #ax2.grid(True)
    #ax2.legend()
    ax2.set_title(
        "Available pylon locations",
        loc='left',
        weight='bold'
    )

    plt.show()


def plot_grid(topo:Topology) -> None:
    pass