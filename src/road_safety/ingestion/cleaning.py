"""
Módulo de limpeza dos dados para evitar Null Island antes das análises espaciais.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.ingestion.storage import load_raw, save_processed

# Bounding box aproximado de Toronto (longitude min/max, latitude min/max)
TORONTO_BBOX = {
    "lon_min": -79.64,
    "lon_max": -79.12,
    "lat_min": 43.58,
    "lat_max": 43.85,
}

# sdf= Spatially Enabled DataFrame
def remove_invalid_geometries(sdf: pd.DataFrame, bbox: dict = TORONTO_BBOX) -> pd.DataFrame:
    """
    Remove registros cuja geometria (ponto OU linha) esteja fora do
    bounding box de Toronto. Funciona para qualquer tipo de geometria,
    porque usa .extent ao invés de colunas fixas como LONG_WGS84 e LAT_WGS84,
    por isso serve tanto para colisões (pontos) quanto ciclovias (linhas).
    """
    # Cria uma cópia do DataFrame para não modificar o original
    new_sdf = sdf.copy()
    # Adiciona uma coluna temporária 'extent' com a extensão da geometria
    new_sdf['extent'] = new_sdf.SHAPE.apply(lambda geom: geom.extent if geom else None)

    # Cria uma máscara booleana para filtrar registros dentro do bounding box
    mask = new_sdf['extent'].apply(lambda ext: (
        ext and
        ext[0] >= bbox['lon_min'] and
        ext[2] <= bbox['lon_max'] and
        ext[1] >= bbox['lat_min'] and
        ext[3] <= bbox['lat_max']
    ))

    # Calcula quantos registros foram removidos e imprime o resultado
    removed_rows = len(new_sdf) - mask.sum()
    print(f"Registros Totais: {len(new_sdf)}")
    print(f"Registros removidos por geometria inválida: {removed_rows}")

    return new_sdf.drop(columns=['extent'])[mask] # remove a coluna 'extent' antes de retornar o DataFrame filtrado


if __name__ == "__main__":
    # Colisões
    raw_collisions = load_raw("collisions_raw.pkl")
    clean_collisions = remove_invalid_geometries(raw_collisions)
    save_processed(clean_collisions, "collisions_clean.pkl")

    # Semáforos
    raw_signals = load_raw("traffic_signals_raw.pkl")
    clean_signals = remove_invalid_geometries(raw_signals)
    save_processed(clean_signals, "traffic_signals_clean.pkl")

    # Ciclovias
    raw_bike_lanes = load_raw("bike_lanes_raw.pkl")
    clean_bike_lanes = remove_invalid_geometries(raw_bike_lanes)
    save_processed(clean_bike_lanes, "bike_lanes_clean.pkl")
