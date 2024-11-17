import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import unidecode 
import requests
import re

# Mostrar diretório
print(os.getcwd())

# Mudar o diretório
os.chdir('C:/Users//Dados')

# Ler o CSV, mudar o codificador e o separador, converter para o tipo DataFrame
postos = pd.read_csv("dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv", encoding='latin1', sep=';', decimal=',').convert_dtypes()
postos = postos[['UF', 'MUNICIPIO', 'BANDEIRA']]

# Substitui as bandeiras conforme as especificações
postos['BANDEIRA'] = postos['BANDEIRA'].replace({
    'RAIZEN MIME': 'RAIZEN',
    'SABBÃ': 'RAIZEN',
    'RAIZEN': 'RAIZEN'
})

# Define as bandeiras de interesse
bandeiras_interesse = ['VIBRA', 'IPIRANGA', 'BANDEIRA BRANCA', 'RAIZEN']

# Substitui todas as bandeiras que não estão na lista de interesse por 'OTHERS'
postos['BANDEIRA'] = postos['BANDEIRA'].apply(lambda x: x if x in bandeiras_interesse else 'OTHERS')

# Agrupe por MUNICIPIO, contando as bandeiras
bandeira_count = postos.groupby(['MUNICIPIO', 'BANDEIRA']).size().reset_index(name='COUNT')

# Passo 1: Calcular o total de postos por município
total_count = bandeira_count.groupby('MUNICIPIO')['COUNT'].transform('sum')

# Passo 2: Calcular a quantidade relativa da bandeira
bandeira_count['RELATIVA'] = bandeira_count['COUNT'] / total_count


pivot_bandeira_count = bandeira_count.pivot_table(index=['MUNICIPIO'], 
                           columns='BANDEIRA', 
                           values='RELATIVA', 
                           fill_value=0)
# Carregar o shapefile dos municípios
mapa_municipios = gpd.read_file('C:/Users/jaotr/OneDrive/Documentos/GMF/CFA/BR_Municipios_2022/BR_Municipios_2022.shp')

# Definir cores usando colormaps do Matplotlib
cmap = plt.cm.get_cmap('Blues', len(bandeiras_interesse))  # Usar um colormap adequado

mapa_municipios['NM_MUN']

mapa_municipios['NM_MUN'] = mapa_municipios['NM_MUN'].str.lower()  # Converte para minúsculas
mapa_municipios['NM_MUN'] = mapa_municipios['NM_MUN'].apply(unidecode.unidecode)  # Remove acentos
mapa_municipios['NM_MUN'] = mapa_municipios['NM_MUN'].str.strip()  # Remove espaços em branco

bandeira_count['MUNICIPIO'] = bandeira_count['MUNICIPIO'].str.lower()  # Converte para minúsculas
bandeira_count['MUNICIPIO'] = bandeira_count['MUNICIPIO'].apply(unidecode.unidecode)  # Remove acentos
bandeira_count['MUNICIPIO'] = bandeira_count['MUNICIPIO'].str.strip()  # Remove espaços em branco

bandeiras_i = ['VIBRA', 'IPIRANGA', 'BANDEIRA BRANCA', 'RAIZEN', 'OTHERS']
# Gerar um gráfico para cada bandeira
for bandeira in bandeiras_i:
    # Unir os dados de concentração da bandeira com o shapefile
    temp_map = mapa_municipios.merge(bandeira_count[bandeira_count['BANDEIRA'] == bandeira], 
                                       how='left', left_on='NM_MUN', right_on='MUNICIPIO')
    
    # Preencher NaN com 0
    temp_map['RELATIVA'] = temp_map['RELATIVA'].fillna(0)

    # Plotar o mapa}
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    
    # Remover as fronteiras
    temp_map.plot(column='RELATIVA', ax=ax, legend=True,
                  legend_kwds={'label': f"Proporção Relativa da {bandeira}",
                               'orientation': "horizontal"},
                  cmap=cmap, missing_kwds={"color": "lightgrey"})  # Use o cmap aqui, YlGn, lightgrey

    # Ajustar título
    plt.title(f'Concentração da Bandeira {bandeira} nos Municípios do Brasil', fontsize=16)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.axis('off')  # Desligar os eixos para uma visualização limpa
    plt.savefig(f'concentracao_bandeira_{bandeira.lower()}.png', format='png', transparent=True, dpi=600)
    plt.show()

# Mostrar diretório
print(os.getcwd())

# Mudar o diretório
os.chdir('C:/Users//VBBR/Dados')

# Ler o CSV, mudar o codificador e o separador, converter para o tipo DataFrame
postos = pd.read_csv("dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv", encoding='latin1', sep=';', decimal=',').convert_dtypes()
postos = postos[['UF', 'MUNICIPIO', 'BANDEIRA']]

# Substitui as bandeiras conforme as especificações
postos['BANDEIRA'] = postos['BANDEIRA'].replace({
    'RAIZEN MIME': 'RAIZEN',
    'SABBÃ': 'RAIZEN',
    'RAIZEN': 'RAIZEN'
})

# Define as bandeiras de interesse
bandeiras_interesse = ['VIBRA', 'IPIRANGA', 'BANDEIRA BRANCA', 'RAIZEN']

# Substitui todas as bandeiras que não estão na lista de interesse por 'OTHERS'
postos['BANDEIRA'] = postos['BANDEIRA'].apply(lambda x: x if x in bandeiras_interesse else 'OTHERS')

