from uuid import uuid4

import streamlit as st

from src.application.use_cases.auth.cadastrar_vendedor import CadastrarVendedorUseCase
from src.application.use_cases.loja.cadastrar_loja import CadastrarLojaUseCase
from src.domain.entities.loja import Loja
from src.domain.exceptions import DomainError, DuplicidadeError
from src.domain.repositories.loja_repository import LojaRepository


def render_aba_cadastro(
    cadastrar_vendedor_uc: CadastrarVendedorUseCase,
    cadastrar_loja_uc: CadastrarLojaUseCase,
    loja_repo: LojaRepository,
) -> None:
    with st.form("form_nova_loja"):
        novo_nome_loja = st.text_input("Nome da Loja *")
        novo_email = st.text_input("E-mail *")
        novo_whats = st.text_input(
            "WhatsApp (Apenas números com DDD) *",
            max_chars=13,
            placeholder="5511999998888",
        )
        nova_senha = st.text_input("Senha *", type="password")

        if st.form_submit_button("Cadastrar", type="primary", use_container_width=True):
            try:
                # Valida regras de formato e unicidade da loja antes de criar o vendedor
                loja_preview = Loja(
                    vendedor_id=uuid4(),
                    nome_loja=novo_nome_loja,
                    whatsapp=novo_whats,
                )
                if loja_repo.buscar_por_nome(loja_preview.nome_loja):
                    raise DuplicidadeError("Já existe uma loja com este nome.")
                if loja_repo.buscar_por_whatsapp(loja_preview.whatsapp):
                    raise DuplicidadeError("WhatsApp já cadastrado.")

                vendedor = cadastrar_vendedor_uc.executar(
                    nome=novo_nome_loja,
                    email=novo_email,
                    senha=nova_senha,
                )
                if not vendedor.id:
                    st.error("Erro inesperado ao criar conta.")
                    return

                cadastrar_loja_uc.executar(
                    vendedor_id=vendedor.id,
                    nome_loja=novo_nome_loja,
                    whatsapp=novo_whats,
                )
                st.success("Conta criada. Vá para a aba 'Entrar'.")
            except DomainError as err:
                st.error(str(err))