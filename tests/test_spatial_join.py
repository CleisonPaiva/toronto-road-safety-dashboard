"""
Testes da lógica de spatial join (usada nas Análises 1, 2 e 4).
"""
import pandas as pd
from arcgis.geometry import Geometry


def test_point_inside_polygon_is_found_by_join():
    """Um ponto geometricamente dentro de um polígono deve aparecer no join."""
    poligono = Geometry({
        "rings": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]],
        "spatialReference": {"wkid": 4326},
    })
    buffer_sdf = pd.DataFrame({"SHAPE": [poligono]})
    buffer_sdf.spatial.set_geometry("SHAPE")

    ponto_dentro = Geometry({"x": 5, "y": 5, "spatialReference": {"wkid": 4326}})
    ponto_fora = Geometry({"x": 50, "y": 50, "spatialReference": {"wkid": 4326}})

    collisions_sdf = pd.DataFrame({
        "EVENT_UNIQUE_ID": ["dentro", "fora"],
        "SHAPE": [ponto_dentro, ponto_fora],
    })
    collisions_sdf.spatial.set_geometry("SHAPE")

    resultado = collisions_sdf.spatial.join(buffer_sdf, how="inner", op="intersects")

    assert "dentro" in resultado["EVENT_UNIQUE_ID"].tolist()
    assert "fora" not in resultado["EVENT_UNIQUE_ID"].tolist()
