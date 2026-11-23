from typing import Optional

from supabase import Client, create_client

from src.infra.database.database_config import DatabaseConfig


class SupabaseClientFactory:
    _instancia: Optional[Client] = None

    @classmethod
    def obter_cliente(cls) -> Client:
        if cls._instancia is None:
            config = DatabaseConfig.carregar()
            cls._instancia = create_client(config.supabase_url, config.supabase_key)
        return cls._instancia