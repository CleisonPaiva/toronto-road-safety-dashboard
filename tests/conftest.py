"""
Configuração compartilhada do pytest — carregada automaticamente antes
de qualquer teste, evitando repetir sys.path.append em cada arquivo.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# Importar GeoAccessor/GeoSeriesAccessor registra o acessador .spatial
# no pandas.DataFrame  sem isso, df.spatial.* falha com AttributeError.
# Localmente isso "funcionava por acidente" (efeito colateral de outro
# import), mas em ambientes limpos (como o CI) precisa ser explícito.
from arcgis.features import GeoAccessor, GeoSeriesAccessor  # noqa: F401
