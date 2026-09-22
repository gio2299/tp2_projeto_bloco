# Model Report — EquidadeJá Brasil

## 1. Objetivo deste documento
Documentar a etapa de "modelagem" do projeto — que, neste caso, não é um
modelo de machine learning treinado, e sim uma solução baseada em **LLM via
engenharia de prompts**, conforme previsto no objetivo final do projeto.

## 2. Abordagem escolhida
Optou-se por usar um LLM (Claude, via API da Anthropic) como um **gerador de
insights textuais** a partir de dados estruturados, em vez de treinar um
modelo preditivo. A justificativa é que o problema de negócio (falta de
interpretação acionável dos indicadores de equidade de gênero) é mais bem
resolvido por síntese e contextualização de linguagem natural do que por
previsão numérica.

## 3. Engenharia de Prompt

### 3.1 System Prompt
Define o papel do modelo (analista de ESG/D&I), o público-alvo (RH e
gestores), o limite de tamanho da resposta, e — mais importante — restrições
explícitas contra "alucinação": o modelo é instruído a usar **somente** os
dados fornecidos, e a declarar explicitamente quando uma informação não está
disponível, em vez de supor.

### 3.2 User Prompt (dados de entrada)
Construído dinamicamente a partir de duas fontes já coletadas nas etapas de
Data Acquisition:
1. Um resumo estatístico verificável dos indicadores do Banco Mundial
   (função `montar_resumo_indicadores`, em `Code/Modeling/llm_insights.py`).
2. Uma lista das manchetes mais recentes coletadas via Web Scraping (função
   `buscar_todas_noticias`, em `Code/DataAcquisition/news_scraper.py`).

### 3.3 Formato de saída esperado
O prompt exige uma estrutura fixa de resposta ("Resumo:" e "Insight
acionável:"), o que facilita tanto a leitura pelo usuário final quanto uma
eventual validação automatizada de formato em versões futuras.

## 4. Avaliação (critérios de qualidade)
Como não há uma métrica numérica tradicional (ex: acurácia) para avaliar
texto gerado, a avaliação é feita por **checklist qualitativo**, aplicado
manualmente a cada resposta gerada durante os testes:

| Critério | Descrição |
|---|---|
| Fidelidade aos dados | O texto não menciona números ou fatos que não estavam no prompt de entrada? |
| Honestidade sobre limitações | Quando os dados são insuficientes, o modelo admite isso em vez de inventar? |
| Utilidade para o público-alvo | O insight sugerido é acionável para uma área de RH/ESG? |
| Aderência ao formato | A resposta segue a estrutura "Resumo:" / "Insight acionável:"? |
| Tom | A resposta é objetiva, sem alarmismo nem otimismo exagerado? |

## 5. Limitações conhecidas
- O modelo depende inteiramente da qualidade e atualidade dos dados
  coletados nas etapas anteriores (API + scraping) — não há verificação
  cruzada com outras fontes.
- Respostas de LLMs podem variar entre execuções mesmo com o mesmo prompt
  (não determinístico), o que é aceitável para este caso de uso (insights
  de apoio à decisão, não fatos regulatórios).
- A funcionalidade requer uma chave de API paga/própria do usuário — não
  está disponível "out of the box" sem essa configuração.

## 6. Próximos passos
- Testar variações do prompt com um conjunto fixo de dados, para avaliar
  consistência das respostas (uma forma simples de "regressão de prompt").
- Considerar adicionar poucos exemplos (few-shot) de bons resumos ao prompt,
  caso a qualidade das respostas precise de ajuste fino.
- Coletar feedback de um usuário-teste da área de RH/D&I sobre a utilidade
  prática dos insights gerados.
