import numpy as np

def dist2(u:tuple[int,int], v:tuple[int,int]) -> float:
    """Euclidian distance between two points.

    Parameters
    ----------
    u
        First point.
    v
        Second point.

    Returns
    -------
    Distance between the two points.
    """
    return ((u[0]-v[0])**2 + (u[1]-v[1])**2)**0.5


def sample_users(tile_size:tuple[float,float], density:int) -> np.ndarray:
    """Sample end users in a tile from a given density.

    Parameters
    ----------
    tile_size
        Size of a tile in meters by coord.
    density
        Number of end users per tile.

    Returns
    -------
    List of sampled end users.
    """
    return np.dstack((np.random.uniform(0, tile_size[0], density), np.random.uniform(0, tile_size[1], density)))[0]
