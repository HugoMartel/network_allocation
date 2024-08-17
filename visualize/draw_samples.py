import json
import matplotlib.pyplot as plt

def plot_samples(UEs:list[object], BSs:list[object]) -> None:
    """TODO
    """
    fig = plt.figure()
    ax = fig.add_subplot()

    x = [ ue["pos"]["x"] for ue in UEs ]
    y = [ ue["pos"]["y"] for ue in UEs ]
    ax.plot(x, y, c='black', marker=r'$\bullet$', markersize=3, linestyle='none', label='User Equipments')

    x = [ bs["pos"]["x"] for bs in BSs ]
    y = [ bs["pos"]["y"] for bs in BSs ]
    ax.plot(x, y, c='red', marker=r'$\star$', markersize=10, linestyle='none', label='Base stations')

    ax.set_xlabel('x position (m)')
    ax.set_ylabel('y position (m)')
    ax.grid(True)
    ax.legend()
    # xmax = topo.width*topo.tile_size[0]
    # ymax = topo.height*topo.tile_size[1]
    # ax.set_xlim(0-xmax/100, xmax+xmax/100)
    # ax.set_ylim(0-ymax/100, ymax+ymax/100)
    # ax.set_title(
    #     "Topology of the network",
    #     loc='left',
    #     weight='bold'
    # )

    plt.show(block=True)


if __name__ == '__main__':
    # Load User Equipments
    #samples = json.load(open("data/equipments/lyon_equipments_INSEE.json", "r"))
    samples = json.load(open("data/equipments/toy.json", "r"))

    # Load towers (Base Stations)
    #towers = json.load(open("data/towers/lyon_towers_ANFR.json", "r"))
    towers = json.load(open("data/towers/toy.json", "r"))

    plot_samples(samples, towers)
