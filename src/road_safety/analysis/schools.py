"""
Análise 4: Colisões próximas a escolas.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.analysis.spatial_utils import buffer_in_meters
from road_safety.auth import get_gis
from road_safety.ingestion.storage import load_processed, save_processed

# Distância do buffer em metros ao redor de cada escola
BUFFER_METERS = 150


def buffer_schools(schools_sdf: pd.DataFrame, distance_m: float = BUFFER_METERS) -> pd.DataFrame:
    """
    Cria um buffer em metros ao redor de cada escola, reaproveitando
    a lógica compartilhada de reprojeção + buffer em spatial_utils.py.
    """
    gis = get_gis()
    buffered_geoms = buffer_in_meters(schools_sdf, distance_m, gis)

    buffered_sdf = schools_sdf.copy()
    buffered_sdf["SHAPE"] = buffered_geoms
    buffered_sdf.spatial.set_geometry("SHAPE")
    return buffered_sdf


def join_collisions_to_school_buffers(collisions_sdf: pd.DataFrame, buffered_schools_sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Faz o spatial join: para cada colisão, verifica se ela cai dentro
    do círculo de buffer de alguma escola.
    """
    joined = collisions_sdf.spatial.join(
        buffered_schools_sdf[["SHAPE", "NAME", "SCHOOL_LEVEL"]],
        how="inner",
        op="intersects",
    )
    return joined


if __name__ == "__main__":
    collisions = load_processed("collisions_clean.pkl")
    schools = load_processed("schools_clean.pkl")

    buffered_schools = buffer_schools(schools)
    near_school = join_collisions_to_school_buffers(collisions, buffered_schools)

    print(f"Colisões dentro do buffer de escolas: {len(near_school)} de {len(collisions)} ({len(near_school)/len(collisions)*100:.2f}%)")

    unique_collisions = near_school["EVENT_UNIQUE_ID"].nunique()
    print(f"Colisões únicas dentro do buffer de escolas: {unique_collisions} de {len(collisions)} ({unique_collisions/len(collisions)*100:.2f}%)")

    near_school = near_school.drop_duplicates(subset=["EVENT_UNIQUE_ID"])
    save_processed(near_school, "collisions_near_schools.pkl")
