import urllib.parse
import hashlib
import streamlit as st
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
    loja_id = query_params["loja"]
    
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
            if res.data and res.data[0]["senha"] == hash_senha(senha_login):
                st.session_state["vendedor_id"] = res.data[0]["id"]
                st.session_state["nome_loja"] = res.data[0]["nome_loja"]
                st.rerun()
            else:
                st.error("E-mail ou senha incorretos.")

    with aba_cadastro:
        with st.form("form_nova_loja"):
            novo_nome = st.text_input("Nome da sua Loja/Negócio *")
            novo_email = st.text_input("Seu E-mail *")
            novo_whats = st.text_input("WhatsApp para Pedidos (com DDD) *")
            nova_senha = st.text_input("Crie uma Senha *", type="password")
            
            if st.form_submit_button("Criar Conta"):
                if novo_nome and novo_email and novo_whats and nova_senha:
                    try:
                        novo_vendedor = {
                            "nome_loja": novo_nome,
                            "email": novo_email.lower(),
                            "whatsapp": novo_whats,
                            "senha": hash_senha(nova_senha)
                        }
                        supabase.table("vendedores").insert(novo_vendedor).execute()
                        st.success("Conta criada! Vá para a aba 'Fazer Login' para entrar.")
                    except Exception as e:
                        st.error(f"Erro ao criar conta: {e}")
                else:
                    st.warning("Preencha todos os campos.")

else:
    # --- PAINEL LOGADO ---
    vid = st.session_state["vendedor_id"]
    
    st.title(f"Painel: {st.session_state['nome_loja']}")
    
    # 1. Substitua o texto entre aspas pela URL REAL do seu site no ar:
    URL_BASE = "https://vitrine-digital.streamlit.app"

    # 2. O link_vitrine monta a URL com o ID da loja e o st.success exibe na tela:
    link_vitrine = f"{URL_BASE}/?loja={vid}"
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
            preco = st.number_input("Preço (R$) *", min_value=0.0, step=0.50, format="%.2f")
            categoria = st.text_input("Categoria *")
            imagem_url = st.text_input("URL da Foto")
            
            if st.form_submit_button("Salvar Produto"):
                if not nome or not categoria or preco <= 0:
                    st.error("Preencha os campos obrigatórios (*).")
                else:
                    supabase.table("produtos").insert({
                        "vendedor_id": vid,
                        "nome": nome,
                        "descricao": descricao,
                        "preco": preco,
                        "categoria": categoria,
                        "imagem_url": imagem_url if imagem_url else None,
                        "disponivel": True
                    }).execute()
                    st.success("Produto cadastrado na sua vitrine!")
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