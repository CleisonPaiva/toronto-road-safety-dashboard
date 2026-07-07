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

def aggregate_collision_counts(within_neighbourhoods: pd.DataFrame, neighbourhoods_sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Conta quantas colisões caíram em cada bairro, e junta essa contagem
    de volta ao DataFrame de polígonos .
    """

    # TODO 1: faça uma contagem de colisões por bairro, usando o campo
    # "AREA_NAME" do DataFrame de colisões (within_neighbourhoods),
    count = within_neighbourhoods.groupby("AREA_NAME").size().reset_index(name="COLLISION_COUNT")

    # TODO 2: faça um merge do DataFrame de contagem com o DataFrame de
    # bairros (neighbourhoods_sdf), usando "AREA_NAME" como chave,
    # garantindo que todos os bairros sejam incluídos (mesmo sem colisões)
    result = pd.merge(neighbourhoods_sdf, count, on="AREA_NAME", how="left")

    # TODO 3: preencha os valores NaN da coluna COLLISION_COUNT com 0
    result["COLLISION_COUNT"] = result["COLLISION_COUNT"].fillna(0)

    return result


if __name__ == "__main__":
    collisions = load_processed("collisions_clean.pkl")
    neighbourhoods = load_processed("neighbourhoods_clean.pkl")

    within_neighbourhoods = join_collisions_to_neighbourhoods(collisions, neighbourhoods)

    unique_collisions = within_neighbourhoods["EVENT_UNIQUE_ID"].nunique()
    print(f"Colisões únicas dentro de bairros: {unique_collisions} de {len(collisions)} ({unique_collisions/len(collisions)*100:.2f}%)")

    duplicated_check = within_neighbourhoods.groupby("EVENT_UNIQUE_ID").size()
    print(f"Colisões que caíram em mais de um bairro: {(duplicated_check > 1).sum()}")

    within_neighbourhoods = validate_against_existing_field(within_neighbourhoods)

    neighbourhoods_with_counts = aggregate_collision_counts(within_neighbourhoods, neighbourhoods)
    save_processed(neighbourhoods_with_counts, "neighbourhoods_with_counts.pkl")

    save_processed(within_neighbourhoods, "collisions_by_neighbourhood.pkl")

    print(neighbourhoods_with_counts[["AREA_NAME", "COLLISION_COUNT"]].sort_values("COLLISION_COUNT", ascending=False).head(10))
