"""
Utilitários espaciais compartilhados entre as análises: reprojeção
em lotes e criação de buffer em metros. Funciona tanto para geometrias
de ponto (semáforos, escolas) quanto de linha (ciclovias).
"""
from arcgis.geometry import project as project_geometries


def project_in_chunks(geometries: list, in_sr: int, out_sr: int, gis, chunk_size: int = 500) -> list:
    """
    Reprojeta uma lista de geometrias em lotes menores, para evitar
    estourar o limite de tamanho de requisição do serviço de geometria
    da Esri (comum com polígonos/linhas complexas, com muitos vértices).
    """
    results = []
    for i in range(0, len(geometries), chunk_size):
        chunk = geometries[i:i + chunk_size]
        projected_chunk = project_geometries(
            geometries=chunk, in_sr=in_sr, out_sr=out_sr, gis=gis
        )
        results.extend(projected_chunk)
        print(f"  Reprojetados {min(i + chunk_size, len(geometries))}/{len(geometries)}...")
    return results


def buffer_in_meters(
    sdf,
    distance_m: float,
    gis,
    in_sr: int = 4326,
    metric_sr: int = 2952,
) -> list:
    """
    Cria um buffer em metros ao redor de cada geometria de um SEDF
    (funciona para pontos OU linhas), reprojetando para um CRS métrico,
    bufferizando localmente, e reprojetando o resultado de volta
    para o CRS original (in_sr).
    """
    geometries_native = list(sdf["SHAPE"])

    print(f"Reprojetando geometrias para EPSG:{metric_sr}...")
    projected = project_in_chunks(geometries_native, in_sr=in_sr, out_sr=metric_sr, gis=gis)

    buffered_metric = [geom.buffer(distance_m) for geom in projected]

    print(f"Reprojetando buffers de volta para EPSG:{in_sr}...")
    buffered_back = project_in_chunks(buffered_metric, in_sr=metric_sr, out_sr=in_sr, gis=gis)

    return buffered_back
