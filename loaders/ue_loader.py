import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

from lib.gps import lyon_coords, inspireID_to_floats, gps_dist
from lib.util import sample_users

from os import path

def load_ue_data(csv_filepath: str) -> pd.DataFrame:
    """Load the UE data from the CSV file and return a DataFrame with the relevant columns.
    These columns are:
    - idcar_200m: The square ID containing the GPS coordinates in the EPSG:3035 projection format
    - i_est_200: 1 if the square is imputed by an approximate value, 0 otherwise
    - ind: Number of individuals in the square
    - men: Number of households in the square (ménages in French)

    Parameters
    ----------
    csv_filepath
        The CSV file path to load

    Returns
    -------
    pd.DataFrame
        The DataFrame with the relevant columns
    """
    # Check that the file exists
    if not path.exists(csv_filepath):
        print(f"{csv_filepath} does not exist, unable to load UEs...")
        exit(-1)

    df = pd.read_csv(csv_filepath, sep=',', header=0, encoding='utf-8')[
    [
        'idcar_200m',
        'i_est_200',# Vaut 1 si le carreau est imputé par une valeur approchée, 0 sinon.
        'ind',# Nombre d'individus
        'men',# Nombre de ménages
    ]]

    # Convert INSPIRE ID to couple of floats
    squares_coords = df['idcar_200m'].apply(inspireID_to_floats)
    # Convert EPSG:3035 float couple to EPSG:4326 (open street map projection) using GeoPandas
    projected_squares = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(squares_coords.str[1], squares_coords.str[0], crs="EPSG:3035")
    ).to_crs(4326)
    # Add the properly projected coords to the inital DataFrame
    df['latitude'] = projected_squares['geometry'].y
    df['longitude'] = projected_squares['geometry'].x

    ## Lyon's center in 3035: N 3919210.942047147 & E 2529111.126602604

    lyon_tiles = df[
        (# Latitude is the second coordinate (E or W)
            (df['latitude'] >= lyon_coords["min"]["lat"]) &
            (df['latitude'] <= lyon_coords["max"]["lat"])
        ) & (# Longitude is the first coordinate (N or S)
            (df['longitude'] >= lyon_coords["min"]["lon"]) &
            (df['longitude'] <= lyon_coords["max"]["lon"])
        )
    ]

    all_lyon_tiles_count:int = lyon_tiles.shape[0]

    #! REMOVE squares with less than 10 individuals
    lyon_tiles = lyon_tiles[
        lyon_tiles['ind'] >= 10
    ]

    print(lyon_tiles.head())
    print(lyon_tiles.shape[0])
    print(f"REMOVED {all_lyon_tiles_count-lyon_tiles.shape[0]} tiles under 10 indiviuals")

    # Export data for OpenStreetMap plotting
    lyon_tiles.to_csv(path.join(path.dirname(csv_filepath), "lyon_tiles_INSEE.csv"))

    return lyon_tiles


def save_ue_data(df: pd.DataFrame, output_filepath: str) -> None:
    """Save the UE data to a JSON file.
    The JSON file can then be used to create a network graph.

    Parameters
    ----------
    df
        The DataFrame to save
    output_filepath
        The output JSON file path
    """
    with open(output_filepath, "w") as f:
        f.write("[\n")
        i = 1
        for index, row in df.iterrows():
            # Convert the coords to local ones in meters
            x = gps_dist(
                lyon_coords["min"]["lat"], lyon_coords["min"]["lon"],
                row['latitude'], lyon_coords["min"]["lon"]
            )
            y = gps_dist(
                lyon_coords["min"]["lat"], lyon_coords["min"]["lon"],
                lyon_coords["min"]["lat"], row["longitude"]
            )
            # Sample UEs from the square
            UEs = []
            samples = sample_users((200.,200.), int(row['ind']))
            for sample in samples:
                UEs.append((x + sample[0], y + sample[1]))

            # Generate string for the user
            for j, (x,y) in enumerate(UEs):
                f.write(f'    {{"pos": {{"x": {x}, "y": {y}}}, "demand": 1e6}}{"," if i < df.shape[0] or j < len(UEs)-1 else ""}\n')
            i+=1
        f.write("]\n")


# Only when in script mode
if __name__ == "__main__":
    from sys import argv

    if len(argv) < 2:
        print("Missing CSV file path to load argument")
        exit(0)

    df = load_ue_data(argv[1])

    # Count imputed squares
    # TODO

    # Count squares with less than 10 individuals
    # TODO

    # Export data to JSON
    save_ue_data(df, "./data/equipments/lyon_equipments_INSEE.json")
