import os
from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class DatabaseConfig:
    supabase_url: str
    supabase_key: str

    @classmethod
    def carregar(cls) -> "DatabaseConfig":
        # Prioriza variáveis de ambiente (útil para rodar pytest no terminal)
        # e usa st.secrets como padrão no ambiente Streamlit
        url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")

        if not url or not key:
            raise RuntimeError("Credenciais SUPABASE_URL e SUPABASE_KEY não configuradas.")

        return cls(supabase_url=url, supabase_key=key)