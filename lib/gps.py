import geopandas as gpd
from math import pi, sin, cos, atan2, sqrt


# LYON GPS BOUNDS
lyon_map_center = {# Lyon center coordinates
    "lat": 45.75,
    "lon": 4.85
}
lyon_offsets = {# Lyon offsets to select only Lyon's antennas (neg offset, pos offset)
    "lat_offset": (.06, .06),
    "lon_offset": (.06,.06)
}
lyon_coords = {# Lyon min and max coordinates to select only Lyon GPS coords
    "min": {
        "lat": lyon_map_center["lat"] - lyon_offsets["lat_offset"][0],
        "lon": lyon_map_center["lon"] - lyon_offsets["lon_offset"][0]
    },# Lyon min coordinates (x,y)
    "max": {
        "lat": lyon_map_center["lat"] + lyon_offsets["lat_offset"][1],
        "lon": lyon_map_center["lon"] + lyon_offsets["lon_offset"][1]
    } # Lyon max coordinates (x,y)
}


def gps_dist(lat1:float, lon1:float, lat2:float, lon2:float) -> float:
    """Computes the distance between two GPS points using the Haversine formula.

    Parameters
    ----------
    lat1
        TODO
    lon1
        TODO
    lat2
        TODO
    lon2
        TODO

    Returns
    -------
    float
        Computed distance in meters.
    """
    earth_radius = 6371000#meters

    lat_diff = (lat2-lat1) * pi / 180# in rad
    lon_diff = (lon2-lon1) * pi / 180# in rad

    lat1_rad = lat1 * pi / 180;
    lat2_rad = lat2 * pi / 180;

    # Haversine formula
    a:float = sin(lat_diff/2) * sin(lat_diff/2) + cos(lat1_rad) * cos(lat2_rad) * sin(lon_diff/2) * sin(lon_diff/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return earth_radius * c


# local_coords = {
#     "min": {
#         "x": 0.,
#         "y": 0.
#     },
#     "max": {
#         "x": gps_dist(lyon_coords["min"]["lat"], lyon_coords["min"]["lon"], lyon_coords["max"]["lat"], lyon_coords["min"]["lon"]),
#         "y": gps_dist(lyon_coords["min"]["lat"], lyon_coords["min"]["lon"], lyon_coords["min"]["lat"], lyon_coords["max"]["lon"])
#     }
# }


def gps_to_float(gps:str) -> float:
    """Converts a GPS coordinate from the format 'xx°xx'xx" to a float.

    Parameters
    ----------
    gps
        The GPS coordinate to convert

    Returns
    -------
    float
        The converted GPS coordinate as a float
    """
    direction = gps[-1]
    degree, tmp = gps.split("°", 1)
    minutes, seconds = tmp[:-3].split("'", 1)
    # don't forget to remove the last character which is the cardinal direction
    return float(degree) + (float(minutes) + float(seconds) / 60 ) / 60


def inspireID_to_floats(ins:str) -> tuple[float,float]:
    """TODO
    """
    # Example given string:
    # Inspire ID example: CRS3035RES200mN2029800E4254200
    # CRS3035 -> EPSG:3035 CRS code for ETRS89-extended / LAEA Europe
    # RES200m -> 200m resolution squares
    # N2029800 -> North coordinate for the left bottom corner of the square (longitude)
    # E4254200 -> East coordinate for the left bottom corner of the square (latitude)
    coords:str = ins[14:]

    return (
        float(coords[1:8]) * (1 if coords[0] == 'N' else -1),
        float(coords[9:]) * (1 if coords[8] == 'E' else -1)
    )


def point_to_gps(point:str) -> dict[str,float]:
    """TODO
    """
    # 'POINT (4.89143176317163 45.68046285023667)'
    lon_lat = point.split(' ')[1:]
    # ['(4.89143176317163', '45.68046285023667)']
    return {
        'lat': float(lon_lat[1][:-1]),
        'lon': float(lon_lat[0][1:])
    }
