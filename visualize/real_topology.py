import folium
import pandas as pd
import json


def plot_use_case(squares_INSEE, BSs_ARCEP, BSs_ANFR):
    """TODO
    """
    m = folium.Map(location=[45.75, 4.85], zoom_start=13)

    # Place density squares from INSEE
    print("> Placing INSEE squares")#! DEBUG
    max_ind = 0 if squares_INSEE == [] else max([ind for _,_,ind in squares_INSEE])
    for lat,lon,ind in squares_INSEE:
        # square holds the left bottom point of a 200m square
        ind_color = f"#{int(ind / max_ind * 255):02x}{int((1-ind / max_ind) * 255):02x}00" # Green-Red linear interpolation
        # Add a square polygon with a color indicating the population density
        folium.Rectangle(
            bounds=[
                [lat, lon],
                [lat + 0.00179, lon + 0.00255],
            ],
            color=ind_color,
            stroke=False,# Disables border
            fill=True,
            fill_color=ind_color,
            fill_opacity=0.4,
        ).add_to(m)

    # Place BSs from ARCEP
    print("> Placing ARCEP towers")#! DEBUG
    for bs in BSs_ARCEP : # Iterate on base stations positions
        # Add a Marker
        folium.RegularPolygonMarker(
            location=bs,         # Latitude and longitude
            number_of_sides=5,      # Number of sides of the polygon
            radius=3,               # Radius of the polygon
            color='red',            # Color of the polygon
            fill=True,              # Fill the polygon with color
            fill_color='blue',      # Fill color
            fill_opacity=1.0,       # Fill opacity (0 to 1)
        ).add_to(m)

    # Place BSs from ANFR
    print("> Placing ANFR towers")#! DEBUG
    for bs in BSs_ANFR: # Iterate on base stations positions
        # Add a Marker
        folium.RegularPolygonMarker(
            location=bs,         # Latitude and longitude
            number_of_sides=3,      # Number of sides of the polygon
            radius=3,               # Radius of the polygon
            color='blue',           # Color of the polygon
            fill=True,              # Fill the polygon with color
            fill_color='blue',      # Fill color
            fill_opacity=1.0,       # Fill opacity (0 to 1)
        ).add_to(m)

    # Display the map
    m.save('real_topology_map.html')



if __name__ == '__main__':
    # Load User Equipments
    squares_df = pd.read_csv("./downloads/lyon_tiles_INSEE.csv")[['latitude','longitude','ind']]
    squares_INSEE = list(zip(squares_df['latitude'], squares_df['longitude'], squares_df['ind']))

    # Load towers (Base Stations)
    BS_df = pd.read_csv("./downloads/lyon_stations_ARCEP.csv")[['latitude', 'longitude']]
    BSs_ARCEP = list(zip(BS_df['latitude'], BS_df['longitude']))
    BSs_ARCEP = []

    BS_df = pd.read_csv("./downloads/lyon_stations_ANFR.csv")[['latitude', 'longitude']]
    BSs_ANFR = list(zip(BS_df['latitude'], BS_df['longitude']))

    plot_use_case(squares_INSEE, BSs_ARCEP, BSs_ANFR)
