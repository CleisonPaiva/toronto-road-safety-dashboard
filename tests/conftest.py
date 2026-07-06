"""
Configuração compartilhada do pytest carregada automaticamente antes
de qualquer teste, evitando repetir sys.path.append em cada arquivo.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
