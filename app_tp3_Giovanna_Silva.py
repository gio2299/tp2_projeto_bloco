"""
app_tp3_giovanna_silva.py
------------------------------------------------------------------
Teste de Performance 3 — Desenvolvimento de Aplicações com Streamlit
Tema: Dados de Turismo do portal Data.Rio (Prefeitura do Rio de Janeiro)
Autora: Giovanna Silva
 
Declaração de uso de Inteligência Artificial:
Este trabalho foi desenvolvido com apoio da ferramenta de IA Claude
(Anthropic), utilizada para geração e revisão de trechos de código
Python/Streamlit e para depuração de erros durante o desenvolvimento.
Todas as decisões de estrutura, dados utilizados e validação final do
funcionamento da aplicação foram revisadas pela autora. Uso citado
conforme item "Uso de IAs: Sinal Verde" do enunciado do TP3.
------------------------------------------------------------------
"""
 
import io
import time
 
import pandas as pd
import plotly.express as px
import streamlit as st
 
# ------------------------------------------------------------------
# CONFIGURAÇÃO GERAL DA PÁGINA
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Turismo no Rio de Janeiro | Data.Rio",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ------------------------------------------------------------------
# ITEM 9 - SESSION STATE
# Inicializa todas as chaves que vamos persistir durante a navegação
# ------------------------------------------------------------------
DEFAULTS = {
    "df": None,                       # dataframe carregado (cacheado)
    "bg_color": "#0E1117",            # cor de fundo escolhida
    "font_color": "#FAFAFA",          # cor de fonte escolhida
    "radio_choice": "Todas as colunas",
    "checkbox_cols": [],
    "dropdown_col": None,
    "dropdown_values": [],
    "last_filename": None,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value
 
 
# ------------------------------------------------------------------
# ITEM 7 - COLOR PICKER (aplica cores personalizadas via CSS)
# ------------------------------------------------------------------
def aplicar_tema(bg_color: str, font_color: str) -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {bg_color};
            color: {font_color};
        }}
        .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{
            color: {font_color};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg_color};
        }}
 
        /* Ao gerar PDF/imprimir (Ctrl+P), o navegador costuma descartar o
        fundo colorido mas mantém a cor da fonte personalizada, o que pode
        deixar o texto invisível (ex.: fonte branca em página branca).
        Este bloco força um visual sempre legível na impressão/PDF,
        independente das cores escolhidas no color picker. */
        @media print {{
            .stApp, .stApp p, .stApp span, .stApp label, .stApp li,
            .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
                background-color: #FFFFFF !important;
                color: #000000 !important;
            }}
            section[data-testid="stSidebar"] {{
                background-color: #FFFFFF !important;
            }}
            /* Evita que gráficos, tabelas e métricas sejam cortados no
            meio por uma quebra de página ao gerar o PDF. */
            div[data-testid="stPlotlyChart"],
            div[data-testid="stDataFrame"],
            div[data-testid="stMetric"],
            div[data-testid="stVerticalBlockBorderWrapper"],
            .js-plotly-plot {{
                break-inside: avoid;
                page-break-inside: avoid;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
 
 
# ------------------------------------------------------------------
# LIMPEZA AUTOMÁTICA
# Muitos datasets de portais governamentais (como o Data.Rio) vêm com
# linhas de título/metadados antes do cabeçalho real, células mescladas
# e colunas numéricas "sujas". As funções abaixo detectam a linha de
# cabeçalho de verdade e convertem colunas numéricas automaticamente.
# ------------------------------------------------------------------
def _fracao_numerica(valores) -> float:
    serie = pd.Series(valores)
    if serie.empty:
        return 0.0
    return pd.to_numeric(serie, errors="coerce").notna().mean()
 
 
def _detectar_linha_cabecalho(bruto: pd.DataFrame) -> int:
    """Procura, nas primeiras linhas, onde a tabela de dados começa de
    fato: a linha de cabeçalho é a linha logo ANTES da primeira linha
    predominantemente numérica e bem preenchida."""
    n_linhas, n_colunas = bruto.shape
    for i in range(min(n_linhas, 30)):
        linha = bruto.iloc[i].dropna()
        if linha.empty:
            continue
        preenchimento = len(linha) / max(n_colunas, 1)
        if preenchimento >= 0.4 and _fracao_numerica(linha.tolist()) >= 0.5:
            return max(i - 1, 0)
    return 0
 
 
def _nomes_colunas_unicos(nomes: list) -> list:
    """Garante nomes de coluna únicos e legíveis, mesmo com células
    mescladas (valores vazios) ou nomes repetidos."""
    contagem: dict = {}
    resultado = []
    for pos, nome in enumerate(nomes):
        nome_limpo = "" if pd.isna(nome) else str(nome).strip()
        if not nome_limpo:
            nome_limpo = f"Coluna_{pos + 1}"
        if nome_limpo in contagem:
            contagem[nome_limpo] += 1
            nome_limpo = f"{nome_limpo}_{contagem[nome_limpo]}"
        else:
            contagem[nome_limpo] = 0
        resultado.append(nome_limpo)
    return resultado
 
 
def _tentar_converter_numerico(serie: pd.Series) -> pd.Series:
    """Tenta converter uma coluna para número; se falhar em formato
    direto, tenta o padrão brasileiro (milhar '.', decimal ',')."""
    validos = serie.notna().sum()
    if validos == 0:
        return serie
 
    direto = pd.to_numeric(serie, errors="coerce")
    taxa_direto = direto.notna().sum() / validos
    if taxa_direto >= 0.7:
        return direto
 
    limpo = (
        serie.astype(str).str.strip()
        .str.replace(r"\.", "", regex=True)
        .str.replace(",", ".", regex=False)
    )
    alternativo = pd.to_numeric(limpo, errors="coerce")
    taxa_alt = alternativo.notna().sum() / validos
    return alternativo if taxa_alt > taxa_direto else serie
 
 
def limpar_dataframe(bruto: pd.DataFrame) -> pd.DataFrame:
    """Recebe um DataFrame 'cru' (lido sem cabeçalho) e devolve uma
    versão limpa: cabeçalho real detectado, colunas nomeadas e tipos
    numéricos corrigidos quando possível."""
    bruto = bruto.dropna(axis=0, how="all").dropna(axis=1, how="all").reset_index(drop=True)
    if bruto.empty:
        return bruto
 
    idx_cabecalho = _detectar_linha_cabecalho(bruto)
    cabecalho = _nomes_colunas_unicos(bruto.iloc[idx_cabecalho].tolist())
 
    dados = bruto.iloc[idx_cabecalho + 1:].reset_index(drop=True)
    dados.columns = cabecalho
    dados = dados.dropna(axis=0, how="all").reset_index(drop=True)
 
    for coluna in dados.columns:
        dados[coluna] = _tentar_converter_numerico(dados[coluna])
 
    return dados
 
 
# ------------------------------------------------------------------
# ITEM 8 - CACHE
# Evita reprocessar o arquivo XLS a cada interação do usuário
# ------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def carregar_dados(arquivo_bytes: bytes, nome_arquivo: str) -> pd.DataFrame:
    """Lê um arquivo .xls/.xlsx (mesmo com cabeçalho 'sujo') e devolve
    um DataFrame limpo e pronto para análise.
 
    Escolhe o engine de leitura de acordo com a extensão:
    - .xls  -> xlrd   (pip install xlrd)
    - .xlsx -> openpyxl (pip install openpyxl)
 
    Alguns portais de dados abertos (como o Data.Rio) exportam arquivos com
    extensão .xls que na verdade são uma tabela HTML. Nesse caso, o xlrd
    falha e recorremos a pd.read_html como alternativa.
    """
    extensao = nome_arquivo.lower().rsplit(".", 1)[-1]
    engine = "xlrd" if extensao == "xls" else "openpyxl"
 
    try:
        bruto = pd.read_excel(io.BytesIO(arquivo_bytes), engine=engine, header=None)
    except ImportError as e:
        raise ImportError(
            f"Faltando dependência para ler arquivos .{extensao}. "
            f"Rode: pip install {engine}"
        ) from e
    except Exception:
        # Fallback: o arquivo pode ser uma tabela HTML disfarçada de .xls
        # (comum em exports de portais de dados abertos governamentais).
        try:
            tabelas = pd.read_html(io.BytesIO(arquivo_bytes), header=None)
            bruto = max(tabelas, key=len)  # pega a maior tabela encontrada
        except Exception as e2:
            raise ValueError(
                "Não foi possível ler o arquivo como Excel nem como HTML. "
                "Verifique se o arquivo não está corrompido ou tente "
                "reexportá-lo do portal Data.Rio."
            ) from e2
 
    return limpar_dataframe(bruto)
 
 
@st.cache_data(show_spinner=False)
def converter_para_xlsx(df: pd.DataFrame) -> bytes:
    """Converte um DataFrame filtrado em bytes de arquivo XLSX para download."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="dados_filtrados")
    return buffer.getvalue()
 
 
# ------------------------------------------------------------------
# BARRA LATERAL
# ------------------------------------------------------------------
with st.sidebar:
    st.title("🏖️ Painel de Controle")
 
    # ---------- ITEM 2: UPLOAD DE ARQUIVO XLS ----------
    st.subheader("1. Upload dos dados")
    arquivo = st.file_uploader(
        "Envie um arquivo .xls ou .xlsx de Turismo do Data.Rio",
        type=["xls", "xlsx"],
        help="Baixe o dataset em https://www.data.rio/ na categoria Turismo "
        "(ex.: Estabelecimentos de Hospedagem, Meios de Hospedagem, "
        "Empresas de Turismo cadastradas etc.)",
    )
 
    st.divider()
 
    # ---------- ITEM 7: COLOR PICKER ----------
    st.subheader("2. Personalização visual")
    st.session_state.bg_color = st.color_picker(
        "Cor de fundo do painel", st.session_state.bg_color
    )
    st.session_state.font_color = st.color_picker(
        "Cor da fonte", st.session_state.font_color
    )
 
aplicar_tema(st.session_state.bg_color, st.session_state.font_color)
 
# ------------------------------------------------------------------
# CABEÇALHO / ITEM 1 - OBJETIVO, MOTIVAÇÃO E DATASET ESCOLHIDO
# ------------------------------------------------------------------
st.title("🏖️ Turismo na Cidade do Rio de Janeiro")
st.caption("Painel interativo construído em Streamlit com dados do portal Data.Rio")
 
with st.expander("📌 Item 1 — Dataset escolhido, objetivo e motivação", expanded=True):
    st.markdown(
        """
**Fonte dos dados:** portal de dados abertos da Prefeitura do Rio de Janeiro,
[Data.Rio](https://www.data.rio/), categoria **Turismo**. Nessa categoria o
portal disponibiliza conjuntos como *Estabelecimentos de Hospedagem
cadastrados*, *Meios de Hospedagem por bairro* e *Equipamentos e atrativos
turísticos da cidade*, entre outros, normalmente exportáveis em `.xls`/`.xlsx`.
 
**Objetivo do painel:** permitir que qualquer usuário (turista, gestor
público, pesquisador ou empreendedor do setor) faça o upload de um desses
datasets e explore, de forma visual e interativa, informações como a
distribuição de estabelecimentos ou atrativos turísticos por bairro/região,
categoria e outras características disponíveis no arquivo.
 
**Motivação:** o setor de turismo é um dos pilares econômicos da cidade do
Rio de Janeiro. Ter uma ferramenta simples para filtrar, visualizar e
exportar esses dados ajuda gestores públicos a identificar áreas com maior
ou menor oferta turística, e ajuda também empreendedores a entender onde
investir.
 
**Funcionalidades implementadas neste painel:**
- Upload de arquivo `.xls`/`.xlsx`;
- Filtros por seletores (radio, checkbox e dropdown/multiselect);
- Tabela interativa (ordenável e filtrável);
- Download dos dados filtrados em `.xlsx`;
- Barra de progresso e spinner durante o carregamento;
- Personalização visual via color picker;
- Cache dos dados carregados;
- Persistência de preferências via Session State;
- Gráficos simples (barras, linhas e pizza);
- Gráficos avançados (histograma e dispersão);
- Métricas básicas (contagem, médias, somas).
        """
    )
 
st.divider()
 
# ------------------------------------------------------------------
# CARREGAMENTO DO ARQUIVO (ITEM 6 - PROGRESS BAR E SPINNER)
# ------------------------------------------------------------------
if arquivo is not None:
    # Só refaz o carregamento "pesado" se o arquivo mudou
    if st.session_state.last_filename != arquivo.name:
        progresso = st.progress(0, text="Iniciando leitura do arquivo...")
        with st.spinner("Processando arquivo XLS, aguarde..."):
            arquivo_bytes = arquivo.getvalue()
            for pct, msg in [
                (25, "Lendo bytes do arquivo..."),
                (55, "Interpretando planilha..."),
                (80, "Organizando colunas..."),
            ]:
                time.sleep(0.3)
                progresso.progress(pct, text=msg)
 
            df_carregado = carregar_dados(arquivo_bytes, arquivo.name)
 
            progresso.progress(100, text="Concluído!")
            time.sleep(0.3)
        progresso.empty()
 
        st.session_state.df = df_carregado
        st.session_state.last_filename = arquivo.name
        # reseta seleções de filtro ao trocar de arquivo
        st.session_state.checkbox_cols = list(df_carregado.columns)
        st.session_state.dropdown_col = df_carregado.columns[0]
        st.session_state.dropdown_values = []
 
        st.success(f"Arquivo **{arquivo.name}** carregado com sucesso! "
                   f"({df_carregado.shape[0]} linhas × {df_carregado.shape[1]} colunas)")
 
df = st.session_state.df
 
if df is None:
    st.info(
        "⬅️ Envie um arquivo `.xls`/`.xlsx` de turismo do Data.Rio na barra "
        "lateral para começar a explorar os dados."
    )
    st.stop()
 
# ------------------------------------------------------------------
# ITEM 3 - FILTROS (RADIO, CHECKBOX, DROPDOWN)
# ------------------------------------------------------------------
st.header("🔍 Filtros e seleção de dados")
 
colunas_todas = list(df.columns)
colunas_numericas = df.select_dtypes(include="number").columns.tolist()
colunas_categoricas = [c for c in colunas_todas if c not in colunas_numericas]
 
col_a, col_b, col_c = st.columns(3)
 
with col_a:
    st.markdown("**Modo de visualização (radio)**")
    st.session_state.radio_choice = st.radio(
        "Quais colunas exibir?",
        options=["Todas as colunas", "Somente colunas selecionadas abaixo"],
        index=["Todas as colunas", "Somente colunas selecionadas abaixo"].index(
            st.session_state.radio_choice
        ),
        label_visibility="collapsed",
    )
 
with col_b:
    st.markdown("**Colunas a exibir (checkbox)**")
    st.session_state.checkbox_cols = st.multiselect(
        "Selecione as colunas",
        options=colunas_todas,
        default=[c for c in st.session_state.checkbox_cols if c in colunas_todas]
        or colunas_todas,
        label_visibility="collapsed",
    )
 
with col_c:
    st.markdown("**Filtrar por valor (dropdown)**")
    st.session_state.dropdown_col = st.selectbox(
        "Escolha a coluna para filtrar",
        options=colunas_categoricas or colunas_todas,
        index=0
        if st.session_state.dropdown_col not in (colunas_categoricas or colunas_todas)
        else (colunas_categoricas or colunas_todas).index(st.session_state.dropdown_col),
    )
    valores_disponiveis = sorted(
        df[st.session_state.dropdown_col].dropna().unique().tolist(),
        key=str,
    )
    st.session_state.dropdown_values = st.multiselect(
        f"Valores de '{st.session_state.dropdown_col}'",
        options=valores_disponiveis,
        default=[v for v in st.session_state.dropdown_values if v in valores_disponiveis],
    )
 
# aplica os filtros
df_filtrado = df.copy()
 
if st.session_state.dropdown_values:
    df_filtrado = df_filtrado[
        df_filtrado[st.session_state.dropdown_col].isin(st.session_state.dropdown_values)
    ]
 
if st.session_state.radio_choice == "Somente colunas selecionadas abaixo":
    colunas_exibidas = st.session_state.checkbox_cols or colunas_todas
else:
    colunas_exibidas = colunas_todas
 
df_filtrado = df_filtrado[colunas_exibidas]
 
st.divider()
 
# ------------------------------------------------------------------
# ITEM 4 - TABELA INTERATIVA
# ------------------------------------------------------------------
st.header("📋 Tabela de dados filtrados")
st.caption("Clique nos cabeçalhos para ordenar. Use a lupa/menu de cada "
           "coluna para filtrar diretamente na tabela.")
st.dataframe(df_filtrado, use_container_width=True, height=400)
 
# ------------------------------------------------------------------
# ITEM 12 - MÉTRICAS BÁSICAS
# ------------------------------------------------------------------
st.subheader("📊 Métricas rápidas")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Registros filtrados", f"{len(df_filtrado):,}".replace(",", "."))
m2.metric("Registros no total", f"{len(df):,}".replace(",", "."))
 
if colunas_numericas:
    col_metrica = colunas_numericas[0]
    m3.metric(f"Média de '{col_metrica}'", f"{df_filtrado[col_metrica].mean():,.2f}"
              if not df_filtrado.empty else "—")
    m4.metric(f"Soma de '{col_metrica}'", f"{df_filtrado[col_metrica].sum():,.2f}"
              if not df_filtrado.empty else "—")
else:
    m3.metric("Colunas numéricas", "0")
    m4.metric("Colunas categóricas", len(colunas_categoricas))
 
st.divider()
 
# ------------------------------------------------------------------
# ITEM 5 - DOWNLOAD DOS DADOS FILTRADOS
# ------------------------------------------------------------------
st.subheader("⬇️ Exportar dados filtrados")
xlsx_bytes = converter_para_xlsx(df_filtrado)
st.download_button(
    label="Baixar dados filtrados em XLSX",
    data=xlsx_bytes,
    file_name="turismo_rio_filtrado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
 
st.divider()
 
# ------------------------------------------------------------------
# ITENS 10 e 11 - GRÁFICOS SIMPLES E AVANÇADOS
# ------------------------------------------------------------------
st.header("📈 Visualizações gráficas")
 
tab_simples, tab_avancado = st.tabs(["Gráficos simples", "Gráficos avançados"])
 
with tab_simples:
    if df_filtrado.empty:
        st.warning("Sem dados para plotar com os filtros atuais.")
    else:
        cat_para_grafico = colunas_categoricas[0] if colunas_categoricas else colunas_todas[0]
 
        if colunas_numericas:
            # Quando existe coluna numérica, é mais informativo somar essa
            # coluna agrupando pela categoria do que apenas contar linhas.
            col_valor = colunas_numericas[0]
            agregado = (
                df_filtrado.groupby(cat_para_grafico, dropna=True)[col_valor]
                .sum()
                .reset_index()
                .sort_values(col_valor, ascending=False)
                .head(15)
            )
            rotulo_valor = f"soma de {col_valor}"
        else:
            agregado = df_filtrado[cat_para_grafico].value_counts().reset_index()
            agregado.columns = [cat_para_grafico, "quantidade"]
            agregado = agregado.head(15)
            col_valor = "quantidade"
            rotulo_valor = "quantidade de registros"
 
        c1, c2 = st.columns(2)
        with c1:
            fig_barras = px.bar(
                agregado, x=cat_para_grafico, y=col_valor,
                title=f"'{cat_para_grafico}' por {rotulo_valor} (barras)",
            )
            st.plotly_chart(fig_barras, use_container_width=True)
 
        with c2:
            fig_pizza = px.pie(
                agregado, names=cat_para_grafico, values=col_valor,
                title=f"Distribuição de '{cat_para_grafico}' por {rotulo_valor} (pizza)",
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
 
        if colunas_numericas:
            col_linha = colunas_numericas[0]
            df_linha = df_filtrado.reset_index()
            fig_linha = px.line(
                df_linha, x=cat_para_grafico, y=col_linha,
                title=f"Evolução de '{col_linha}' por '{cat_para_grafico}' (linha)",
            )
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.info("Não há colunas numéricas suficientes para o gráfico de linhas.")
 
with tab_avancado:
    if not colunas_numericas:
        st.warning("O arquivo carregado não possui colunas numéricas suficientes "
                    "para gráficos avançados.")
    else:
        c3, c4 = st.columns(2)
        with c3:
            col_hist = st.selectbox("Coluna para o histograma", colunas_numericas, key="hist_col")
            fig_hist = px.histogram(df_filtrado, x=col_hist, title=f"Histograma de '{col_hist}'")
            st.plotly_chart(fig_hist, use_container_width=True)
 
        with c4:
            if len(colunas_numericas) >= 2:
                col_x = st.selectbox("Eixo X (dispersão)", colunas_numericas, index=0, key="scatter_x")
                col_y = st.selectbox("Eixo Y (dispersão)", colunas_numericas, index=1, key="scatter_y")
                cor_opcional = colunas_categoricas[0] if colunas_categoricas else None
                fig_scatter = px.scatter(
                    df_filtrado, x=col_x, y=col_y,
                    color=cor_opcional,
                    title=f"Dispersão: '{col_x}' vs '{col_y}'",
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("São necessárias ao menos duas colunas numéricas para o "
                         "gráfico de dispersão.")
 
st.divider()
st.caption(
    "Desenvolvido para o TP3 — Desenvolvimento de Aplicações com Streamlit. "
    "Dados: portal Data.Rio (https://www.data.rio/), categoria Turismo."
)