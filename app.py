import urllib.parse
import hashlib
import streamlit as st
import time
import re
import base64
from supabase import create_client, Client

# Configuração da página móvel
st.set_page_config(page_title="Vitrine Digital", page_icon="🍲", layout="centered")

# Inicialização da Conexão com Supabase
def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# Função utilitária para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Estilização CSS
st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    .card-produto { border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin-bottom: 16px; background-color: #ffffff;}
    .preco-tag { color: #2e7d32; font-size: 1.25rem; font-weight: bold; }

    /* Força todas as imagens (Logo e Produtos) a serem quadradas e uniformes */
    div[data-testid="stImage"] img {
        object-fit: cover !important;
        aspect-ratio: 1 / 1 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODO 1: VITRINE PÚBLICA DO CLIENTE (Via parâmetro na URL)
# ---------------------------------------------------------
query_params = st.query_params
if "loja" in query_params:
    loja_hash = query_params["loja"]
    
    # Reverte o Base64 para descobrir o ID real
    try:
        decodificado = base64.urlsafe_b64decode(loja_hash.encode()).decode()
        loja_id = decodificado.replace("vitrine_", "") 
    except:
        st.error("❌ Link da loja inválido ou corrompido!")
        st.stop()
    
    # Buscar dados da loja
    res_loja = supabase.table("vendedores").select("*").eq("id", loja_id).execute()
    
    if not res_loja.data:
        st.error("Loja não encontrada!")
        st.stop()

    loja = res_loja.data[0]

    # --- Cabeçalho com Logo e Descrição ---
    col_logo, col_info = st.columns([1, 3])
    with col_logo:
        logo = loja.get("logo_url") if loja.get("logo_url") else "https://via.placeholder.com/150?text=Sua+Logo"
        # Renderiza a logo redonda usando HTML
        st.markdown(f'''
            <img src="{logo}" style="width:100%; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1; border: 3px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        ''', unsafe_allow_html=True)
    with col_info:
        st.title(f"🏪 {loja['nome_loja']}")
        if loja.get("descricao_loja"):
            st.write(loja["descricao_loja"])
        st.caption("Faça sua encomenda direto pelo WhatsApp!")
    st.divider()
    
    # Buscar produtos desta loja
    res_prod = supabase.table("produtos").select("*").eq("vendedor_id", loja_id).eq("disponivel", True).execute()
    produtos = res_prod.data

    if not produtos:
        st.info("Nenhum produto disponível no momento.")
    else:
        categorias = sorted(list(set(p["categoria"] for p in produtos)))
        
        for cat in categorias:
            st.header(f"📌 {cat}")
            produtos_cat = [p for p in produtos if p["categoria"] == cat]
            
            for cat in categorias:
                st.header(f"📌 {cat}")
            
                # 1. Filtra apenas os produtos desta categoria
                produtos_cat = [p for p in produtos if p["categoria"] == cat]
            
                # 2. NOVO: Ordena os produtos em ordem alfabética (A-Z) ignorando maiúsculas e minúsculas
                produtos_cat = sorted(produtos_cat, key=lambda x: x["nome"].lower())
            
                for p in produtos_cat:
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                    
                        with col1:
                            urls_img = [p.get("imagem_url"), p.get("imagem_url_2"), p.get("imagem_url_3")]
                            urls_validas = [u for u in urls_img if u]
                        
                            def render_img_clicavel(url):
                                st.markdown(f'''
                                    <a href="{url}" target="_blank">
                                     <img src="{url}" style="width:100%; border-radius: 10px; object-fit: cover; aspect-ratio: 1/1; cursor: pointer; border: 1px solid #eee;">
                                    </a>
                                ''', unsafe_allow_html=True)
                        
                            if urls_validas:
                                render_img_clicavel(urls_validas[0])
                            
                                if len(urls_validas) > 1:
                                    mini_cols = st.columns(len(urls_validas) - 1)
                                 for i, m_col in enumerate(mini_cols):
                                        with m_col:
                                            render_img_clicavel(urls_validas[i+1])
                            else:
                                st.markdown('''
                                    <img src="https://via.placeholder.com/150?text=Sem+Foto" style="width:100%; border-radius: 10px; object-fit: cover; aspect-ratio: 1/1; border: 1px solid #eee;">
                                ''', unsafe_allow_html=True)
                            
                        with col2:
                            st.subheader(p["nome"])
                            st.write(p.get("descricao", ""))
                            st.markdown(f"<span class='preco-tag'>R$ {p['preco']:.2f}</span>", unsafe_allow_html=True)
                        
                            telefone_limpo = "".join(filter(str.isdigit, str(loja["whatsapp"])))
                            texto_msg = f"Olá! Vi o produto *{p['nome']}* (R$ {p['preco']:.2f}) na sua vitrine e gostaria de fazer uma encomenda!"
                            wa_url = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(texto_msg)}"
                            st.link_button("💬 Quero encomendar", wa_url, use_container_width=True)
                st.divider()
                            
                    with col2:
                        st.subheader(p["nome"])
                        st.write(p.get("descricao", ""))
                        st.markdown(f"<span class='preco-tag'>R$ {p['preco']:.2f}</span>", unsafe_allow_html=True)
                        
                        telefone_limpo = "".join(filter(str.isdigit, str(loja["whatsapp"])))
                        texto_msg = f"Olá! Vi o produto *{p['nome']}* (R$ {p['preco']:.2f}) na sua vitrine e gostaria de fazer uma encomenda!"
                        wa_url = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(texto_msg)}"
                        st.link_button("💬 Quero encomendar", wa_url, use_container_width=True)
                st.divider()
    
    st.stop()

# ---------------------------------------------------------
# MODO 2: ÁREA ADMINISTRATIVA (Login e Painel da Vendedora)
# ---------------------------------------------------------

if "vendedor_id" not in st.session_state:
    st.title("🔐 Acesso Restrito - Vendedores")
    
    aba_login, aba_cadastro = st.tabs(["Fazer Login", "Criar minha Loja"])
    
    with aba_login:
        # O st.form cria uma "caixa" que envia os dados automaticamente ao apertar Enter
        with st.form("form_login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar", type="primary"):
                res = supabase.table("vendedores").select("*").eq("email", email_login.lower()).execute()
                
                if not res.data:
                    st.error("❌ E-mail não cadastrado. Verifique a digitação ou crie uma conta.")
                elif res.data[0]["senha"] != hash_senha(senha_login):
                    st.error("❌ Senha incorreta.")
                else:
                    st.session_state["vendedor_id"] = res.data[0]["id"]
                    st.session_state["nome_loja"] = res.data[0]["nome_loja"]
                    st.rerun()

    with aba_cadastro:
        with st.form("form_nova_loja"):
            novo_nome = st.text_input("Nome da sua Loja/Negócio *")
            novo_email = st.text_input("Seu E-mail *")

            novo_whats = st.text_input(
                "WhatsApp para Pedidos (Apenas números com DDD) *",
                max_chars=13,
                placeholder="5511999998888",
                help="Digite APENAS números, sem espaços ou traços."
            )
            nova_senha = st.text_input("Crie uma Senha *", type="password")

            if st.form_submit_button("Criar Conta"):
                if not (novo_nome and novo_email and novo_whats and nova_senha):
                    st.warning("Preencha todos os campos obrigatórios (*).")
                elif not novo_whats.isdigit():
                    st.error("❌ O campo de WhatsApp não aceita letras ou símbolos! Digite APENAS números.")
                elif len(novo_whats) < 10:
                    st.error("❌ Telefone incompleto! Faltou o DDD ou números do celular.")
                else:
                    res_email = supabase.table("vendedores").select("id").eq("email", novo_email.lower()).execute()
                    res_whats = supabase.table("vendedores").select("id").eq("whatsapp", novo_whats).execute()

                    if res_email.data:
                        st.error("❌ Este e-mail já está cadastrado em outra conta!")
                    elif res_whats.data:
                        st.error("❌ Este WhatsApp já está cadastrado em outra loja!")
                    else:
                        try:
                            novo_vendedor = {
                                "nome_loja": novo_nome,
                                "email": novo_email.lower(),
                                "whatsapp": novo_whats,
                                "senha": hash_senha(nova_senha)
                            }
                            supabase.table("vendedores").insert(novo_vendedor).execute()
                            st.success("Conta criada com sucesso! Vá para a aba 'Fazer Login' para entrar.")
                        except Exception as e:
                            st.error(f"Erro ao criar conta: {e}")

else:
    # --- PAINEL LOGADO ---
    vid = st.session_state["vendedor_id"]

    # Verifica e dispara notificações guardadas na memória
    if "msg_sucesso" in st.session_state:
        st.toast(st.session_state["msg_sucesso"], icon="✅")
        del st.session_state["msg_sucesso"]

    st.title(f"Painel: {st.session_state['nome_loja']}")

    # Mostra o link da vitrine
    URL_BASE = "https://vitrine-digital.streamlit.app"
    id_string = f"vitrine_{vid}"
    id_criptografado = base64.urlsafe_b64encode(id_string.encode()).decode()
    link_vitrine = f"{URL_BASE}/?loja={id_criptografado}"
    st.success(f"**Seu Link Exclusivo para clientes:**\n\n{link_vitrine}")

    if st.button("Sair (Logout)"):
        del st.session_state["vendedor_id"]
        del st.session_state["nome_loja"]
        st.rerun()

    # --- Janela Flutuante (Modal) de Edição de Produto ---
    @st.dialog("✏️ Editar Produto")
    def modal_editar_produto(item):
        with st.form(f"form_edit_{item['id']}", clear_on_submit=False):
            edit_nome = st.text_input("Nome", value=item['nome'])
            edit_desc = st.text_area("Descrição", value=item.get('descricao', ''))
            edit_preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f", value=float(item['preco']))
            edit_cat = st.text_input("Categoria", value=item['categoria'])
            
            st.caption("Para manter as fotos atuais, não envie nada. Para trocar, envie até 3 novas fotos.")
            edit_imagens = st.file_uploader(
                "Substituir Fotos (Máximo 3)", 
                type=["png", "jpg", "jpeg", "webp"], 
                accept_multiple_files=True, 
                key=f"up_{item['id']}"
            )
            
            if st.form_submit_button("Salvar Alterações"):
                if not edit_nome or not edit_cat or edit_preco <= 0:
                    st.error("Preencha Nome, Preço e Categoria.")
                elif len(edit_imagens) > 3:
                    st.error("❌ Envie no máximo 3 fotos!")
                else:
                    update_data = {
                        "nome": edit_nome,
                        "descricao": edit_desc,
                        "preco": edit_preco,
                        "categoria": edit_cat
                    }
                    
                    if edit_imagens:
                        urls_geradas = [None, None, None]
                        upload_succeeded = True
                        for idx, img_file in enumerate(edit_imagens):
                            try:
                                ext = img_file.name.split(".")[-1]
                                nome_arquivo = f"{vid}_edit_{int(time.time())}_{idx}.{ext}"
                                supabase.storage.from_("produtos").upload(
                                    path=nome_arquivo, 
                                    file=img_file.getvalue(), 
                                    file_options={"content-type": img_file.type}
                                )
                                urls_geradas[idx] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                            except Exception as err:
                                st.error(f"Erro ao atualizar foto: {err}")
                                upload_succeeded = False
                                break
                                
                        if upload_succeeded:
                            update_data["imagem_url"] = urls_geradas[0]
                            update_data["imagem_url_2"] = urls_geradas[1]
                            update_data["imagem_url_3"] = urls_geradas[2]
                    
                    supabase.table("produtos").update(update_data).eq("id", item['id']).execute()
                    st.session_state["msg_sucesso"] = "Alterações salvas com sucesso!"
                    st.rerun()

    tab_cadastro, tab_gerenciamento, tab_config = st.tabs(["Cadastrar Novo Item", "Meus Produtos", "⚙️ Configurações da Loja"])

    with tab_cadastro:
        with st.form("form_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto *")
            descricao = st.text_area("Descrição (Ingredientes, tamanho)")
            preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f", value=None)
            categoria = st.text_input("Categoria *")

            imagens_arquivo = st.file_uploader("Fotos do Produto (Máximo 3)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

            if st.form_submit_button("Salvar Produto"):
                if not nome or not categoria or preco is None or preco <= 0:
                    st.error("Preencha os campos obrigatórios (*).")
                elif len(imagens_arquivo) > 3:
                    st.error("❌ Você pode enviar no máximo 3 fotos por produto!")
                else:
                    urls_geradas = [None, None, None]
                    upload_succeeded = True

                    if imagens_arquivo:
                        for idx, img_file in enumerate(imagens_arquivo):
                            try:
                                ext = img_file.name.split(".")[-1]
                                nome_arquivo = f"{vid}_{int(time.time())}_{idx}.{ext}"
                                bytes_data = img_file.getvalue()

                                supabase.storage.from_("produtos").upload(
                                    path=nome_arquivo,
                                    file=bytes_data,
                                    file_options={"content-type": img_file.type}
                                )
                                urls_geradas[idx] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                            except Exception as err:
                                st.error(f"Erro ao enviar foto {idx+1}: {err}")
                                upload_succeeded = False
                                break

                    if upload_succeeded:
                        supabase.table("produtos").insert({
                            "vendedor_id": vid,
                            "nome": nome,
                            "descricao": descricao,
                            "preco": preco,
                            "categoria": categoria,
                            "imagem_url": urls_geradas[0],
                            "imagem_url_2": urls_geradas[1],
                            "imagem_url_3": urls_geradas[2],
                            "disponivel": True
                        }).execute()

                        st.session_state["msg_sucesso"] = "Novo produto cadastrado com sucesso!"
                        st.rerun()

    with tab_gerenciamento:
        # Removemos o .order("id") antigo para fazermos a ordenação inteligente no Python
        res_meus_prod = supabase.table("produtos").select("*").eq("vendedor_id", vid).execute()
        meus_produtos = res_meus_prod.data

        if not meus_produtos:
            st.info("Você ainda não tem produtos cadastrados.")
        else:
            # 1. Pega as categorias únicas e ordena de A a Z
            categorias_admin = sorted(list(set(p["categoria"] for p in meus_produtos)))
            
            for cat in categorias_admin:
                # Cria um mini-cabeçalho para cada categoria no painel
                st.markdown(f"#### 📁 {cat}") 
                
                # 2. Filtra os produtos dessa categoria e também ordena por nome (A-Z)
                produtos_cat_admin = [p for p in meus_produtos if p["categoria"] == cat]
                produtos_cat_admin = sorted(produtos_cat_admin, key=lambda x: x["nome"].lower())
                
                for item in produtos_cat_admin:
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                    with c1:
                        st.write(f"**{item['nome']}** - R$ {item['preco']:.2f}")
                    with c2:
                        novo_status = st.toggle("Ativo", value=item["disponivel"], key=f"status_{item['id']}")
                        if novo_status != item["disponivel"]:
                            supabase.table("produtos").update({"disponivel": novo_status}).eq("id", item["id"]).execute()
                            st.rerun()
                    with c3:
                        if st.button("✏️", key=f"btn_edit_{item['id']}", help="Editar Produto"):
                            modal_editar_produto(item)
                    with c4:
                        if st.button("🗑️", key=f"del_{item['id']}", help="Excluir Produto"):
                            supabase.table("produtos").delete().eq("id", item["id"]).execute()
                            st.rerun()
                    st.divider()

    with tab_config:
        res_minha_loja = supabase.table("vendedores").select("*").eq("id", vid).execute()
        dados_loja = res_minha_loja.data[0]

        with st.form("form_config_loja"):
            st.subheader("Personalizar Perfil da Vitrine")
            edit_nome_loja = st.text_input("Nome da Loja", value=dados_loja['nome_loja'])
            edit_desc_loja = st.text_area(
                "Apresentação / Descrição da Loja",
                value=dados_loja.get('descricao_loja', ''),
                help="Ex: Bolos artesanais feitos com carinho. Atendimento das 08h às 18h."
            )

            st.caption("Para manter a logo atual, não envie nada. Para trocar, envie uma nova foto.")
            edit_logo = st.file_uploader("Logo / Foto de Perfil da Loja", type=["png", "jpg", "jpeg", "webp"])

            if st.form_submit_button("Salvar Configurações"):
                update_loja = {
                    "nome_loja": edit_nome_loja,
                    "descricao_loja": edit_desc_loja
                }
                upload_succeeded = True

                if edit_logo:
                    try:
                        ext = edit_logo.name.split(".")[-1]
                        nome_arquivo = f"logo_{vid}_{int(time.time())}.{ext}"
                        supabase.storage.from_("produtos").upload(
                            path=nome_arquivo,
                            file=edit_logo.getvalue(),
                            file_options={"content-type": edit_logo.type}
                        )
                        update_loja["logo_url"] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                    except Exception as e:
                        st.error(f"Erro ao enviar logo: {e}")
                        upload_succeeded = False

                if upload_succeeded:
                    supabase.table("vendedores").update(update_loja).eq("id", vid).execute()
                    st.session_state["nome_loja"] = edit_nome_loja
                    st.session_state["msg_sucesso"] = "Perfil da loja atualizado com sucesso!"
                    st.rerun()