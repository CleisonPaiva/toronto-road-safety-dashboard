"""
Configuração compartilhada do pytest — carregada automaticamente antes
de qualquer teste, evitando repetir sys.path.append em cada arquivo.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# A biblioteca arcgis usa "lazy loading" — importar arcgis.features
# sozinho não executa o submódulo interno que registra o acessador
# .spatial no pandas.DataFrame. Precisamos importar o submódulo exato
# onde esse registro acontece (via decorator), forçando sua execução.
import arcgis.features.geo._accessor  # noqa: F401
