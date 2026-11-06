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
# @st.cache_resource --- teste #
def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# Função utilitária para hash de senha (segurança básica)
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Estilização CSS
st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    .card-produto { border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin-bottom: 16px; background-color: #ffffff;}
    .preco-tag { color: #2e7d32; font-size: 1.25rem; font-weight: bold; }
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
        loja_id = decodificado.replace("vitrine_", "") # Remove a palavra e sobra só o número
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
        st.image(logo, use_container_width=True)
    with col_info:
        st.title(f"🏪 {loja['nome_loja']}")
        if loja.get("descricao_loja"):
            st.write(loja["descricao_loja"])
        st.caption("Faça sua encomenda direto pelo WhatsApp!")
    st.divider()
    
    # Buscar produtos desta loja específica
    res_prod = supabase.table("produtos").select("*").eq("vendedor_id", loja_id).eq("disponivel", True).execute()
    produtos = res_prod.data

    if not produtos:
        st.info("Nenhum produto disponível no momento.")
    else:
        # Pega as categorias únicas e as organiza em ordem alfabética
        categorias = sorted(list(set(p["categoria"] for p in produtos)))
        
        # Cria uma sessão (Header) para cada categoria
        for cat in categorias:
            st.header(f"📌 {cat}")
            
            # Filtra apenas os produtos desta categoria
            produtos_cat = [p for p in produtos if p["categoria"] == cat]
            
            for p in produtos_cat:
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Pega as 3 imagens e filtra as que não existem (None)
                        urls_img = [p.get("imagem_url"), p.get("imagem_url_2"), p.get("imagem_url_3")]
                        urls_validas = [u for u in urls_img if u]
                        
                        if urls_validas:
                            # Se tiver mais de uma, cria Abas (estilo carrossel mobile)
                            if len(urls_validas) > 1:
                                abas_img = st.tabs([f"Foto {i+1}" for i in range(len(urls_validas))])
                                for i, aba in enumerate(abas_img):
                                    with aba:
                                        st.image(urls_validas[i], use_container_width=True)
                            else:
                                st.image(urls_validas[0], use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/150?text=Sem+Foto", use_container_width=True)
                            
                    with col2:
                        st.subheader(p["nome"])
                        st.write(p.get("descricao", ""))
                        st.markdown(f"<span class='preco-tag'>R$ {p['preco']:.2f}</span>", unsafe_allow_html=True)
                        
                        telefone_limpo = "".join(filter(str.isdigit, str(loja["whatsapp"])))
                        texto_msg = f"Olá! Vi o produto *{p['nome']}* (R$ {p['preco']:.2f}) na sua vitrine e gostaria de fazer uma encomenda!"
                        wa_url = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(texto_msg)}"
                        st.link_button("💬 Quero encomendar", wa_url, use_container_width=True)
                    st.divider()
    
    # Encerra o script para não carregar a área de login/admin
    st.stop()

# ---------------------------------------------------------
# MODO 2: ÁREA ADMINISTRATIVA (Login e Painel da Vendedora)
# ---------------------------------------------------------

if "vendedor_id" not in st.session_state:
    st.title("🔐 Acesso Restrito - Vendedores")
    
    aba_login, aba_cadastro = st.tabs(["Fazer Login", "Criar minha Loja"])
    
    with aba_login:
        email_login = st.text_input("E-mail")
        senha_login = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary"):
            res = supabase.table("vendedores").select("*").eq("email", email_login.lower()).execute()
            
            # 1. Verifica se o e-mail existe no banco
            if not res.data:
                st.error("❌ E-mail não cadastrado. Verifique a digitação ou crie uma conta.")
            # 2. Se o e-mail existe, verifica se a senha bate
            elif res.data[0]["senha"] != hash_senha(senha_login):
                st.error("❌ Senha incorreta.")
            # 3. Se tudo estiver certo, faz o login
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
                max_chars=11,  # Trava o campo em no máximo 11 dígitos
                placeholder="11999998888",
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
                    # --- NOVO: Verifica se e-mail ou WhatsApp já existem no banco ---
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

    st.title(f"Painel: {st.session_state['nome_loja']}")

    URL_BASE = "https://vitrine-digital.streamlit.app" # URL real
    
    # Criptografa a URL com Base64
    id_string = f"vitrine_{vid}"
    id_criptografado = base64.urlsafe_b64encode(id_string.encode()).decode()
    
    link_vitrine = f"{URL_BASE}/?loja={id_criptografado}"
    st.success(f"**Seu Link Exclusivo para clientes:**\n\n{link_vitrine}")

    if st.button("Sair (Logout)"):
        del st.session_state["vendedor_id"]
        del st.session_state["nome_loja"]
        st.rerun()

    tab_cadastro, tab_gerenciamento, tab_config = st.tabs(["Cadastrar Novo Item", "Meus Produtos", "⚙️ Configurações da Loja"])

    with tab_cadastro:
        with st.form("form_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto *")
            descricao = st.text_area("Descrição (Ingredientes, tamanho)")
            preco = st.number_input("Preço (R$) *", min_value=0.0, step=0.50, format="%.2f", value=None)
            categoria = st.text_input("Categoria *")

            # Ativa o recebimento de múltiplos arquivos
            imagens_arquivo = st.file_uploader("Fotos do Produto (Máximo 3)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

            if st.form_submit_button("Salvar Produto"):
                if not nome or not categoria or preco is None or preco <= 0:
                    st.error("Preencha os campos obrigatórios (*).")
                elif len(imagens_arquivo) > 3:
                    st.error("❌ Você pode enviar no máximo 3 fotos por produto!")
                else:
                    # Prepara uma lista vazia para até 3 fotos
                    urls_geradas = [None, None, None]
                    upload_succeeded = True

                    # Loop para salvar cada foto separadamente
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
                        # Salva o produto gravando até 3 URLs
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

                        st.success("Produto cadastrado com sucesso!")

    with tab_gerenciamento:
        res_meus_prod = supabase.table("produtos").select("*").eq("vendedor_id", vid).order("id", desc=True).execute()
        meus_produtos = res_meus_prod.data

        if not meus_produtos:
            st.info("Você ainda não tem produtos cadastrados.")
        else:
            for item in meus_produtos:
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.write(f"**{item['nome']}** - R$ {item['preco']:.2f}")
                with c2:
                    novo_status = st.toggle("Ativo", value=item["disponivel"], key=f"status_{item['id']}")
                    if novo_status != item["disponivel"]:
                        supabase.table("produtos").update({"disponivel": novo_status}).eq("id", item["id"]).execute()
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        supabase.table("produtos").delete().eq("id", item["id"]).execute()
                        st.rerun()

                # --- NOVO: Painel Retrátil de Edição ---
                with st.expander("✏️ Editar Produto"):
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
                                st.error("Preencha os campos obrigatórios (Nome, Preço e Categoria).")
                            elif len(edit_imagens) > 3:
                                st.error("❌ Envie no máximo 3 fotos!")
                            else:
                                update_data = {
                                    "nome": edit_nome,
                                    "descricao": edit_desc,
                                    "preco": edit_preco,
                                    "categoria": edit_cat
                                }
                                upload_succeeded = True
                                # Se a vendedora enviou novas imagens, substituímos as antigas
                                if edit_imagens:
                                    urls_geradas = [None, None, None]
                                    for idx, img_file in enumerate(edit_imagens):
                                        try:
                                            ext = img_file.name.split(".")[-1]
                                            # Gera um nome único para a nova foto
                                            nome_arquivo = f"{vid}_edit_{int(time.time())}_{idx}.{ext}"
                                            bytes_data = img_file.getvalue()

                                            supabase.storage.from_("produtos").upload(
                                                path=nome_arquivo,
                                                file=bytes_data,
                                                file_options={"content-type": img_file.type}
                                            )
                                            urls_geradas[idx] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                                        except Exception as err:
                                            st.error(f"Erro ao atualizar foto {idx+1}: {err}")
                                            upload_succeeded = False
                                            break

                                    if upload_succeeded:
                                        update_data["imagem_url"] = urls_geradas[0]
                                        update_data["imagem_url_2"] = urls_geradas[1]
                                        update_data["imagem_url_3"] = urls_geradas[2]

                                if upload_succeeded:
                                    # Executa a atualização no banco de dados
                                    supabase.table("produtos").update(update_data).eq("id", item['id']).execute()
                                    st.success("Produto atualizado com sucesso!")
                                    st.rerun()
                st.divider()

                # --- Configurações da Loja ---
    with tab_config:
        # Puxa os dados atuais da vendedora no banco
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
                        # Reaproveitamos o bucket "produtos" para armazenar as logos
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
                    # Atualiza o banco e o nome salvo na sessão atual
                    supabase.table("vendedores").update(update_loja).eq("id", vid).execute()
                    st.session_state["nome_loja"] = edit_nome_loja
                    st.success("Perfil da loja atualizado com sucesso!")
                    st.rerun()