# Data Summary Report - EquidadeJá Brasil

## 1. Visão Geral das Fontes de Dados

O projeto utiliza duas fontes de dados principais para alimentar as análises quantitativas e qualitativas:

| Fonte | Tipo de Dado | Método de Aquisição | Ficheiro de Destino |
| :--- | :--- | :--- | :--- |
| **World Bank / Amostra** | Estruturado (CSV) | Carga Local / API | `Sample Data/amostra_indicadores_genero.csv` |
| **Google News RSS** | Não Estruturado / Semiestruturado | Web Scraping (`BeautifulSoup`) | `Data/Processed/noticias_equidade.csv` e `corpus_noticias.txt` |

---

## 2. Detalhamento da Coleta via Web Scraping (TP2)

### 2.1 Fonte e Mecanismo de Extração
- **URL Base:** Feed RSS do Google News referente a buscas sobre equidade de género no mercado de trabalho.
- **Script Responsável:** `Code/DataAcquisition/coletor_noticias.py`
- **Ferramentas Utilizadas:**
  - `requests`: Para efetuar as requisições HTTP ao servidor remoto.
  - `BeautifulSoup` (`bs4`): Para realizar o *parsing* do XML/HTML e isolar as tags das notícias (`<item>`, `<title>`, `<source>`, `<pubDate>`, `<link>`).

### 2.2 Estrutura dos Ficheiros Gerados
1. **`Data/Processed/noticias_equidade.csv`**:
   - Contém o registo estruturado das notícias com as colunas: `titulo`, `fonte`, `data` e `link`.
2. **`Data/Processed/corpus_noticias.txt`**:
   - Contém a concatenação dos títulos das notícias coletadas, utilizado diretamente para a geração da Nuvem de Palavras na aplicação.

---

## 3. Fluxo de Dados na Aplicação (Streamlit)

1. **Carga e Cache:** A aplicação lê os ficheiros processados na pasta `Data/Processed/` utilizando a função `@st.cache_data` para assegurar velocidade na renderização.
2. **Interatividade:** O utilizador pode visualizar a tabela de notícias na Aba 2 e a Nuvem de Palavras na Aba 3.
3. **Upload de Ficheiros:** Através da Aba 4, o utilizador pode carregar novos ficheiros CSV, cujos dados são armazenados temporariamente na memória através de `st.session_state['dados_usuario']`.