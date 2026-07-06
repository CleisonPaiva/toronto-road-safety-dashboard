"""
Testes de round-trip (salvar e carregar) do módulo storage.py.
"""
import pandas as pd

from road_safety.ingestion import storage


def test_save_and_load_processed_round_trip(tmp_path, monkeypatch):
    """
    Salvar e depois carregar um DataFrame deve devolver dados idênticos.
    Usa tmp_path (pasta temporária do pytest, apagada automaticamente)
    e monkeypatch para redirecionar DATA_PROCESSED_DIR, evitando
    escrever arquivos de teste na pasta real do projeto.
    """
    monkeypatch.setattr(storage, "DATA_PROCESSED_DIR", tmp_path)

    df_original = pd.DataFrame({"NOME": ["A", "B"], "VALOR": [1, 2]})

    storage.save_processed(df_original, "teste_round_trip.pkl")
    df_carregado = storage.load_processed("teste_round_trip.pkl")

    pd.testing.assert_frame_equal(df_original, df_carregado)
