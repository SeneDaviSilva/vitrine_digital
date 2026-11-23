from typing import Callable

import streamlit as st

from src.domain.entities.loja import Loja


def render_header_auth() -> None:
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 1.5rem 0;">
            <h1 style="font-size: 2.5rem; font-weight: 700; letter-spacing: -1px; margin-bottom: 0;">
                Vitrine Digital.
            </h1>
            <p style="opacity: 0.6; font-size: 1.05rem; margin-top: 5px;">
                Plataforma de gestão para o seu negócio.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header_vitrine(loja: Loja, qtd_itens: int, on_abrir_carrinho: Callable[[], None]) -> None:
    col_logo, col_info = st.columns([1, 3])
    with col_logo:
        logo = loja.logo_url if loja.logo_url else "https://via.placeholder.com/150?text=Logo"
        st.markdown(
            f"""
            <img src="{logo}" style="width:100%; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1;
                 border: 1px solid rgba(128, 128, 128, 0.2); box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            """,
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown(
            f"<h2 style='margin-bottom: 0; padding-bottom: 0;'>{loja.nome_loja}</h2>",
            unsafe_allow_html=True,
        )
        if loja.descricao:
            st.markdown(
                f"<div style='opacity: 0.7; font-size: 0.95rem; margin-top: 4px; margin-bottom: 12px;'>{loja.descricao}</div>",
                unsafe_allow_html=True,
            )

        if st.button(f"Ver Carrinho ({qtd_itens})", type="primary", use_container_width=True):
            on_abrir_carrinho()


def render_header_lojista(loja: Loja, is_admin_master: bool, on_sair: Callable[[], None]) -> None:
    img_src = loja.logo_url if loja.logo_url else "https://via.placeholder.com/150?text=Loja"

    c_logo, c_titulo, c_sair = st.columns([1, 2.5, 1.5])
    with c_logo:
        st.markdown(
            f"""
            <img src="{img_src}" style="width: 100%; max-width: 75px; border-radius: 50%; object-fit: cover;
                 aspect-ratio: 1/1; border: 1px solid rgba(128, 128, 128, 0.2); margin-top: 5px;">
            """,
            unsafe_allow_html=True,
        )

    with c_titulo:
        st.markdown(
            f"<h2 style='margin-bottom: 0; padding-bottom: 0; margin-top: 0;'>{loja.nome_loja}</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='opacity: 0.6; font-size: 0.95rem; margin-bottom: 12px;'>Painel de Gestão</div>",
            unsafe_allow_html=True,
        )

    with c_sair:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        rotulo = "Sair (Admin)" if is_admin_master else "Sair"
        if st.button(rotulo, use_container_width=True):
            on_sair()