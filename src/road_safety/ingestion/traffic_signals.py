"""
Módulo de ingestão dos dados de semáforos de Toronto.
Fonte: City of Toronto Open Data Portal (open.toronto.ca), via API CKAN
— um sistema diferente do ArcGIS Hub usado pelo dataset de colisões.
"""
import sys
from pathlib import Path
import requests
sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.ingestion.storage import save_raw

CKAN_BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
DATASET_SLUG = "traffic-signals-tabular"
#DATASET_SLUG = "bikeways"


def get_dataset_resources() -> list[dict]:
    """Consulta os metadados do dataset e retorna a lista de resources."""
    url = f"{CKAN_BASE_URL}/api/3/action/package_show"
    params = {"id": DATASET_SLUG}
    response = requests.get(url, params=params)
    response.raise_for_status()
    package = response.json()
    resources = package["result"]["resources"]
    return resources


def inspect_metadata():
    """Imprime a taxa de atualização e última modificação do dataset."""
    url = f"{CKAN_BASE_URL}/api/3/action/package_show"
    params = {"id": DATASET_SLUG}
    response = requests.get(url, params=params)
    package = response.json()["result"]
    print(f"Taxa de atualização declarada: {package.get('refresh_rate')}")
    print(f"Última modificação dos metadados: {package.get('metadata_modified')}")


def get_signal_download_url(resource_id: str = "e331c953-7e49-418b-9eab-594881c76f33") -> str:
    """Consulta os metadados de um resource específico e retorna a URL de download."""
    url = f"{CKAN_BASE_URL}/api/3/action/resource_show"
    params = {"id": resource_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["result"]["url"]


def download_signals_sdf():
    """Baixa o GeoJSON de semáforos e converte para Spatially Enabled DataFrame."""
    from arcgis.features import FeatureSet

    download_url = get_signal_download_url()
    geojson_data = requests.get(download_url).json()
    feature_set = FeatureSet.from_geojson(geojson_data)
    sdf = feature_set.sdf
    return sdf


if __name__ == "__main__":
    resources = get_dataset_resources()
    #print(f"Dataset '{DATASET_SLUG}' tem {len(resources)} recursos:\n")
    for r in resources:
        print(f"  - {r['name']} | formato: {r['format']} | id: {r['id']}")

    print()
    inspect_metadata()

    #print()
    #sdf = download_signals_sdf()
    #print(f"Baixados {len(sdf)} semáforos com colunas: {sdf.columns.tolist()}")
    #save_raw(sdf, "traffic_signals_raw.pkl")
