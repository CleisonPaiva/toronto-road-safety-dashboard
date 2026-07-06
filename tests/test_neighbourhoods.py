"""
Testes para a validação de bairros (Análise 3).
"""
import pandas as pd

from road_safety.analysis.neighbourhoods import validate_against_existing_field


def test_extracts_name_without_numeric_code():
    """O nome extraído de NEIGHBOURHOOD_158 não deve conter o código entre parênteses."""
    df = pd.DataFrame({
        "AREA_NAME": ["Rustic"],
        "NEIGHBOURHOOD_158": ["Rustic (28)"],
    })
    resultado = validate_against_existing_field(df)

    assert resultado["NOME_EXTRAIDO"].iloc[0] == "Rustic"


def test_identifies_correct_match():
    """Quando AREA_NAME e o nome extraído são iguais, deve contar como match."""
    df = pd.DataFrame({
        "AREA_NAME": ["Weston"],
        "NEIGHBOURHOOD_158": ["Weston (113)"],
    })
    resultado = validate_against_existing_field(df)

    match = resultado["AREA_NAME"].str.upper().str.strip() == resultado["NOME_EXTRAIDO"].str.upper()
    assert match.iloc[0] == True


def test_identifies_real_divergence():
    """Quando os bairros são de fato diferentes (caso documentado), não deve dar match."""
    df = pd.DataFrame({
        "AREA_NAME": ["Brookhaven-Amesbury"],
        "NEIGHBOURHOOD_158": ["Rustic (28)"],
    })
    resultado = validate_against_existing_field(df)

    match = resultado["AREA_NAME"].str.upper().str.strip() == resultado["NOME_EXTRAIDO"].str.upper()
    assert match.iloc[0] == False
