from typing import Optional

import streamlit as st

from src.application.use_cases.auth.autenticar_vendedor import AutenticarVendedorUseCase
from src.application.use_cases.auth.redefinir_senha import RedefinirSenhaUseCase
from src.domain.exceptions import DomainError
from src.domain.repositories.loja_repository import LojaRepository
from src.infra.security.auth.autenticacao import TokenVitrineEncoder


@st.dialog("Redefinir Senha")
def _modal_redefinir_senha(redefinir_uc: RedefinirSenhaUseCase) -> None:
    st.write("Informe o e-mail e o WhatsApp cadastrados na loja para criar uma nova senha.")
    with st.form("form_esqueci_senha"):
        email = st.text_input("E-mail cadastrado")
        whatsapp = st.text_input("WhatsApp da loja (apenas números)", max_chars=13)
        nova_senha = st.text_input("Nova Senha", type="password")

        if st.form_submit_button("Alterar Senha", type="primary", use_container_width=True):
            try:
                redefinir_uc.executar(email=email, whatsapp=whatsapp, nova_senha=nova_senha)
                st.session_state["msg_sucesso"] = "Senha redefinida com sucesso."
                st.rerun()
            except DomainError as err:
                st.error(str(err))


def render_aba_login(
    autenticar_uc: AutenticarVendedorUseCase,
    redefinir_senha_uc: RedefinirSenhaUseCase,
    loja_repo: LojaRepository,
    admin_email: Optional[str],
    admin_senha: Optional[str],
) -> None:
    with st.form("form_login"):
        email_login = st.text_input("E-mail")
        senha_login = st.text_input("Senha", type="password")

        if st.form_submit_button("Acessar Painel", type="primary", use_container_width=True):
            if TokenVitrineEncoder.validar_admin_master(email_login, senha_login, admin_email, admin_senha):
                st.session_state["is_admin_master"] = True
                st.rerun()

            try:
                vendedor = autenticar_uc.executar(email=email_login, senha=senha_login)
                if not vendedor.id:
                    st.error("Erro ao recuperar identificação do vendedor.")
                    return

                loja = loja_repo.buscar_por_vendedor_id(vendedor.id)
                if not loja or not loja.id:
                    st.error("Nenhuma loja vinculada a esta conta.")
                    return

                st.session_state["vendedor_id"] = str(vendedor.id)
                st.session_state["loja_id"] = str(loja.id)
                st.rerun()
            except DomainError as err:
                st.error(str(err))

    if st.button("Esqueci minha senha", use_container_width=True):
        _modal_redefinir_senha(redefinir_senha_uc)