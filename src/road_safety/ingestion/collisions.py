"""
Módulo de ingestão dos dados de colisões de trânsito em Toronto.
Fonte: Toronto Police Service Public Safety Data Portal (data.tps.ca),
dataset "Traffic Collisions Open Data (ASR-T-TBL-001)".
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Permite rodar este arquivo diretamente E ser importado como módulo,
# adicionando a pasta src/ ao caminho de busca de imports do Python
sys.path.append(str(Path(__file__).resolve().parents[2]))

from road_safety.auth import get_gis
from road_safety.ingestion.storage import save_raw

# Item ID é um identificador estável do dataset dentro do ArcGIS Online/Hub ,
# não muda mesmo que a URL REST interna do serviço seja reorganizada
COLLISIONS_ITEM_ID = "bc4c72a793014a55a674984ef175a6f3"

# Pasta onde os dados brutos ficam guardados localmente (fora do Git)
DATA_RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"

# Campos que realmente vamos usar nas 4 análises , evita trazer
# colunas desnecessárias e deixa o dataset mais leve
FIELDS_OF_INTEREST = [
    "OBJECTID",
    "EVENT_UNIQUE_ID",
    "OCC_DATE",
    "OCC_YEAR",
    "DIVISION",
    "FATALITIES",
    "INJURY_COLLISIONS",
    "HOOD_158",
    "NEIGHBOURHOOD_158",
    "LONG_WGS84",
    "LAT_WGS84",
    "AUTOMOBILE",
    "MOTORCYCLE",
    "PASSENGER",
    "BICYCLE",
    "PEDESTRIAN",
]


def get_collisions_layer():
    """
    Retorna o objeto FeatureLayer do dataset de colisões,
    sem baixar nenhum dado ainda , só a "referência" à camada.
    """
    gis = get_gis()

    # content.get() busca o Item pelo seu ID único no ArcGIS Online/Hub.
    # Funciona mesmo o item pertencendo a outra organização (torontops),
    # desde que o item seja público
    item = gis.content.get(COLLISIONS_ITEM_ID)

    # Um Item do tipo "Feature Service" pode conter várias camadas (layers).
    # Pegamos a primeira (índice 0) , é a mais comum pra datasets simples
    layer = item.layers[0]

    return layer


def inspect_schema():
    """
    Inspeciona os campos (colunas) disponíveis no dataset,
    sem baixar nenhuma feature , só metadados.
    """
    layer = get_collisions_layer()

    print(f"Nome da camada: {layer.properties.name}")
    print(f"Tipo de geometria: {layer.properties.geometryType}")
    print(f"Total de registros no servidor: {layer.query(return_count_only=True)}")
    print("\nCampos disponíveis:")
    for field in layer.properties.fields:
        print(f"  - {field['name']} ({field['type']})")


def download_recent_collisions(years_back: int = 2) -> pd.DataFrame:
    """
    Baixa colisões dos últimos `years_back` anos, filtrando no servidor
    (WHERE clause), e retorna um Spatially Enabled DataFrame (SEDF).

    Um SEDF é um pandas.DataFrame comum, mas com uma coluna especial
    'SHAPE' que guarda a geometria , permite usar tanto operações
    do pandas (groupby, filter) quanto operações espaciais (buffer, join).
    """
    layer = get_collisions_layer()

    # Constrói a data de corte e formata no padrão que o ArcGIS REST
    # espera dentro de uma cláusula WHERE: timestamp 'YYYY-MM-DD HH:MM:SS'
    cutoff_date = datetime.now() - timedelta(days=365 * years_back)
    where_clause = f"OCC_DATE >= timestamp '{cutoff_date.strftime('%Y-%m-%d')} 00:00:00'"

    print(f"Consultando colisões desde {cutoff_date.strftime('%Y-%m-%d')}...")

    # query() com out_sr=4326 garante que a geometria venha em
    # coordenadas lat/long padrão (WGS84) , o mesmo sistema usado
    # pelos campos LAT_WGS84/LONG_WGS84 do dataset
    sdf = layer.query(
        where=where_clause,
        out_fields=FIELDS_OF_INTEREST,
        out_sr=4326,
    ).sdf  # .sdf converte o resultado (FeatureSet) em Spatially Enabled DataFrame

    print(f"{len(sdf)} colisões baixadas.")
    return sdf




if __name__ == "__main__":
    sdf = download_recent_collisions(years_back=2)
    print(sdf.head())
    print(f"\nColunas: {list(sdf.columns)}")
    save_raw(sdf, "collisions_raw.pkl")
























# """
# Módulo de ingestão dos dados de colisões de trânsito em Toronto.
# Fonte: Toronto Police Service Public Safety Data Portal (data.tps.ca),
# dataset "Traffic Collisions Open Data (ASR-T-TBL-001)".
# """
# import sys  # usado para manipular o sys.path abaixo
# from pathlib import Path  # usado para resolver o caminho do arquivo atual
#
# # Permite rodar este arquivo diretamente E ser importado como módulo,
# # adicionando a pasta src/ ao caminho de busca de imports do Python
# sys.path.append(str(Path(__file__).resolve().parents[2]))
#
# from road_safety.auth import get_gis  # helper que autentica e retorna o cliente GIS (ArcGIS)
#
# # Item ID é um identificador estável do dataset dentro do ArcGIS Online/Hub ,
# # não muda mesmo que a URL REST interna do serviço seja reorganizada
# COLLISIONS_ITEM_ID = "bc4c72a793014a55a674984ef175a6f3"
#
#
# def get_collisions_layer():
#     """
#     Retorna o objeto FeatureLayer do dataset de colisões,
#     sem baixar nenhum dado ainda , só a "referência" à camada.
#     """
#     gis = get_gis()  # obtém a sessão autenticada com o ArcGIS Online/Hub
#
#     # content.get() busca o Item pelo seu ID único no ArcGIS Online/Hub.
#     # Funciona mesmo o item pertencendo a outra organização (torontops),
#     # desde que o item seja público
#     item = gis.content.get(COLLISIONS_ITEM_ID)
#
#     # Um Item do tipo "Feature Service" pode conter várias camadas (layers).
#     # Pegamos a primeira (índice 0) , é a mais comum pra datasets simples
#     layer = item.layers[0]
#
#     return layer  # devolve a referência à camada, pronta para queries posteriores
#
#
# def inspect_schema():
#     """
#     Inspeciona os campos (colunas) disponíveis no dataset,
#     sem baixar nenhuma feature , só metadados.
#     """
#     layer = get_collisions_layer()  # referência à camada de colisões
#
#     print(f"Nome da camada: {layer.properties.name}")  # nome legível da camada no servidor
#     print(f"Tipo de geometria: {layer.properties.geometryType}")  # ex.: esriGeometryPoint
#     print(f"Total de registros no servidor: {layer.query(return_count_only=True)}")  # query só de contagem, sem trazer dados
#     print("\nCampos disponíveis:")
#     for field in layer.properties.fields:  # percorre os metadados de cada coluna do dataset
#         print(f"  - {field['name']} ({field['type']})")  # nome do campo e seu tipo (ex.: esriFieldTypeString)
#
#
# if __name__ == "__main__":
#     # só executa a inspeção quando o arquivo é rodado diretamente,
#     # não quando importado como módulo por outro script
#     inspect_schema()
