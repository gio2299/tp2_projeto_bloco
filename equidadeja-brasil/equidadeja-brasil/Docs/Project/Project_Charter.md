# Project Charter - EquidadeJá Brasil

## Visão Geral do Projeto
O **EquidadeJá Brasil** é uma plataforma analítica desenvolvida para monitorizar, consolidar e analisar dados e notícias relacionados com a equidade de género no mercado de trabalho brasileiro. O projeto está alinhado com o **ODS 5** (Igualdade de Género) e o **ODS 8** (Trabalho Decente e Crescimento Económico).

## Escopo e Entregas por Fase

### Fase 1 (TP1) - Estruturação e Indicadores Globais
- Configuração do repositório no GitHub sob a metodologia TDSP/CRISP-DM.
- Criação da estrutura base em Streamlit com navegação por abas.
- Integração com dados de amostra dos Indicadores de Género do World Bank.
- Configuração inicial do ambiente de desenvolvimento Python.

### Fase 2 (TP2) - Coleta Automatizada, Performance e Visualização Não Estruturada
- **Web Scraping:** Implementação de script automatizado (`Code/DataAcquisition/coletor_noticias.py`) utilizando as bibliotecas `requests` e `BeautifulSoup` para extração de notícias em tempo real sobre equidade de género.
- **Armazenamento Processado:** Geração e atualização dos ficheiros `Data/Processed/noticias_equidade.csv` e `Data/Processed/corpus_noticias.txt`.
- **Otimização de Performance:** Aplicação do decorador `@st.cache_data` do Streamlit para evitar releituras desnecessárias dos ficheiros locais durante a navegação.
- **Gestão de Estado:** Utilização do `st.session_state` para persistência temporária dos dados submetidos pelo utilizador na sessão do painel.
- **Serviços de Ficheiros:** Implementação dos módulos de *Upload* de ficheiros CSV complementares e *Download* das notícias coletadas.
- **Visualização NLP:** Integração de Nuvem de Palavras (`wordcloud` e `matplotlib`) para análise textual das manchetes raspadas.

## Metodologia e Boas Práticas
- **Controlo de Versões:** Versionamento contínuo via Git/GitHub.
- **Gestão de Dependências:** Documentação de bibliotecas no ficheiro `requirements.txt`.