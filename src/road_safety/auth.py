"""
Módulo responsável por autenticar no ArcGIS Online via OAuth 2.0.
Centraliza a lógica de conexão para ser reutilizada em toda a aplicação
(scripts de ingestão, análise e publicação).
"""
import os
from pathlib import Path

from arcgis.gis import GIS
from dotenv import load_dotenv


def get_gis() -> GIS:
    """
    Autentica no ArcGIS Online usando OAuth 2.0 (user authentication)
    e retorna um objeto GIS conectado.

    As credenciais (URL do portal e Client ID) vêm do arquivo config/.env,
    nunca hardcoded no código-fonte.
    """
    # Localiza o arquivo .env dentro da pasta config/, independente
    # de onde este script for executado a partir do projeto
    env_path = Path(__file__).resolve().parents[2] / "config" / ".env"
    load_dotenv(dotenv_path=env_path)

    portal_url = os.getenv("ARCGIS_PORTAL_URL")
    client_id = os.getenv("ARCGIS_CLIENT_ID")

    if not portal_url or not client_id:
        raise ValueError(
            "ARCGIS_PORTAL_URL ou ARCGIS_CLIENT_ID não encontrados. "
            "Verifique se o arquivo config/.env está preenchido corretamente."
        )

    # client_id aciona o fluxo OAuth 2.0: abre o navegador para login
    # e não expõe nenhuma senha no código
    gis = GIS(portal_url, client_id=client_id)

    return gis


# Bloco de teste manual: só executa quando rodamos este arquivo diretamente
# (python src/road_safety/auth.py), não quando ele é importado por outro módulo
if __name__ == "__main__":
    gis = get_gis()
    me = gis.users.me
    print(f"✅ Conectado com sucesso!")
    print(f"Usuário: {me.username}")
    print(f"Organização: {gis.properties.name}")
    print(f"Papel (role): {me.role}")
