import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from lib.gps import lyon_coords, gps_dist

from os import path

def load_bs_ARCEP_data(csv_filepath: str) -> pd.DataFrame:
    """Load the UE data from the CSV file and return a DataFrame with the relevant columns.
    These columns are:
    - latitude and longitude (ESP:4326 projection)
    - nom_com: Name of the city where the station is located
    - site_2g: 1 if the station is in 2G, 0 otherwise
    - site_3g: 1 if the station is in 3G, 0 otherwise
    - site_4g: 1 if the station is in 4G, 0 otherwise
    - site_5g: 1 if the station is in 5G, 0 otherwise

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

    df = pd.read_csv(csv_filepath, sep=';', header=0, encoding='latin1', decimal=',')[
        [
            #'nom_op',# Opérateur
            'latitude', 'longitude',# Projection: WGS 1984 (EPSG:4326)
            'nom_com',# Nom de la commune de la station
            'site_2g',# Booléen: 1 si la station est en 2G, 0 sinon
            'site_3g',# Booléen: 1 si la station est en 3G, 0 sinon
            'site_4g',# Booléen: 1 si la station est en 4G, 0 sinon
            'site_5g' # Booléen: 1 si la station est en 5G, 0 sinon
        ]]

    lyon_stations = df.loc[df['nom_com'] == "Lyon"]
    # TODO: maybe select on GPS coords rather than city name

    print(lyon_stations.head())
    print(lyon_stations.shape[0])

    # Export data for OpenStreetMap plotting
    lyon_stations.to_csv(path.join(path.dirname(csv_filepath), "lyon_stations_ARCEP.csv"))

    return lyon_stations


def save_bs_ARCEP_data(df: pd.DataFrame, output_filepath: str) -> None:
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
            x = gps_dist(
                lyon_coords["min"]["lat"], lyon_coords["min"]["lon"],
                row['latitude'], lyon_coords["min"]["lon"]
            )
            y = gps_dist(
                lyon_coords["min"]["lat"], lyon_coords["min"]["lon"],
                lyon_coords["min"]["lat"], row["longitude"]
            )
            f.write(f'    {{"pos": {{"x": {x}, "y": {y}, "h": 30}}}}{"," if i < df.shape[0] else ""}\n')
            i+=1
        f.write("]\n")


# Only when in script mode
if __name__ == "__main__":
    from sys import argv

    if len(argv) < 2:
        print("Missing CSV file path to load argument")
        exit(0)

    df = load_bs_ARCEP_data(argv[1])

    # PLOT
    x = ["2G", "3G", "4G", "5G"]
    y = [df['site_2g'].sum(), df['site_3g'].sum(), df['site_4g'].sum(), df['site_5g'].sum()]

    sns.set_theme(font_scale=3.)

    sns.barplot(x=x, y=y, hue=x, legend=False)

    plt.show()

    # Export data to JSON
    save_bs_ARCEP_data(df, "./data/towers/lyon_towers_ARCEP.json")
