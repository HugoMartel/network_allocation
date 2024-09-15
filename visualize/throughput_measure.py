from lib.topology import Topology, AntennaModel, Pylon, User, Wlimit, pathloss_oh, pathloss_fs, pathloss_simple, dist2, snr, Wcost, Wcost_prime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_topology_density(topo:Topology) -> None:
    """TODO
    """
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

    plt.show(block=False)


def plot_topology_graph(topo:Topology) -> None:
    """TODO
    """
    fig = plt.figure()
    ax = fig.add_subplot()

    x,y = zip(*topo.pylons.keys())
    ax.plot(x, y, c='red', marker=r'$\star$', markersize=10, linestyle='none', label='Base stations')
    x,y = zip(*topo.users.keys())
    ax.plot(x, y, c='black', marker=r'$\bullet$', markersize=3, linestyle='none', label='User Equipments')

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.grid(True)
    ax.legend()
    xmax = topo.width*topo.tile_size[0]
    ymax = topo.height*topo.tile_size[1]
    ax.set_xlim(0-xmax/100, xmax+xmax/100)
    ax.set_ylim(0-ymax/100, ymax+ymax/100)
    # ax.set_title(
    #     "Topology of the network",
    #     loc='left',
    #     weight='bold'
    # )

    plt.show(block=False)


def plot_measures(topo:Topology):
    """TODO
    """
    # Compute values
    x = []# Users positions on one axis
    # Path loss models to take into account
    pathlosses = {"OH": pathloss_oh, "FS": pathloss_fs, "Simple": pathloss_simple}
    # Init measures dictionaries
    throughput = {"OH": [], "FS": [], "Simple": []}
    pl = {"OH": [], "FS": [], "Simple": []}
    s = {"OH": [], "FS": [], "Simple": []}
    sn = {"OH": [], "FS": [], "Simple": []}

    # Measure everything
    antenna = topo.antennas[0]
    p = list(topo.pylons.keys())[0]# Select the only pylon in the topology
    for u in sorted(topo.users.keys(), key=lambda u: u[0]):
        x.append(dist2(u, p))
        for pi, pathloss in pathlosses.items():
            throughput[pi].append(antenna.bandwidth * np.log2(1 + snr(topo, p, u, pathloss)))
            pl[pi].append(pathloss(topo, p,u))# Pathloss in dB
            s[pi].append(topo.antennas[0].power + antenna.gain - pathloss(topo, p,u))# in dB
            sn[pi].append(10*np.log10(snr(topo, p, u, pathloss)))# Convert to dB

    # Plotting styles
    styles = {"OH": "-", "FS": ":", "Simple": "--"}

    # PL
    fig = plt.figure()
    ax = fig.add_subplot()

    for pi in pathlosses.keys():
        ax.plot(x, pl[pi], styles[pi], linewidth="5", label=pi)

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Path loss (dB)')
    #ax.set_yscale('log')
    ax.grid(True)
    ax.legend()

    plt.show(block=False)

    # S
    fig = plt.figure()
    ax = fig.add_subplot()

    for pi in pathlosses.keys():
        ax.plot(x, s[pi], styles[pi], linewidth="5", label=pi)

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Signal (dB)')
    ax.grid(True)
    ax.legend()

    plt.show(block=False)

    # SNR
    fig = plt.figure()
    ax = fig.add_subplot()

    for pi in pathlosses.keys():
        ax.plot(x, sn[pi], styles[pi], linewidth="5", label=pi)

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Signal to Noise Ratio (dB)')
    #ax.set_yscale('log')
    ax.grid(True)
    ax.legend()

    plt.show(block=False)

    # Throughput
    fig = plt.figure()
    ax = fig.add_subplot()

    for pi in pathlosses.keys():
        ax.plot(x, throughput[pi], styles[pi], linewidth="5", label=pi)

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Throughput (bit/s)')
    ax.grid(True)
    ax.legend()

    plt.show(block=False)

    # Spectral efficiency
    fig = plt.figure()
    ax = fig.add_subplot()

    for pi in pathlosses.keys():
        ax.plot(x, [ t / antenna.bandwidth for t in throughput[pi] ], styles[pi], linewidth="5", label=pi)

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Spectral efficiency ((bit/s)/Hz)')
    #ax.set_yscale('log')
    ax.grid(True)
    ax.legend()

    plt.show()


if __name__ == '__main__':

    # Create an empty topology
    topo = Topology()

    # Samples amount
    n = 1000
    min_dist = 10
    max_dist = 1000

    # Init the topology by hand for measures
    ## Create antennas
    topo.antennas.append(AntennaModel(# 5G Macro Cell values
        "5G Antenna",
        60,
        17,
        10e6,
        700e6,
        1000000# Huge range to always allow computing the throughput
    ))

    ## Create pylons
    topo.pylons[(0,0)] = Pylon((0,0), 30, 0)

    ## Create users
    topo.width = max_dist
    topo.height = 1
    topo.density_grid = [[1 for _ in range(max_dist)]]
    topo.users = {
        (x,0): User((x,0), (0,0), 1e6)
        for x in np.arange(min_dist, max_dist+1, (max_dist-min_dist)/n)
    }

    # Checking if the topology is correctly created
    plot_topology_density(topo)
    plot_topology_graph(topo)

    # Plot the different measurements
    plot_measures(topo)
