import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import unidecode
import requests
import re

# Show current directory
print(os.getcwd())

# Change directory
os.chdir('/path/to/data_directory')

# Read the CSV file, change encoding and separator, and convert to DataFrame type
stations = pd.read_csv("fuel_station_data.csv", encoding='latin1', sep=';', decimal=',').convert_dtypes()
stations = stations[['UF', 'MUNICIPIO', 'BANDEIRA']]

# Replace brands as specified
stations['BANDEIRA'] = stations['BANDEIRA'].replace({
    'RAIZEN MIME': 'RAIZEN',
    'SABBÃ': 'RAIZEN',
    'RAIZEN': 'RAIZEN'
})

# Define the brands of interest
brands_of_interest = ['VIBRA', 'IPIRANGA', 'BANDEIRA BRANCA', 'RAIZEN']

# Replace all brands not in the list of interest with 'OTHERS'
stations['BANDEIRA'] = stations['BANDEIRA'].apply(lambda x: x if x in brands_of_interest else 'OTHERS')

# Group by MUNICIPIO, counting the brands
brand_count = stations.groupby(['MUNICIPIO', 'BANDEIRA']).size().reset_index(name='COUNT')

# Step 1: Calculate the total number of stations per municipality
total_count = brand_count.groupby('MUNICIPIO')['COUNT'].transform('sum')

# Step 2: Calculate the relative count for each brand
brand_count['RELATIVE'] = brand_count['COUNT'] / total_count

# Pivot table with relative counts by municipality and brand
pivot_brand_count = brand_count.pivot_table(index=['MUNICIPIO'], 
                                            columns='BANDEIRA', 
                                            values='RELATIVE', 
                                            fill_value=0)

# Load the shapefile for municipalities
municipality_map = gpd.read_file('/path/to/municipality_shapefile.shp')

# Normalize municipality names
municipality_map['NM_MUN'] = municipality_map['NM_MUN'].str.lower()
municipality_map['NM_MUN'] = municipality_map['NM_MUN'].apply(unidecode.unidecode)
municipality_map['NM_MUN'] = municipality_map['NM_MUN'].str.strip()

brand_count['MUNICIPIO'] = brand_count['MUNICIPIO'].str.lower()
brand_count['MUNICIPIO'] = brand_count['MUNICIPIO'].apply(unidecode.unidecode)
brand_count['MUNICIPIO'] = brand_count['MUNICIPIO'].str.strip()

brands = ['VIBRA', 'IPIRANGA', 'BANDEIRA BRANCA', 'RAIZEN', 'OTHERS']

# Generate a map for each brand
for brand in brands:
    temp_map = municipality_map.merge(brand_count[brand_count['BANDEIRA'] == brand], 
                                      how='left', left_on='NM_MUN', right_on='MUNICIPIO')
    
    temp_map['RELATIVE'] = temp_map['RELATIVE'].fillna(0)

    # Plot the map
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    temp_map.plot(column='RELATIVE', ax=ax, legend=True,
                  legend_kwds={'label': f"Relative Proportion of {brand}",
                               'orientation': "horizontal"},
                  cmap='Blues', missing_kwds={"color": "lightgrey"})

    plt.title(f'Relative Concentration of {brand} in Brazilian Municipalities', fontsize=16)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.axis('off')
    plt.savefig(f'{brand.lower()}_concentration.png', format='png', transparent=True, dpi=600)
    plt.show()

# Process and analyze population and GDP data
def get_ibge_data(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error accessing IBGE API: {response.status_code}")

# Other functions for processing data follow...
# Function to process population data
def process_population_data(data):
    municipalities = []
    for result in data[0]['resultados']:
        for series in result['series']:
            municipality = series['localidade']['nome'].lower().strip()
            population = series['serie']['2022']
            municipalities.append({
                'MUNICIPIO': municipality,
                'POPULATION': population
            })
    return pd.DataFrame(municipalities)

# Function to process GDP data
def process_gdp_data(data):
    municipalities = []
    for result in data[0]['resultados']:
        for series in result['series']:
            municipality = series['localidade']['nome'].lower().strip()
            gdp = series['serie']['2021']
            municipalities.append({
                'MUNICIPIO': municipality,
                'GDP': gdp
            })
    return pd.DataFrame(municipalities)

# Function to remove state abbreviation from municipality names
def remove_state_abbreviation(name):
    return re.sub(r' - [a-z]{2}$', '', name)

# Fetch and process population data
population_data = get_ibge_data("https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93|10605?localidades=N6[all]")
population_df = process_population_data(population_data)

# Fetch and process GDP data
gdp_data = get_ibge_data("https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021/variaveis/37?localidades=N6[all]")
gdp_df = process_gdp_data(gdp_data)

# Clean municipality names
population_df['MUNICIPIO'] = population_df['MUNICIPIO'].apply(remove_state_abbreviation).apply(unidecode.unidecode).str.strip()
gdp_df['MUNICIPIO'] = gdp_df['MUNICIPIO'].apply(remove_state_abbreviation).apply(unidecode.unidecode).str.strip()

# Merge data with pivot table
pivot_brand_count = pivot_brand_count.reset_index()
pivot_brand_count['MUNICIPIO'] = pivot_brand_count['MUNICIPIO'].str.lower().apply(unidecode.unidecode).str.strip()

combined_df = pivot_brand_count.merge(population_df, on='MUNICIPIO', how='left')
combined_df = combined_df.merge(gdp_df, on='MUNICIPIO', how='left')

# Ensure GDP and population are numeric
combined_df['GDP'] = combined_df['GDP'].astype(float) * 1000
combined_df['POPULATION'] = pd.to_numeric(combined_df['POPULATION'], errors='coerce')

# Calculate GDP per capita
combined_df['GDP per capita'] = combined_df['GDP'] / combined_df['POPULATION']

# Analyze municipalities with the highest concentration for each brand
n_top = 200  # Number of top municipalities to analyze

# Top municipalities for Vibra
top_vibra = combined_df.nlargest(n_top, 'VIBRA')[['MUNICIPIO', 'POPULATION', 'GDP', 'GDP per capita', 'VIBRA']]
print("Municipalities with the highest concentration of Vibra:")
print(top_vibra)

# Top municipalities for Ipiranga
top_ipiranga = combined_df.nlargest(n_top, 'IPIRANGA')[['MUNICIPIO', 'POPULATION', 'GDP', 'GDP per capita', 'IPIRANGA']]
print("\nMunicipalities with the highest concentration of Ipiranga:")
print(top_ipiranga)

# Top municipalities for Raízen
top_raizen = combined_df.nlargest(n_top, 'RAIZEN')[['MUNICIPIO', 'POPULATION', 'GDP', 'GDP per capita', 'RAIZEN']]
print("\nMunicipalities with the highest concentration of Raízen:")
print(top_raizen)

# Display combined dataframe
print(combined_df.head())
