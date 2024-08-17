#!/bin/bash

DL_FOLDER=downloads

# Create download directory
mkdir -p $DL_FOLDER

# Download data from ARCEP and INSEE
## ARCEP Antennas
if [ ! -e "$DL_FOLDER/all_antennas_ARCEP.csv" ]; then
    wget -nv -c --output-document=$DL_FOLDER/all_antennas_ARCEP.csv "https://files.data.gouv.fr/arcep_donnees/mobile/sites/2023_T3/2023_T3_sites_Metropole.csv"
else
    echo "ARCEP antennas file already downloaded"
fi
## ANFR Antennas
if [ ! -e "$DL_FOLDER/all_antennas_ANFR.csv" ]; then
    wget -nv -c --output-document=$DL_FOLDER/all_antennas_ANFR.csv "https://data.anfr.fr/d4c/api/records/2.0/downloadfile/format=csv&resource_id=88ef0887-6b0f-4d3f-8545-6d64c8f597da&use_labels_for_header=true&user_defined_fields=true"
else
    echo "ANFR antennas file already downloaded"
fi
## INSEE population density squares
if [ ! -e "$DL_FOLDER/pop_density.zip" ]; then
    wget -nv -c --output-document=$DL_FOLDER/pop_density.zip "https://www.insee.fr/fr/statistiques/fichier/7655475/Filosofi2019_carreaux_200m_csv.zip"
    # Extract only needed values from population density
    unzip -d $DL_FOLDER/ $DL_FOLDER/pop_density.zip
    7z x $DL_FOLDER/Filosofi2019_carreaux_200m_csv.7z -o$DL_FOLDER/
else
    echo "INSEE population density file already downloaded"
fi

# Extract only needed values from CSVs
echo "Extracting from ARCEP csv"
python -m loaders.bs_loader_ARCEP $DL_FOLDER/all_antennas_ARCEP.csv
echo "Extracting from ANFR csv"
python -m loaders.bs_loader_ANFR $DL_FOLDER/all_antennas_ANFR.csv
echo "Extracting from INSEE csv"
python -m loaders.ue_loader $DL_FOLDER/carreaux_200m_met.csv
echo "Generated JSON files"
