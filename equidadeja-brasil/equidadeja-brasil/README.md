# EquidadeJá Brasil

Painel de equidade de gênero no mercado de trabalho brasileiro, alinhado à
Agenda 2030 (ODS 5 e ODS 8). Projeto completo integrando **API**, **Web
Scraping** e **LLM via engenharia de prompts**, em Python + Streamlit.

## Estrutura de diretórios (padrão TDSP)

```
equidadeja-brasil/
├── Code/
│   ├── DataAcquisition/
│   │   ├── worldbank_api.py   # coleta via API (Banco Mundial)
│   │   └── news_scraper.py    # coleta via Web Scraping (Google News RSS)
│   ├── DataExploration/       # (livre para análises exploratórias futuras)
│   ├── Modeling/
│   │   └── llm_insights.py    # geração de insights via LLM (Anthropic API)
│   └── Deployment/
│       └── app.py             # aplicação Streamlit (integra as 3 fontes)
├── Data/
│   ├── Raw/                   # dados brutos coletados (uso futuro)
│   └── Processed/             # dados tratados (uso futuro)
├── Docs/
│   ├── Project/Project_Charter.md
│   ├── Data Report/Data_Summary_Report.md
│   └── Model Report/Model_Report.md
├── Sample Data/                # dados de amostra (fallback caso API/scraping falhem)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Como configurar o ambiente

### Opção 1 — venv (Windows / PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Opção 2 — venv (Linux / Mac)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Opção 3 — conda
```bash
conda create -n equidadeja python=3.11 -y
conda activate equidadeja
pip install -r requirements.txt
```

## Configurar a chave de API da Anthropic (para a aba de Insights com IA)

1. Copie o arquivo `.env.example` para `.env`.
2. Preencha `ANTHROPIC_API_KEY=sua-chave-real`.
3. Antes de rodar o Streamlit, carregue a variável de ambiente. Duas formas:

   **a) Usando python-dotenv (mais simples):** o próprio app pode carregar o
   `.env` automaticamente se você adicionar, no topo de `app.py`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
   (isso já está preparado para ser adicionado; o pacote `python-dotenv` já
   está no `requirements.txt`.)

   **b) Definindo manualmente no terminal antes de rodar:**
   ```powershell
   $env:ANTHROPIC_API_KEY="sua-chave-real"      # PowerShell
   ```
   ```bash
   export ANTHROPIC_API_KEY="sua-chave-real"    # Linux/Mac
   ```

> Sem a chave configurada, o dashboard funciona normalmente nas abas de
> Indicadores e Notícias — apenas a aba "Insight gerado por IA" fica
> desabilitada, com um aviso explicando o motivo.

## Como rodar a aplicação

```bash
streamlit run "Code/Deployment/app.py"
```

O app abre no navegador (por padrão em `http://localhost:8501`), com três
abas:
1. **📊 Indicadores (API):** dados do Banco Mundial sobre participação de
   gênero no mercado de trabalho e representatividade em posições de
   decisão, com fallback para dados de amostra caso a API esteja fora do ar.
2. **📰 Notícias (Web Scraping):** manchetes recentes coletadas via feed RSS
   do Google News, com fallback para amostra local.
3. **🤖 Insight gerado por IA:** resumo executivo e insight acionável,
   gerado por LLM a partir dos dados das duas abas anteriores.

## Documentos do projeto
- [Project Charter](Docs/Project/Project_Charter.md) — problema de negócio, metas, ODS e público-alvo.
- [Data Summary Report](Docs/Data%20Report/Data_Summary_Report.md) — fontes de dados (API, scraping e LLM).
- [Model Report](Docs/Model%20Report/Model_Report.md) — documentação da engenharia de prompts e avaliação.

## Metodologia
Projeto organizado seguindo **CRISP-DM** (ciclo analítico: entendimento do
negócio → dos dados → preparação → modelagem → avaliação → implantação) e
**TDSP** (organização de papéis, artefatos e diretórios). Ver detalhes no
Project Charter.
