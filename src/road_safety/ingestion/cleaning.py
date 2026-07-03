"""
Módulo de limpeza dos dados de colisões antes das análises espaciais.
"""
from pathlib import Path
import pandas as pd

DATA_RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"
DATA_PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"

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


if __name__ == "__main__":
    raw = load_raw_collisions()
    clean = remove_invalid_coordinates(raw)
    save_processed(clean)
