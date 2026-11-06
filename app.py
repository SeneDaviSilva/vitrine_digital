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
    
    # Buscar dados da loja
    res_loja = supabase.table("vendedores").select("*").eq("id", loja_id).execute()
    
    if not res_loja.data:
        st.error("Loja não encontrada!")
        st.stop()
        
    loja = res_loja.data[0]
    st.title(f"🏪 {loja['nome_loja']}")
    st.caption("Faça sua encomenda direto pelo WhatsApp!")
    st.divider()
    
    # Buscar produtos desta loja específica
    res_prod = supabase.table("produtos").select("*").eq("vendedor_id", loja_id).eq("disponivel", True).execute()
    produtos = res_prod.data

    if not produtos:
        st.info("Nenhum produto disponível no momento.")
    else:
        for p in produtos:
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    img_url = p.get("imagem_url") if p.get("imagem_url") else "https://via.placeholder.com/150?text=Sem+Foto"
                    st.image(img_url, use_container_width=True)
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

            novo_whats = st.number_input(
                "WhatsApp para Pedidos (Apenas números com DDD) *",
                min_value=0,
                max_value=11,
                value=None,
                step=1,
                format="%d",
                help="Digite apenas os números, incluindo DDD (10 ou 11 dígitos)"
            )
            nova_senha = st.text_input("Crie uma Senha *", type="password")

            if st.form_submit_button("Criar Conta"):
                telefone = str(novo_whats)
                padrao_br = r'^\d{2}(?:9\d{4}|\d{4})\d{4}$'
                formato_valido = bool(re.match(padrao_br, telefone))

                if not (novo_nome and novo_email and novo_whats and nova_senha):
                    st.warning("Preencha todos os campos obrigatórios (*).")
                elif not formato_valido:
                    st.error("❌ Formato de telefone inválido! Digite 10 ou 11 números, incluindo o DDD. Exemplo: 11999998888.")
                else:
                    whats_limpo = telefone
                    try:
                        novo_vendedor = {
                            "nome_loja": novo_nome,
                            "email": novo_email.lower(),
                            "whatsapp": whats_limpo,
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

    URL_BASE = "https://vitrine-digitalm.streamlit.app" # URL real
    
    # Criptografa a URL com Base64
    id_string = f"vitrine_{vid}"
    id_criptografado = base64.urlsafe_b64encode(id_string.encode()).decode()
    
    link_vitrine = f"{URL_BASE}/?loja={id_criptografado}"
    st.success(f"**Seu Link Exclusivo para clientes:**\n\n{link_vitrine}")

    if st.button("Sair (Logout)"):
        del st.session_state["vendedor_id"]
        del st.session_state["nome_loja"]
        st.rerun()

    tab_cadastro, tab_gerenciamento = st.tabs(["Cadastrar Novo Item", "Meus Produtos"])

    with tab_cadastro:
        with st.form("form_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto *")
            descricao = st.text_area("Descrição (Ingredientes, tamanho)")
            preco = st.number_input("Preço (R$) *", value = None, min_value=0.0, step=0.50, format="%.2f")
            categoria = st.text_input("Categoria *")

            # Novo componente para upload direto do celular/PC
            imagem_arquivo = st.file_uploader("Foto do Produto", type=["png", "jpg", "jpeg", "webp"])

            if st.form_submit_button("Salvar Produto"):
                if not nome or not categoria or preco is None or preco <= 0:
                    st.error("Preencha os campos obrigatórios (*).")
                else:
                    imagem_url = None
                    upload_succeeded = imagem_arquivo is None

                    # Se o usuário enviou uma imagem
                    if imagem_arquivo is not None:
                        try:
                            # Gerar nome único para o arquivo usando timestamp
                            ext = imagem_arquivo.name.split(".")[-1]
                            nome_arquivo = f"{vid}_{int(time.time())}.{ext}"
                            bytes_data = imagem_arquivo.getvalue()

                            # Faz o upload para o bucket 'produtos' no Supabase
                            supabase.storage.from_("produtos").upload(
                                path=nome_arquivo,
                                file=bytes_data,
                                file_options={"content-type": imagem_arquivo.type}
                            )

                            # Gera o link público da foto salva
                            imagem_url = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                            upload_succeeded = True
                        except Exception as err:
                            st.error(f"Erro ao enviar foto: {err}")

                    if upload_succeeded:
                        # Salva o produto no banco com o link da foto gerado
                        supabase.table("produtos").insert({
                            "vendedor_id": vid,
                            "nome": nome,
                            "descricao": descricao,
                            "preco": preco,
                            "categoria": categoria,
                            "imagem_url": imagem_url,
                            "disponivel": True
                        }).execute()

                        st.success("Produto cadastrado com sucesso!")
                        st.rerun()

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
                st.divider()