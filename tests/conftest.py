"""
Configuração compartilhada do pytest — carregada automaticamente antes
de qualquer teste, evitando repetir sys.path.append em cada arquivo.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# Importar o módulo arcgis.features
# já dispara o registro do acessador .spatial no pandas.DataFrame
import arcgis.features
