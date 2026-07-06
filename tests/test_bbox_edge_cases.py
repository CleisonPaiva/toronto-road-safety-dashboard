"""
Testes de caso de borda para o TORONTO_BBOX (limites exatos).
"""
import pandas as pd
from arcgis.geometry import Geometry

from road_safety.ingestion.cleaning import remove_invalid_geometries, TORONTO_BBOX


def test_point_exactly_on_boundary_is_kept():
    """
    Um ponto EXATAMENTE em cima do lon_max deve ser mantido, já que
    a condição usa <= (menor ou igual), não < (estritamente menor).
    """
    ponto_no_limite = Geometry({
        "x": TORONTO_BBOX["lon_max"],
        "y": 43.7,
        "spatialReference": {"wkid": 4326},
    })
    df = pd.DataFrame({"NOME": ["No limite"], "SHAPE": [ponto_no_limite]})
    df.spatial.set_geometry("SHAPE")

    resultado = remove_invalid_geometries(df)
    assert "No limite" in resultado["NOME"].tolist()


def test_point_slightly_beyond_boundary_is_removed():
    """Um ponto passando 0.001 grau do lon_max deve ser removido."""
    ponto_fora = Geometry({
        "x": TORONTO_BBOX["lon_max"] + 0.001,
        "y": 43.7,
        "spatialReference": {"wkid": 4326},
    })
    df = pd.DataFrame({"NOME": ["Além do limite"], "SHAPE": [ponto_fora]})
    df.spatial.set_geometry("SHAPE")

    resultado = remove_invalid_geometries(df)
    assert "Além do limite" not in resultado["NOME"].tolist()
