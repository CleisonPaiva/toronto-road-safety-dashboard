"""
Módulo de limpeza dos dados de colisões antes das análises espaciais.
"""
from pathlib import Path
import sys
import pandas as pd

DATA_RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"
DATA_PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"
sys.path.append(str(Path(__file__).resolve().parents[2]))
from road_safety.ingestion.storage import load_raw, save_processed

# Bounding box aproximado de Toronto (longitude min/max, latitude min/max)
TORONTO_BBOX = {
    "lon_min": -79.64,
    "lon_max": -79.12,
    "lat_min": 43.58,
    "lat_max": 43.85,
}


def load_raw_collisions() -> pd.DataFrame:
    """Carrega o arquivo .pkl salvo pelo módulo de ingestão."""
    # TODO: ler o arquivo data/raw/collisions_raw.pkl com pandas
    # (dica: pd.read_pickle)
    raw_path = DATA_RAW_DIR / "collisions_raw.pkl"
    if not raw_path.exists():
        raise FileNotFoundError(f"Arquivo {raw_path} não encontrado. Rode o módulo de ingestão primeiro.")

    df = pd.read_pickle(raw_path)
    print(f" Dados brutos carregados de: {raw_path}")

    return df


def remove_invalid_coordinates(sdf: pd.DataFrame) -> pd.DataFrame:
    """
    Remove registros com coordenadas inválidas (fora do bounding box
    de Toronto, incluindo o caso de 'Null Island').

    Deve imprimir quantos registros foram removidos, para transparência.
    """
    # TODO:
    # 1. Descobrir como extrair 'x' (longitude) e 'y' (latitude) de cada
    #    linha da coluna SHAPE (dica: sdf.SHAPE.apply(lambda geom: ...)
    #    ou explore o que geom.x e geom.y retornam para um objeto
    #    de geometria do arcgis)
    # 2. Criar uma condição booleana: coordenada está DENTRO do TORONTO_BBOX?
    # 3. Filtrar o DataFrame mantendo só as linhas que passam nessa condição
    # 4. Calcular e imprimir quantas linhas foram removidas (antes vs depois)

    #No pandas, df['nome_qualquer'] = valores tanto cria (se não existe) quanto sobrescreve (se já existe) uma coluna, o mesmo operador faz as duas coisas, dependendo do contexto.
    # sdf['X'] = sdf.SHAPE.apply(lambda geom: geom.x if geom else None)

    # Criar uma condição booleana para filtrar coordenadas dentro do bounding box
    mask = (
        (sdf['LONG_WGS84'] >= TORONTO_BBOX['lon_min']) &
        (sdf['LONG_WGS84'] <= TORONTO_BBOX['lon_max']) &
        (sdf['LAT_WGS84'] >= TORONTO_BBOX['lat_min']) &
        (sdf['LAT_WGS84'] <= TORONTO_BBOX['lat_max'])
    )

    # Calcular quantas linhas foram removidas
    removed_rows = len(sdf) - mask.sum()
    print(f"Registros removidos: {removed_rows}")

    # Filtrar o DataFrame
    return sdf[mask]


def save_processed(sdf: pd.DataFrame, filename: str = "collisions_clean.pkl") -> Path:
    """Salva o DataFrame limpo em data/processed/."""
    # TODO: criar a pasta se não existir, e salvar com to_pickle
    # (mesma lógica do save_raw que já vimos em collisions.py)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_PROCESSED_DIR / filename
    sdf.to_pickle(output_path)
    print(f" Dados limpos salvos em: {output_path}")
    return output_path

def remove_invalid_geometries(sdf: pd.DataFrame, bbox: dict = TORONTO_BBOX) -> pd.DataFrame:
    """
    Remove registros cuja geometria (ponto OU linha) esteja fora do
    bounding box de Toronto. Funciona para qualquer tipo de geometria,
    porque usa .extent ao invés de colunas fixas como LONG_WGS84.
    """
    # TODO 1: para cada linha, extraia geom.extent (dica: .apply())
    #         Você vai ter uma Series onde cada elemento é uma tupla
    #         (xmin, ymin, xmax, ymax)
    new_sdf = sdf.copy()  # Cria uma cópia do DataFrame original para evitar modificar o original
    new_sdf['extent'] = new_sdf.SHAPE.apply(lambda geom: geom.extent if geom else None)
    #sdf['extent'] = sdf.SHAPE.apply(lambda geom: geom.extent if geom else None)

    # TODO 2: a partir dessa Series de tuplas, construa a condição
    #         booleana — pense: quais dos 4 valores (xmin, ymin, xmax, ymax)
    #         você precisa comparar com bbox['lon_min'], bbox['lon_max'],
    #         bbox['lat_min'], bbox['lat_max']?
    #         Dica: uma tupla pode ser "desempacotada" dentro de um apply,
    #         ou você pode extrair cada posição separadamente antes
    mask = new_sdf['extent'].apply(lambda ext: (
        ext and
        ext[0] >= bbox['lon_min'] and
        ext[2] <= bbox['lon_max'] and
        ext[1] >= bbox['lat_min'] and
        ext[3] <= bbox['lat_max']
    ))

    # TODO 3: calcule e imprima quantos registros foram removidos
    #         (mesmo padrão que você já fez antes)
    removed_rows = len(new_sdf) - mask.sum()
    print(f"Registros removidos por geometria inválida: {removed_rows}")

    # TODO 4: retorne o DataFrame filtrado
    return new_sdf.drop(columns=['extent'])[mask] # Remove a coluna 'extent' antes de retornar


if __name__ == "__main__":
    # Colisões (fluxo existente)
    #raw_collisions = load_raw_collisions()
    #clean_collisions = remove_invalid_coordinates(raw_collisions)
    #save_processed(clean_collisions)

    # Ciclovias
    raw_bike_lanes = load_raw("bike_lanes_raw.pkl")
    clean_bike_lanes = remove_invalid_geometries(raw_bike_lanes)
    save_processed(clean_bike_lanes, "bike_lanes_clean.pkl")
