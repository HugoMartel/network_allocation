import json
from matplotlib import pyplot as plt
from lib.util import sample_users


def sample_toy_UEs(grid:list[list[int]], tile_size:tuple[int, int]) -> list[object]:
    """TODO
    """
    UEs = []
    for i,row in enumerate(grid):
        for j,ind in enumerate(row):
            if ind > 0:
                for ue in sample_users(tile_size, ind):
                    UEs.append({
                        "pos": {
                            "x": j*tile_size[0]+ue[0],
                            "y": i*tile_size[1]+ue[1]
                        },
                        "demand": 1e6
                    })
    return UEs


if __name__ == '__main__':
    # Setup pop density grid
    density_grid = [
        [0, 0, 2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 5,20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 2,18, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0],
        [0, 3,30,21,35,25, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0,20,13,16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2,10, 4, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 7, 0,20, 0, 0, 0],
        [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0]
    ]
    tile_size = (200,200)

    # Plot the density grid
    fig = plt.figure()
    ax = fig.add_subplot()

    im = ax.imshow(density_grid, cmap='viridis', origin='lower')
    fig.colorbar(im, ax=ax, label='Density of end users')

    ax.set_xlabel('x position')
    ax.set_ylabel('y position')
    ax.grid(False)

    plt.show()

    # Sample UEs
    json.dump(
        sample_toy_UEs(density_grid, tile_size),
        open("data/equipments/toy.json", "w"),
        indent=4
    )
