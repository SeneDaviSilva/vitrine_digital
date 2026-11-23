import streamlit as st

from src.domain.repositories.loja_repository import LojaRepository
from src.frontend.components.card_loja import render_card_loja_admin


def render_painel_admin(loja_repo: LojaRepository) -> None:
    st.markdown(
        """
        <div style="padding: 1rem 0;">
            <h2 style="margin-bottom: 0;">Vitrine Digital</h2>
            <p style="opacity: 0.6;">Administração Global do Sistema</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Sair"):
        st.session_state.pop("is_admin_master", None)
        st.rerun()

    st.subheader("Gerenciamento de Lojas")
    todas_lojas = loja_repo.listar_todas()

    if not todas_lojas:
        st.warning("Nenhuma loja cadastrada.")
        return

    lojas_dict = {f"{loja.nome_loja} ({loja.whatsapp})": loja for loja in todas_lojas}
    escolha = st.selectbox("Selecione a loja:", list(lojas_dict.keys()))

    if st.button("Gerenciar Loja", type="primary"):
        loja_alvo = lojas_dict[escolha]
        if loja_alvo.id:
            st.session_state["vendedor_id"] = str(loja_alvo.vendedor_id)
            st.session_state["loja_id"] = str(loja_alvo.id)
            st.rerun()

    st.divider()
    st.markdown(f"**Total de Lojas:** {len(todas_lojas)}")
    for loja in todas_lojas:
        render_card_loja_admin(loja)