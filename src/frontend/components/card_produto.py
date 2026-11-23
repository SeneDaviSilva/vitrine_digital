from typing import Callable

import streamlit as st

from src.domain.entities.produto import Produto


def _render_img_clicavel(url: str) -> None:
    st.markdown(
        f"""
        <a href="{url}" target="_blank">
            <img src="{url}" style="width:100%; border-radius: 8px; object-fit: cover; aspect-ratio: 1/1;
                 cursor: pointer; border: 1px solid rgba(128, 128, 128, 0.2);">
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_card_produto_vitrine(produto: Produto, on_adicionar: Callable[[Produto], None]) -> None:
    with st.container():
        col1, col2 = st.columns([1, 2])

        with col1:
            if produto.imagens_url:
                _render_img_clicavel(produto.imagens_url[0])
                if len(produto.imagens_url) > 1:
                    mini_cols = st.columns(len(produto.imagens_url) - 1)
                    for idx, m_col in enumerate(mini_cols):
                        with m_col:
                            _render_img_clicavel(produto.imagens_url[idx + 1])
            else:
                st.markdown(
                    """
                    <img src="https://via.placeholder.com/150?text=Produto"
                         style="width:100%; border-radius: 8px; object-fit: cover; aspect-ratio: 1/1;
                         border: 1px solid rgba(128, 128, 128, 0.2);">
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown(f"**{produto.nome}**")
            if produto.descricao:
                st.caption(produto.descricao)
            st.markdown(f"<span class='preco-tag'>R$ {produto.preco:.2f}</span>", unsafe_allow_html=True)

            if st.button("Adicionar", key=f"add_{produto.id}", use_container_width=True):
                on_adicionar(produto)

    st.markdown(
        "<hr style='margin: 1em 0; border: none; border-top: 1px solid rgba(128,128,128,0.2);'/>",
        unsafe_allow_html=True,
    )


def render_card_produto_admin(
    produto: Produto,
    on_toggle_status: Callable[[Produto, bool], None],
    on_editar: Callable[[Produto], None],
    on_excluir: Callable[[Produto], None],
) -> None:
    c1, c2, c3, c4 = st.columns([3.5, 1.5, 1, 1])

    with c1:
        img_url = produto.imagens_url[0] if produto.imagens_url else "https://via.placeholder.com/150?text=Sem+Foto"
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 8px;'>
                <img src="{img_url}" style="width: 44px; height: 44px; object-fit: cover; border-radius: 8px;
                     border: 1px solid rgba(128, 128, 128, 0.2);">
                <div style="line-height: 1.2;">
                    <div style="font-weight: 600;">{produto.nome}</div>
                    <div style="opacity: 0.7; font-size: 0.9rem;">R$ {produto.preco:.2f}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        visivel_atual = produto.esta_visivel()
        novo_status = st.toggle("Ativo", value=visivel_atual, key=f"status_{produto.id}")
        if novo_status != visivel_atual:
            on_toggle_status(produto, novo_status)

    with c3:
        if st.button("Editar", key=f"btn_edit_{produto.id}"):
            on_editar(produto)

    with c4:
        if st.button("Excluir", key=f"del_{produto.id}"):
            on_excluir(produto)

    st.divider()