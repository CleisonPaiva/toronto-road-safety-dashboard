"""
Análise 3: Colisões por bairro.

Nota metodológica: o spatial join calculado aqui (point-in-polygon,
usando os limites oficiais mais atuais de 158 bairros) diverge em ~17%
dos casos do campo NEIGHBOURHOOD_158 já presente no dataset de colisões.
Investigação mostrou que a divergência se concentra em blocos específicos
de bairros (não em ruído aleatório de borda), sugerindo que as duas fontes
usam versões diferentes do esquema de limites administrativos este
projeto usa a versão mais atual (fevereiro de 2026), obtida diretamente
da fonte oficial.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.ingestion.storage import load_processed, save_processed


def join_collisions_to_neighbourhoods(collisions_sdf: pd.DataFrame, neighbourhoods_sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Faz o spatial join: para cada colisão, identifica em qual bairro
    ela está localizada (predicado "within", sem buffer, já que bairros
    são polígonos mutuamente exclusivos sem sobreposição entre si).
    """
    joined = collisions_sdf.spatial.join(
        neighbourhoods_sdf[["AREA_NAME", "SHAPE"]],
        how="inner",
        op="within",
    )
    return joined


def validate_against_existing_field(joined: pd.DataFrame) -> pd.DataFrame:
    """
    Compara o bairro encontrado pelo spatial join (AREA_NAME) contra o
    campo NEIGHBOURHOOD_158 já existente no dataset de colisões, como
    checagem de sanidade. Ver nota metodológica no topo do arquivo sobre
    a divergência esperada de ~17%.
    """
    joined = joined.copy()
    joined["NOME_EXTRAIDO"] = joined["NEIGHBOURHOOD_158"].str.split("(").str[0].str.strip()

    matches = joined["AREA_NAME"].str.upper().str.strip() == joined["NOME_EXTRAIDO"].str.upper()
    print(f"Casos que batem com o campo NEIGHBOURHOOD_158 original: {matches.sum()} de {len(joined)} ({matches.mean()*100:.2f}%)")

    return joined


if __name__ == "__main__":
    collisions = load_processed("collisions_clean.pkl")
    neighbourhoods = load_processed("neighbourhoods_clean.pkl")

    within_neighbourhoods = join_collisions_to_neighbourhoods(collisions, neighbourhoods)

    unique_collisions = within_neighbourhoods["EVENT_UNIQUE_ID"].nunique()
    print(f"Colisões únicas dentro de bairros: {unique_collisions} de {len(collisions)} ({unique_collisions/len(collisions)*100:.2f}%)")

    duplicated_check = within_neighbourhoods.groupby("EVENT_UNIQUE_ID").size()
    print(f"Colisões que caíram em mais de um bairro: {(duplicated_check > 1).sum()}")

    within_neighbourhoods = validate_against_existing_field(within_neighbourhoods)

    save_processed(within_neighbourhoods, "collisions_by_neighbourhood.pkl")
