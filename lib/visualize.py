import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize
import seaborn as sns
import numpy as np
from scipy.optimize import root_scalar
from lib.topology import Topology, Wlimit, pathloss_oh, pathloss_fs, pathloss_simple, dist2, snr, Wcost, Wcost_prime

# Global setup
plt.ioff()
sns.set_theme(font_scale=3.)
plt.rcParams.update({'font.size': 20})


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


def plot_topology_allocation(topo:Topology):
    """TODO
    """
    fig = plt.figure()
    ax = fig.add_subplot()

    # Plot allocations
    edges = [ (u,user.pylon) for u,user in topo.users.items() if user.pylon != None ]
    colors = [ (topo.graph.vertices[u] / topo.antennas[topo.pylons[p].antenna_type].bandwidth, .5, .5) for u,p in edges ]
    test_cmap = LinearSegmentedColormap('Test', {
        'red': (
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0)
        ),
        'green': (
            (0.0, 0.5, 0.5),
            (1.0, 0.5, 0.5)
        ),
        'blue': (
            (0.0, 0.5, 0.5),
            (1.0, 0.5, 0.5)
        ),
        'alpha': (
            (0.0, 0.8, 0.8),
            (1.0, 0.8, 0.8)
        )
    })
    lc = LineCollection(edges, linewidths=1, colors=colors)
    ax.add_collection(lc)

    # Plot points
    x,y = zip(*topo.pylons.keys())
    ax.plot(x, y, c='red', marker=r'$\star$', markersize=10, linestyle='none', label='Base stations')
    x,y = zip(*topo.users.keys())
    ax.plot(x, y, c='black', marker=r'$\bullet$', markersize=3, linestyle='none', label='User Equipments')

    max_bandwidth = np.max(list(map(lambda a: a.bandwidth, topo.antennas)))
    cbar = fig.colorbar(None, ax=ax, location='right', label='Allocated bandwidth (Hz)', cmap=test_cmap, norm=Normalize(0, max_bandwidth))
    cbar.minorticks_on()

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.grid(True)
    ax.legend()
    # ax.set_title(
    #     "BS/UE allocation of the network",
    #     loc='left',
    #     weight='bold'
    # )

    plt.show()


def plot_allocated_bandwidth(topo:Topology, p:tuple[float,float], u:tuple[float,float], pathloss) -> None:
    """TODO

    Parameters
    ----------
    topo
        The topology of the network
    p
        The position of the pylon
    u
        The position of the user
    pathloss
        The pathloss function to use
    """
    fig, (ax, axprime) = plt.subplots(1,2, figsize=(16,6))

    # Constants
    a = 1
    C = a*topo.users[u].demand
    PL = pathloss(topo, p, u)
    N0 = -174
    antenna = topo.antennas[topo.pylons[p].antenna_type]
    S = antenna.power + antenna.gain - PL
    d = dist2(p,u)

    # Plot allocations
    x = np.linspace(1000, C, 1000)

    # Function plot
    ax.plot(x, [ Wcost(w, C, N0, S) for w in x ], '-', c='red')
    lim = Wlimit(C, N0, S)
    ax.plot(x, np.full_like(x, lim), '--', c='black', label='$\\lim_{w \\to \\infty} f(w)$')

    # Derivative plot
    axprime.plot(x, [ Wcost_prime(w, C, N0, S) for w in x ], '-', c='blue')
    axprime.plot(x, np.zeros_like(x), '--', c='black')

    # Call the solver if there exists a root for f
    root_value = antenna.bandwidth + 1
    if lim <= 0.:
        try:
            #nx0 = 100
            #opt_res = root_scalar(Wcost, fprime=Wcost_prime, x0=np.array([C*i/nx0 for i in range(1,nx0+1)]), args=(C, N0, S))
            opt_res = root_scalar(Wcost, fprime=Wcost_prime, x0=0.5*C, args=(C, N0, S), bracket=[1, 1e22])
        except ValueError:
            print("ERROR when calling the solver")
            print(f"C={C}, N0={N0}, S={S}")
            print("----------------------")

        # Handle the solver result and plot the root
        if opt_res.converged:
            root_value = opt_res.root
        else:
            print("The solver did not converge, can't plot root, defaults to W+1")

    print(f"Bandwidth to allocate: {root_value} Hz")
    ax.axvline(x=root_value, c='green')
    axprime.axvline(x=root_value, c='green', label=f'Allocated bandwidth')

    ax.set_xlabel('$w$ - Allocated bandwidth (Hz)')
    ax.set_ylabel('$f(w)$')
    ax.grid(True)
    ax.legend()
    ax.set_title(
        f"BS's bandwidth to allocate to a given UE at {d:.0f}m",
        loc='left',
        weight='bold'
    )

    axprime.set_xlabel('$w$ - Allocated bandwidth (Hz)')
    axprime.set_ylabel('$f\'(w)$')
    axprime.grid(True)
    axprime.legend()

    plt.show()


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
