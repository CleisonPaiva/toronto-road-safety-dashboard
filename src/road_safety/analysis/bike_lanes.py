"""
Análise 2: Colisões próximas a ciclovias.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.analysis.spatial_utils import buffer_in_meters
from road_safety.auth import get_gis
from road_safety.ingestion.storage import load_processed, save_processed

# Distância do buffer em metros ao redor de cada ciclovias
BUFFER_METERS = 25


def buffer_bike_lanes(bike_lanes_sdf: pd.DataFrame, distance_m: float = BUFFER_METERS) -> pd.DataFrame:
    """
    Cria um buffer em metros ao redor de cada ciclovia, reaproveitando
    a lógica compartilhada de reprojeção + buffer em spatial_utils.py.
    """
    gis = get_gis()
    buffered_geoms = buffer_in_meters(bike_lanes_sdf, distance_m, gis)

    buffered_sdf = bike_lanes_sdf.copy()
    buffered_sdf["SHAPE"] = buffered_geoms
    buffered_sdf.spatial.set_geometry("SHAPE")
    return buffered_sdf


def join_collisions_to_bike_lane_buffers(collisions_sdf: pd.DataFrame, buffered_bike_lanes_sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Faz o spatial join: para cada colisão, verifica se ela cai dentro
    do círculo de buffer de alguma ciclovias.
    """
    joined = collisions_sdf.spatial.join(
        buffered_bike_lanes_sdf[["SHAPE"]],
        how="inner",
        op="intersects",
    )
    return joined


if __name__ == "__main__":
    collisions = load_processed("collisions_clean.pkl")
    bike_lanes = load_processed("bike_lanes_clean.pkl")

    buffered_bike_lanes = buffer_bike_lanes(bike_lanes)
    near_bike_lane = join_collisions_to_bike_lane_buffers(collisions, buffered_bike_lanes)

    print(f"Colisões dentro do buffer de ciclovias: {len(near_bike_lane)} de {len(collisions)} ({len(near_bike_lane)/len(collisions)*100:.2f}%)")

    unique_collisions = near_bike_lane["EVENT_UNIQUE_ID"].nunique()
    print(f"Colisões únicas dentro do buffer de ciclovias: {unique_collisions} de {len(collisions)} ({unique_collisions/len(collisions)*100:.2f}%)")

    near_bike_lane = near_bike_lane.drop_duplicates(subset=["EVENT_UNIQUE_ID"])
    save_processed(near_bike_lane, "collisions_near_bike_lanes.pkl")
