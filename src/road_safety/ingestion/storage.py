"""
Módulo compartilhado de I/O para dados brutos e processados.
Usado por todos os módulos de ingestão (colisões, semáforos,
ciclovias, escolas) para evitar duplicar a lógica de salvar/carregar.
"""
from pathlib import Path

import pandas as pd

DATA_RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"
DATA_PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"


def save_raw(sdf: pd.DataFrame, filename: str) -> Path:
    """Salva um DataFrame em data/raw/, no formato pickle."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_RAW_DIR / filename
    sdf.to_pickle(output_path)
    print(f"Dados salvos em: {output_path}")
    return output_path


def load_raw(filename: str) -> pd.DataFrame:
    """Carrega um DataFrame de data/raw/."""
    path = DATA_RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo {path} não encontrado.")
    df = pd.read_pickle(path)
    print(f"Dados carregados de: {path}")
    return df

def load_processed(filename: str) -> pd.DataFrame:
    """Carrega um DataFrame de data/processed/."""
    path = DATA_PROCESSED_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo {path} não encontrado.")
    df = pd.read_pickle(path)
    print(f"Dados carregados de: {path}")
    return df


def save_processed(sdf: pd.DataFrame, filename: str) -> Path:
    """Salva um DataFrame em data/processed/."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_PROCESSED_DIR / filename
    sdf.to_pickle(output_path)
    print(f"Dados salvos em: {output_path}")
    return output_path
