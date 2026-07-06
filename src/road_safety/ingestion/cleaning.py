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
    "lon_min": -79.65,   # -79.6392649324429 arredondado para fora (~0.01)
    "lon_max": -79.10,   # -79.1152736124458 arredondado para fora (~0.01)
    "lat_min": 43.57,    # 43.5809960000775 arredondado para fora (~0.01)
    "lat_max": 43.87,    # 43.8554571861712 arredondado para fora (~0.01)
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

    # Bairros
    raw_neighbourhoods = load_raw("neighbourhoods_raw.pkl")
    clean_neighbourhoods = remove_invalid_geometries(raw_neighbourhoods)
    save_processed(clean_neighbourhoods, "neighbourhoods_clean.pkl")

    # Escolas
    raw_schools = load_raw("schools_raw.pkl")
    clean_schools = remove_invalid_geometries(raw_schools)
    save_processed(clean_schools, "schools_clean.pkl")

    """
    # Investigação temporária: quais bairros foram removidos?
    raw_neighbourhoods = load_raw("neighbourhoods_raw.pkl")
    raw_neighbourhoods['extent'] = raw_neighbourhoods.SHAPE.apply(lambda g: g.extent if g else None)
    for idx, row in raw_neighbourhoods.iterrows():
        ext = row['extent']
        if not (ext and ext[0] >= TORONTO_BBOX['lon_min'] and ext[2] <= TORONTO_BBOX['lon_max']
                and ext[1] >= TORONTO_BBOX['lat_min'] and ext[3] <= TORONTO_BBOX['lat_max']):
            print(row['AREA_NAME'], ext)

    print()
    # Carrega os bairros SEM nenhuma filtragem ainda
    extents = raw_neighbourhoods['SHAPE'].apply(lambda g: g.extent if g else None).dropna()

    xmin = min(e[0] for e in extents)
    ymin = min(e[1] for e in extents)
    xmax = max(e[2] for e in extents)
    ymax = max(e[3] for e in extents)

    print(f"lon_min: {xmin}, lon_max: {xmax}, lat_min: {ymin}, lat_max: {ymax}")
    """
