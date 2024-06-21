import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize
import seaborn as sns
import numpy as np
from scipy.optimize import root_scalar
from lib.topology import Topology, pathloss_oh, pathloss_fs, pathloss_simple, dist2, snr, Wcost, Wcost_prime

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

    plt.show(block=False)


def plot_topology_graph(topo:Topology) -> None:
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
    ax.set_title(
        "Topology of the network",
        loc='left',
        weight='bold'
    )

    plt.show(block=False)


def plot_topology_allocation(topo:Topology):
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
    print("Colormap test")#! DEBUG
    print(f"Max bandwidth: {max_bandwidth}")#! DEBUG
    cbar = fig.colorbar(None, ax=ax, location='right', label='Allocated bandwidth (MHz)', cmap=test_cmap, norm=Normalize(0, max_bandwidth))
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


def plot_allocated_bandwidth(topo:Topology, p:tuple[float,float], u:tuple[float,float]) -> None:
    fig, (ax, axprime) = plt.subplots(1,2, figsize=(16,6))

    # Constants
    Q = topo.users[u].demand
    PL = pathloss_fs(topo, p, u)
    N0 = -174
    antenna = topo.antennas[topo.pylons[p].antenna_type]
    d = dist2(p,u)

    # Plot allocations
    x = np.linspace(.001, antenna.bandwidth, 1000)

    f = lambda x: Wcost(x, Q, N0, antenna.power + antenna.gain - PL)
    df = lambda x: Wcost_prime(x, Q, N0)

    # Plot points
    ax.plot(x, f(x), '-', c='red', label=f'UE at {d}m from BS')

    ax.set_xlabel('$w$ - Allocated bandwidth (MHz)')
    ax.set_ylabel('$f(w)$')
    ax.grid(True)
    #ax.legend()
    #ax.set_title(
    #    "BS's bandwidth to allocate to a given UE",
    #    loc='left',
    #    weight='bold'
    #)

    axprime.plot(x, df(x), '-', c='blue', label=f'Derivative of the function')
    axprime.plot(x, [0 for _ in x], '--', c='black', label='y=0')

    opt_res = root_scalar(f, fprime=df, x0=Q)

    if opt_res.converged:
        ax.axvline(x=opt_res.root, c='green', label=f'Optimal bandwidth {opt_res.root:.2f} MHz')
        axprime.axvline(x=opt_res.root, c='green', label=f'Optimal bandwidth {opt_res.root:.2f} MHz')
        print(f"Bandwidth to allocate: {opt_res.root} MHz")
    else:
        print("ERROR: the solver did not converge, can't plot")

    axprime.set_xlabel('$w$ - Allocated bandwidth (MHz)')
    axprime.set_ylabel('$f\'(w)$')
    axprime.grid(True)

    plt.show()


def plot_throughput(topo:Topology):
    # Compute values
    x = []
    y = []
    pl = []
    s = []
    sn = []

    for u in sorted(topo.users.keys(), key=lambda u: u[0]):
        for p in topo.pylons.keys():
            x.append(dist2(u, p))
            # PL in db
            y.append(topo.antennas[0].bandwidth * np.log2(1 + snr(topo, p, u)))
            pl.append(pathloss_simple(topo, p,u))
            s.append(topo.antennas[0].power + topo.antennas[0].gain - pathloss_simple(topo, p,u))
            sn.append(snr(topo, p,u))
            break

    # PL
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(x, pl, c='red')

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Path loss (dB)')
    ax.set_yscale('log')
    ax.grid(True)

    plt.show(block=False)

    # S
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(x, s, c='pink')

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Signal in dB')
    ax.grid(True)

    plt.show(block=False)

    # SNR
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(x, sn, c='blue')

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Signal to Noise Ratio')
    ax.set_yscale('log')
    ax.grid(True)

    plt.show(block=False)

    # Throughput
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(x, y, c='black')

    ax.set_xlabel('Distance between the UE and BS (m)')
    ax.set_ylabel('Throughput (Mbps)')
    ax.grid(True)

    plt.show()