# Agrupe por MUNICIPIO, contando as bandeiras
bandeira_count = postos.groupby(['MUNICIPIO', 'BANDEIRA']).size().reset_index(name='COUNT')

# Passo 1: Calcular o total de postos por município
total_count = bandeira_count.groupby('MUNICIPIO')['COUNT'].transform('sum')

# Passo 2: Calcular a quantidade relativa da bandeira
bandeira_count['RELATIVA'] = bandeira_count['COUNT'] / total_count


pivot_bandeira_count = bandeira_count.pivot_table(index=['MUNICIPIO'], 
                           columns='BANDEIRA', 
                           values='RELATIVA', 
                           fill_value=0)

pivot_bandeira_count.to_excel('C:/Users//pivot_bandeira_count.xlsx', index = True)


def get_ibge_data(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar a API do IBGE: {response.status_code}")

# Função para obter dados de população por município
def get_populacao_municipios():
    url = "https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93|10605?localidades=N6[all]"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar a API do IBGE: {response.status_code}")

# Função para obter dados de PIB por município
def get_pib_municipios():
    url = "https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021/variaveis/37?localidades=N6[all]"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar a API do IBGE: {response.status_code}")

 #Função para processar dados de população
def process_populacao_data(data):
    municipios = []
    for resultado in data[0]['resultados']:
        for serie in resultado['series']:
            municipio = serie['localidade']['nome'].lower().strip()
            populacao = serie['serie']['2022']
            municipios.append({
                'MUNICIPIO': municipio,
                'POPULACAO': populacao
            })
    return pd.DataFrame(municipios)

# Função para processar dados de PIB
def process_pib_data(data):
    municipios = []
    for resultado in data[0]['resultados']:
        for serie in resultado['series']:
            municipio = serie['localidade']['nome'].lower().strip()
            pib = serie['serie']['2021']
            municipios.append({
                'MUNICIPIO': municipio,
                'PIB': pib
            })
    return pd.DataFrame(municipios)

# Função para remover UF do nome do município
def remover_uf(nome):
    return re.sub(r' - [a-z]{2}$', '', nome)

# Obter e processar os dados de população
populacao_data = get_ibge_data("https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93|10605?localidades=N6[all]")
populacao_df = process_populacao_data(populacao_data)

# Obter e processar os dados de PIB
pib_data = get_ibge_data("https://servicodados.ibge.gov.br/api/v3/agregados/5938/periodos/2021/variaveis/37?localidades=N6[all]")
pib_df = process_pib_data(pib_data)

# Remover UF dos nomes dos municípios
populacao_df['MUNICIPIO'] = populacao_df['MUNICIPIO'].apply(remover_uf).apply(unidecode.unidecode).str.strip()
pib_df['MUNICIPIO'] = pib_df['MUNICIPIO'].apply(remover_uf).apply(unidecode.unidecode).str.strip()

# Carregar o DataFrame original
#pivot_bandeira_count = pd.read_excel('C:/Users/jaotr/OneDrive/Documentos/GMF/CFA/VBBR/Dados/your_original_data.xlsx')
pivot_bandeira_count = pivot_bandeira_count.reset_index()
pivot_bandeira_count['MUNICIPIO'] = pivot_bandeira_count['MUNICIPIO'].str.lower().apply(unidecode.unidecode).str.strip()

# Combinar dados de população
combined_df = pivot_bandeira_count.merge(populacao_df, on='MUNICIPIO', how='left')

# Combinar dados de PIB
combined_df = combined_df.merge(pib_df, on='MUNICIPIO', how='left')

# Multiplicando o PIB por 1000
# Multiplicando o PIB por 1000
combined_df['PIB'] = combined_df['PIB'].astype(float) * 1000

# Garantindo que a população também seja numérica
combined_df['POPULACAO'] = pd.to_numeric(combined_df['POPULACAO'], errors='coerce')

# Calculando o PIB per capita
combined_df['PIB per capita'] = combined_df['PIB'] / combined_df['POPULACAO']

# Exibindo as primeiras linhas para verificar o resultado
print(combined_df[['MUNICIPIO', 'PIB per capita']].head())

# Defina o número de municípios que você deseja analisar
n_top = 200  # Por exemplo, os 10 principais

# Analisando a Vibra
top_vibra = combined_df.nlargest(n_top, 'VIBRA')[['MUNICIPIO', 'POPULACAO', 'PIB', 'PIB per capita', 'VIBRA']]
print("Municípios com maior concentração de Vibra:")
print(top_vibra)
#top_vibra.to_excel('C:/Users/jaotr/OneDrive/Documentos/GMF/CFA/DataAnalysis/top_vibra.xlsx', index = False)

# Analisando a Ipiranga
top_ipiranga = combined_df.nlargest(n_top, 'IPIRANGA')[['MUNICIPIO', 'POPULACAO', 'PIB', 'PIB per capita', 'IPIRANGA']]
print("\nMunicípios com maior concentração de Ipiranga:")
print(top_ipiranga)
#top_ipiranga.to_excel('C:/Users/jaotr/OneDrive/Documentos/GMF/CFA/DataAnalysis/top_ipiranga.xlsx', index = False)

# Analisando a Raízen
top_raizen = combined_df.nlargest(n_top, 'RAIZEN')[['MUNICIPIO', 'POPULACAO', 'PIB', 'PIB per capita', 'RAIZEN']]
print("\nMunicípios com maior concentração de Raízen:")
print(top_raizen)

# Exibir as primeiras linhas do DataFrame combinado
print(combined_df.head())
