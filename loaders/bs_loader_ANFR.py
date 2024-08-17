#!/usr/bin/env python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from lib.gps import lyon_coords, gps_to_float, gps_dist

from os import path

def load_bs_ANFR_data(csv_filepath: str) -> pd.DataFrame:
    """Load the UE data from the CSV file and return a DataFrame with the relevant columns.
    These columns are:
    - latitude and longitude (ESP:4326 projection)
    - nom_com: Name of the city where the station is located
    - site_2g: 1 if the station is in 2G, 0 otherwise
    - site_3g: 1 if the station is in 3G, 0 otherwise
    - site_4g: 1 if the station is in 4G, 0 otherwise
    - site_5g: 1 if the station is in 5G, 0 otherwise

    This function also writes the parsed file to a new CSV one.

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

    df = pd.read_csv(csv_filepath, sep=';', header=0, encoding='utf-8', decimal=',')[
        [
            'coord',
            'statut'
        ]]

    # Remove multiple entries for the same pylon (different antennas)
    df.drop_duplicates(subset=['coord'], inplace=True)

    # Add a column with the gps coordinates converted to float coordinates
    df['float_coord'] = df['coord'].str.split(pat=" ").apply(lambda gps: (gps_to_float(gps[0]), gps_to_float(gps[1])))

    # Only select the pylons in Lyon
    print(lyon_coords)
    lyon_stations = df[
        ((df['float_coord'].str[0] >= lyon_coords["min"]["lat"]) & (df['float_coord'].str[0] <= lyon_coords["max"]["lat"])) &
        ((df['float_coord'].str[1] >= lyon_coords["min"]["lon"]) & (df['float_coord'].str[1] <= lyon_coords["max"]["lon"]))]

    print(lyon_stations.head())
    print(lyon_stations.shape[0])
    print("=========")

    # Split the float coordinates into two columns for practical use
    lyon_stations['latitude'] = lyon_stations['float_coord'].str[0].astype  (float)
    lyon_stations['longitude'] = lyon_stations['float_coord'].str[1].astype(float)

    print(lyon_stations.head())
    print(lyon_stations.shape[0])
    print("=========")

    # Export data for OpenStreetMap plotting
    lyon_stations.to_csv(path.join(path.dirname(csv_filepath), "lyon_stations_ANFR.csv"))

    return lyon_stations


def save_bs_ANFR_data(df: pd.DataFrame, output_filepath: str) -> None:
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

    df = load_bs_ANFR_data(argv[1])

    # PLOT antennas statuses stats
    status_counts = df['statut'].value_counts()
    tmp = pd.DataFrame(status_counts)
    status_counts = tmp.reset_index()
    status_counts.columns = ['statut', 'counts']

    x = status_counts['statut']
    y = status_counts['counts']

    sns.set_theme(font_scale=2.7)

    sns.barplot(x=x, y=y, hue=x, legend=False)

    plt.show()

    # Export JSON file
    save_bs_ANFR_data(df, "./data/towers/lyon_towers_ANFR.json")
