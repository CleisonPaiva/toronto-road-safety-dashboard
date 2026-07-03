"""
Análise 1: Colisões próximas a semáforos.
"""
import sys
from pathlib import Path

import pandas as pd
from arcgis.geometry.functions import buffer as geodesic_buffer
from arcgis.geometry import LengthUnits

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.auth import get_gis
from road_safety.ingestion.storage import load_raw, save_processed, load_processed

BUFFER_METERS = 50

def project_in_chunks(geometries: list, in_sr: int, out_sr: int, gis, chunk_size: int = 500) -> list:
    """
    Reprojeta uma lista de geometrias em lotes menores, para evitar
    estourar o limite de tamanho de requisição do serviço de geometria
    da Esri (comum quando as geometrias são polígonos complexos,
    como buffers circulares com muitos vértices).
    """
    from arcgis.geometry import project as project_geometries

    results = []
    for i in range(0, len(geometries), chunk_size):
        chunk = geometries[i:i + chunk_size]
        projected_chunk = project_geometries(
            geometries=chunk, in_sr=in_sr, out_sr=out_sr, gis=gis
        )
        results.extend(projected_chunk)
        print(f"  Reprojetados {min(i + chunk_size, len(geometries))}/{len(geometries)}...")

    return results

def buffer_signals(signals_sdf: pd.DataFrame, distance_m: float = BUFFER_METERS) -> pd.DataFrame:
    """
    Cria um buffer em metros ao redor de cada semáforo, usando o método
    clássico: reprojeta para um CRS métrico, bufferiza localmente,
    depois reprojeta de volta para 4326. Processa em lotes para evitar
    estourar o limite de tamanho de requisição do serviço de geometria.
    """
    gis = get_gis()
    points_4326 = list(signals_sdf["SHAPE"])

    print("Reprojetando pontos para EPSG:2952...")
    points_2952 = project_in_chunks(points_4326, in_sr=4326, out_sr=2952, gis=gis)

    buffered_2952 = [pt.buffer(distance_m) for pt in points_2952]

    print("Reprojetando buffers de volta para EPSG:4326...")
    buffered_4326 = project_in_chunks(buffered_2952, in_sr=2952, out_sr=4326, gis=gis)

    buffered_sdf = signals_sdf.copy()
    buffered_sdf["SHAPE"] = buffered_4326
    buffered_sdf.spatial.set_geometry("SHAPE")

    return buffered_sdf


def join_collisions_to_signal_buffers(collisions_sdf: pd.DataFrame, buffered_signals_sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Faz o spatial join: para cada colisão, verifica se ela cai dentro
    do círculo de buffer de algum semáforo.
    """
    # how="inner" mantém só colisões que caíram dentro de algum buffer;
    # op="intersects" é o predicado espacial (colisão toca o polígono?)
    joined = collisions_sdf.spatial.join(
        buffered_signals_sdf[["SHAPE"]],
        how="inner",
        op="intersects",
    )
    return joined

if __name__ == "__main__":
    collisions = load_processed("collisions_clean.pkl")
    signals = load_raw("traffic_signals_raw.pkl")

    buffered_signals = buffer_signals(signals)
    near_signal = join_collisions_to_signal_buffers(collisions, buffered_signals)

    # TODO 1: Descubra quantas colisões (de um total) caíram dentro do
    #         buffer de 50m de algum semáforo. Imprima os dois números
    #         e a porcentagem (dica: len(near_signal) vs len(collisions))
    print(f"Colisões dentro do buffer de semáforos: {len(near_signal)} de {len(collisions)} ({len(near_signal)/len(collisions)*100:.2f}%)")
    #
    # TODO 2: Existe um problema sutil aqui: se um ponto de colisão está
    #         dentro da área de buffer de DOIS semáforos que se sobrepõem
    #         (comum em cruzamentos próximos), o spatial join pode gerar
    #         uma linha DUPLICADA para essa colisão (uma por semáforo).
    #         Investigue: len(near_signal) bate com o número de
    #         EVENT_UNIQUE_ID únicos em near_signal? Se não, pense em
    #         como remover essas duplicatas (dica: pandas tem um método
    #         chamado .drop_duplicates())
    #
    unique_collisions = near_signal["EVENT_UNIQUE_ID"].nunique()
    print(f"Colisões únicas dentro do buffer de semáforos: {unique_collisions} de {len(collisions)} ({unique_collisions/len(collisions)*100:.2f}%)")
    # TODO 3: Salve o resultado final (sem duplicatas) em
    #         data/processed/collisions_near_signals.pkl
    #         usando save_processed()
    near_signal.drop_duplicates(subset=["EVENT_UNIQUE_ID"])
    save_processed(near_signal, "collisions_near_signals.pkl")
