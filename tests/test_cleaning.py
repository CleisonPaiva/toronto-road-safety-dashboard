"""
Testes para o módulo de limpeza de geometrias.
"""
import sys
from pathlib import Path

import pandas as pd
from arcgis.geometry import Geometry

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from road_safety.ingestion.cleaning import remove_invalid_geometries, TORONTO_BBOX


def make_test_sdf():
    """
    Cria um Spatially Enabled DataFrame pequeno e controlado, com um
    ponto DENTRO de Toronto e um ponto FORA (Null Island), para testar
    a função de limpeza sem depender de nenhum dado real baixado.
    """
    # Geometry() cria um objeto de geometria "na mão", sem precisar
    # consultar nenhum servidor só um dicionário com x, y e o CRS
    ponto_valido = Geometry({"x": -79.38, "y": 43.65, "spatialReference": {"wkid": 4326}})
    ponto_invalido = Geometry({"x": 0.0, "y": 0.0, "spatialReference": {"wkid": 4326}})

    df = pd.DataFrame({
        "NOME": ["Ponto Válido (Toronto)", "Ponto Inválido (Null Island)"],
        "SHAPE": [ponto_valido, ponto_invalido],
    })
    df.spatial.set_geometry("SHAPE")
    return df


def test_remove_invalid_geometries_mantem_ponto_valido():
    """O ponto dentro do bbox de Toronto deve permanecer após a limpeza."""
    sdf = make_test_sdf()
    resultado = remove_invalid_geometries(sdf)

    assert "Ponto Válido (Toronto)" in resultado["NOME"].tolist()


def test_remove_invalid_geometries_remove_ponto_invalido():
    """O ponto fora do bbox (Null Island) deve ser removido pela limpeza."""
    sdf = make_test_sdf()
    resultado = remove_invalid_geometries(sdf)

    assert "Ponto Inválido (Null Island)" not in resultado["NOME"].tolist()
