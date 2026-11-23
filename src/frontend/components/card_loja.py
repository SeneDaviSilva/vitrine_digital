import streamlit as st

from src.domain.entities.loja import Loja


def render_banner_link_vitrine(link_vitrine: str) -> None:
    st.markdown(
        f"""
        <div style="background-color: rgba(128,128,128,0.05); padding: 12px 16px; border-radius: 8px;
             border: 1px solid rgba(128,128,128,0.15); margin-bottom: 24px;">
            <span style="font-size: 0.85rem; opacity: 0.7;">Compartilhe este link com seus clientes:</span><br>
            <a href="{link_vitrine}" target="_blank" style="font-weight: 500; text-decoration: none; color: #2e7d32;">
                {link_vitrine}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card_loja_admin(loja: Loja) -> None:
    st.markdown(
        f"""
        <div style="padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); margin-bottom: 8px;">
            <div style="font-weight: 600;">{loja.nome_loja}</div>
            <div style="font-size: 0.85rem; opacity: 0.7;">WhatsApp: {loja.whatsapp}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )