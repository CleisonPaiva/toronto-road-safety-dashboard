"""
Configuração compartilhada do pytest — carregada automaticamente antes
de qualquer teste, evitando repetir sys.path.append em cada arquivo.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# setuptools precisa ser importado ANTES de qualquer módulo do arcgis:
# ele registra um atalho de compatibilidade para 'distutils', que foi
# removido da biblioteca padrão do Python a partir da versão 3.12, mas
# ainda é usado internamente por esta versão do arcgis (2.4.3).
import setuptools  # noqa: F401

# Força o registro do acessador .spatial no pandas.DataFrame — sem
# isso, df.spatial.* falha com AttributeError em ambientes limpos.
import arcgis.features.geo._accessor  # noqa: F401
