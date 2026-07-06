"""
Análise 1: Colisões próximas a semáforos.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.analysis.spatial_utils import buffer_in_meters
from road_safety.auth import get_gis
from road_safety.ingestion.storage import load_processed, save_processed

# Distância do buffer em metros ao redor de cada semáforo
BUFFER_METERS = 50


def buffer_signals(signals_sdf: pd.DataFrame, distance_m: float = BUFFER_METERS) -> pd.DataFrame:
    """
    Cria um buffer em metros ao redor de cada semáforo, reaproveitando
    a lógica compartilhada de reprojeção + buffer em spatial_utils.py.
    """
    gis = get_gis()
    buffered_geoms = buffer_in_meters(signals_sdf, distance_m, gis)

    buffered_sdf = signals_sdf.copy()
    buffered_sdf["SHAPE"] = buffered_geoms
    buffered_sdf.spatial.set_geometry("SHAPE")
    return buffered_sdf


def join_collisions_to_signal_buffers(collisions_sdf: pd.DataFrame, buffered_signals_sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Faz o spatial join: para cada colisão, verifica se ela cai dentro
    do círculo de buffer de algum semáforo.
    """
    joined = collisions_sdf.spatial.join(
        buffered_signals_sdf[["SHAPE"]],
        how="inner",
        op="intersects",
    )
    return joined


if __name__ == "__main__":
    collisions = load_processed("collisions_clean.pkl")
    signals = load_processed("traffic_signals_clean.pkl")

    buffered_signals = buffer_signals(signals)
    near_signal = join_collisions_to_signal_buffers(collisions, buffered_signals)

    print(f"Colisões dentro do buffer de semáforos: {len(near_signal)} de {len(collisions)} ({len(near_signal)/len(collisions)*100:.2f}%)")

    unique_collisions = near_signal["EVENT_UNIQUE_ID"].nunique()
    print(f"Colisões únicas dentro do buffer de semáforos: {unique_collisions} de {len(collisions)} ({unique_collisions/len(collisions)*100:.2f}%)")

    near_signal = near_signal.drop_duplicates(subset=["EVENT_UNIQUE_ID"])
    save_processed(near_signal, "collisions_near_signals.pkl")
