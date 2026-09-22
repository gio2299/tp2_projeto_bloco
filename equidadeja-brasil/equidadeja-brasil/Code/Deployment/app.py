import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# Configuração da página
st.set_page_config(page_title="EquidadeJá Brasil - TP2", layout="wide")

st.title("⚖️ EquidadeJá Brasil")
st.subheader("Painel de Equidade de Gênero no Mercado de Trabalho Brasileiro")

# --- 1. PERSISTÊNCIA VIA ESTADO DE SESSÃO (st.session_state) ---
if 'dados_usuario' not in st.session_state:
    st.session_state['dados_usuario'] = None

# --- 2. OTIMIZAÇÃO E PERFORMANCE VIA CACHE (@st.cache_data) ---
@st.cache_data
def carregar_noticias_csv():
    caminho = os.path.join('Data', 'Processed', 'noticias_equidade.csv')
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()

@st.cache_data
def carregar_corpus_txt():
    caminho = os.path.join('Data', 'Processed', 'corpus_noticias.txt')
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

@st.cache_data
def carregar_indicadores_ficticios():
    # Amostra de fallback do TP1 para os indicadores do World Bank
    caminho = os.path.join('Sample Data', 'amostra_indicadores_genero.csv')
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    # Dados de fallback caso o arquivo não exista
    dados = {
        'Ano': [2018, 2019, 2020, 2021, 2022],
        'Taxa de Participação Feminina (%)': [53.2, 54.1, 51.5, 52.8, 53.9],
        'Taxa de Participação Masculina (%)': [73.5, 73.8, 71.2, 72.0, 72.8]
    }
    return pd.DataFrame(dados)

# Carregamento dos dados
df_noticias = carregar_noticias_csv()
texto_corpus = carregar_corpus_txt()
df_indicadores = carregar_indicadores_ficticios()

# --- NAVEGAÇÃO POR ABAS (UNIFICANDO TP1 + TP2) ---
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "📈 Indicadores (World Bank)", 
    "📊 Notícias (Beautiful Soup)", 
    "☁️ Nuvem de Palavras", 
    "📁 Upload & Download", 
    "ℹ️ Sobre & ODS"
])

# --- ABA 1: INDICADORES (DO TP1) ---
with aba1:
    st.header("Indicadores Oficiais de Gênero no Mercado de Trabalho")
    st.caption("Fonte dos dados exibidos: Amostra Local / World Bank Open Data")
    
    st.subheader("Taxa de Participação na Força de Trabalho (%)")
    st.dataframe(df_indicadores, use_container_width=True)
    st.line_chart(df_indicadores.set_index('Ano'))

# --- ABA 2: NOTÍCIAS RASPADAS (DO TP2) ---
with aba2:
    st.header("Notícias Extraídas via Web Scraping (Beautiful Soup)")
    if not df_noticias.empty:
        st.metric("Total de manchetes coletadas", len(df_noticias))
        st.dataframe(df_noticias, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado em Data/Processed. Execute primeiro o script 'coletor_noticias.py'.")

# --- ABA 3: NUVEM DE PALAVRAS (DO TP2) ---
with aba3:
    st.header("Nuvem de Palavras dos Conteúdos Raspados")
    if texto_corpus:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto_corpus)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("Arquivo 'corpus_noticias.txt' não encontrado em Data/Processed.")

# --- ABA 4: UPLOAD & DOWNLOAD (DO TP2) ---
with aba4:
    st.header("Serviço de Upload e Download de Arquivos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Upload de Arquivo CSV")
        arquivo_enviado = st.file_uploader("Envie um CSV com indicadores complementares", type=["csv"])
        
        if arquivo_enviado is not None:
            st.session_state['dados_usuario'] = pd.read_csv(arquivo_enviado)
            st.success("Arquivo carregado e armazenado no Session State com sucesso!")

        if st.session_state['dados_usuario'] is not None:
            st.write("### Dados Enviados pelo Usuário:")
            st.dataframe(st.session_state['dados_usuario'])

    with col2:
        st.subheader("2. Download dos Dados")
        if not df_noticias.empty:
            csv_dados = df_noticias.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Notícias Coletadas (CSV)",
                data=csv_dados,
                file_name="noticias_equidade_consolidado.csv",
                mime="text/csv"
            )

# --- ABA 5: SOBRE O PROJETO ---
with aba5:
    st.markdown("""
    ### Sobre o Projeto
    O **EquidadeJá Brasil** consolida informações sobre a equidade de gênero no mercado de trabalho brasileiro.
    
    * **ODS Atendidos:** ODS 5 (Igualdade de Gênero) e ODS 8 (Trabalho Decente e Crescimento Econômico).
    * **Estrutura de Desenvolvimento:** Metodologia TDSP / CRISP-DM.
    """)