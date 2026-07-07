"""
Módulo de exportação dos resultados finais para GeoJSON,
para consumo em mapas web.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.ingestion.storage import load_processed

DATA_GEOJSON_DIR = Path(__file__).resolve().parents[3] / "data" / "geojson"


def export_to_geojson(sdf, filename: str) -> Path:
    """
    Converte um Spatially Enabled DataFrame para um arquivo GeoJSON,
    usando o caminho SEDF -> FeatureSet -> GeoJSON .
    """
    DATA_GEOJSON_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_GEOJSON_DIR / filename

    feature_set = sdf.spatial.to_featureset()
    geojson_str = feature_set.to_geojson

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(geojson_str)

    print(f"Exportado: {output_path}")
    return output_path


if __name__ == "__main__":
    collisions_near_signals = load_processed("collisions_near_signals.pkl")
    export_to_geojson(collisions_near_signals, "collisions_near_signals.geojson")

    collisions_near_bike_lanes = load_processed("collisions_near_bike_lanes.pkl")
    export_to_geojson(collisions_near_bike_lanes, "collisions_near_bike_lanes.geojson")

    collisions_by_neighbourhood = load_processed("collisions_by_neighbourhood.pkl")
    export_to_geojson(collisions_by_neighbourhood, "collisions_by_neighbourhood.geojson")

    collisions_near_schools = load_processed("collisions_near_schools.pkl")
    export_to_geojson(collisions_near_schools, "collisions_near_schools.geojson")

    neighbourhoods_with_counts = load_processed("neighbourhoods_with_counts.pkl")
    export_to_geojson(neighbourhoods_with_counts, "neighbourhoods_with_counts.geojson")

