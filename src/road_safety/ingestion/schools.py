"""
Módulo de ingestão dos dados de escolas de Toronto.
Fonte: GIS operacional da Prefeitura de Toronto (gis.toronto.ca),
camada "Schools " — dado vivo, editado continuamente
pela equipe de Transportation Services (diferente do Open Data
Portal, que tinha uma versão estática e não mais atualizada).
"""
import sys
from pathlib import Path

from arcgis.features import FeatureLayer

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.ingestion.storage import save_raw

# URL direta do serviço REST  diferente do Item ID que usamos em
# collisions.py, porque essa camada não está catalogada como um
# "Item" pesquisável no ArcGIS Hub, e sim exposta diretamente como
# serviço no servidor ArcGIS da própria Prefeitura
SCHOOLS_URL = "https://gis.toronto.ca/arcgis/rest/services/cot_geospatial28/FeatureServer/17"

FIELDS_OF_INTEREST = [
    "OBJECTID",
    "NAME",
    "ADDRESS_FULL",
    "BOARD_NAME",
    "SCHOOL_LEVEL",
    "SCHOOL_TYPE_DESC",
    "MUNICIPALITY"
]

def get_schools_layer() -> FeatureLayer:
    """Retorna o objeto FeatureLayer da camada de escolas."""
    return FeatureLayer(SCHOOLS_URL)


# TODO 1: escreva inspect_schema()  igual fez em collisions.py:
#   - nome da camada (layer.properties.name)
#   - tipo de geometria (layer.properties.geometryType)
#   - total de registros (layer.query(return_count_only=True))
#   - lista de campos (layer.properties.fields)
def inspect_schema():
    layer = get_schools_layer()
    print(f"Nome da camada: {layer.properties.name}")
    print(f"Tipo de geometria: {layer.properties.geometryType}")
    print(f"Total de registros no servidor: {layer.query(return_count_only=True)}")
    print(f"Campos disponíveis:")
    for field in layer.properties.fields:
        #print(f"  - {field.name} ({field.type})")
        print(f"  - {field['name']} ({field['type']})")


# TODO 2: escreva download_bike_lanes()  igual download_recent_collisions(),
#   mas SEM filtro de data (ciclovia não tem "data de ocorrência"
#   pense: faz sentido esse dataset ter um WHERE de data, ou não?).
#   Escolha os campos que fazem sentido trazer (dica: olhe o schema
#   que o TODO 1 vai te mostrar antes de decidir)
def download_schools():
    """Baixa os dados de escolas e retorna um Spatially Enabled DataFrame."""
    layer = get_schools_layer()
    # TODO 2: escreva a query para trazer todos os registros, mas só os campos de interesse
    #   (dica: use layer.query() com out_fields=FIELDS_OF_INTEREST)
    sdf = layer.query(
        out_fields=FIELDS_OF_INTEREST,
        out_sr=4326
        ).sdf

    print(f"{len(sdf)} escolas baixadas.")
    return sdf


if __name__ == "__main__":
    # TODO 3: chame inspect_schema() primeiro, veja o resultado,
    # DEPOIS decida os campos e escreva a chamada de download_schools()
    # e save_raw(..., "schools_raw.pkl")
    #inspect_schema()

    sdf = download_schools()
    save_raw(sdf, "schools_raw.pkl")
