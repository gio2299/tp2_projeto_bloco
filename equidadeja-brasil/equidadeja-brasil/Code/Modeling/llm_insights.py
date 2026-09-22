"""
Módulo de Modelagem — geração de insights via LLM (Claude, API da Anthropic),
usando engenharia de prompts.

Este módulo NÃO treina um modelo de machine learning tradicional; a
"modelagem" deste projeto consiste em projetar um prompt estruturado que:
  1. Recebe um resumo estatístico dos indicadores (do Banco Mundial).
  2. Recebe as manchetes coletadas via Web Scraping.
  3. Instrui o modelo a gerar um resumo executivo curto e um insight
     acionável, em português, para o público de RH/ESG.
  4. Restringe o modelo a usar apenas os dados fornecidos, para reduzir o
     risco de "alucinação" (invenção de números ou fatos).

Requer uma chave de API da Anthropic na variável de ambiente
ANTHROPIC_API_KEY (ver README.md e .env.example).
"""

import os

import pandas as pd

try:
    import anthropic
except ImportError:
    anthropic = None

MODELO = "claude-sonnet-4-5"

SYSTEM_PROMPT = """\
Você é um analista de ESG especializado em diversidade e inclusão no mercado \
de trabalho brasileiro. Sua tarefa é gerar um resumo executivo curto (máximo \
150 palavras), em português, para um público de RH e gestores de ESG.

Regras obrigatórias:
- Use SOMENTE os dados numéricos e as manchetes fornecidas. Nunca invente \
números, datas ou fatos que não estejam explicitamente no texto de entrada.
- Se os dados fornecidos forem insuficientes para alguma afirmação, diga que \
a informação não está disponível, em vez de supor.
- Estruture a resposta em duas partes, com estes títulos exatos:
  "Resumo:" (2-3 frases sobre o que os dados mostram)
  "Insight acionável:" (1-2 frases com uma sugestão prática para RH/ESG)
- Tom objetivo e profissional, sem alarmismo nem otimismo exagerado.
"""


def _montar_prompt_usuario(resumo_indicadores: str, manchetes: list[str]) -> str:
    manchetes_formatadas = "\n".join(f"- {m}" for m in manchetes) if manchetes else "(nenhuma manchete disponível)"
    return f"""\
Dados quantitativos (Banco Mundial, indicadores de gênero no mercado de \
trabalho no Brasil):
{resumo_indicadores}

Manchetes recentes coletadas (Web Scraping — Google News):
{manchetes_formatadas}

Gere o resumo executivo e o insight acionável conforme as instruções."""


def montar_resumo_indicadores(df_gap: pd.DataFrame) -> str:
    """
    Constrói um resumo textual simples e verificável a partir do DataFrame
    de gap de participação (ver worldbank_api.calcular_gap_participacao),
    para servir de entrada factual ao prompt.
    """
    if df_gap.empty:
        return "Não há dados quantitativos disponíveis no momento."

    ultimo = df_gap.iloc[-1]
    primeiro = df_gap.iloc[0]

    return (
        f"- Em {int(ultimo['ano'])}, a taxa de participação na força de trabalho foi de "
        f"{ultimo['mulheres']:.1f}% para mulheres e {ultimo['homens']:.1f}% para homens "
        f"(diferença de {ultimo['gap_pontos_percentuais']:.1f} pontos percentuais).\n"
        f"- Em {int(primeiro['ano'])}, essa diferença era de {primeiro['gap_pontos_percentuais']:.1f} "
        f"pontos percentuais.\n"
        f"- Ou seja, a diferença {'diminuiu' if ultimo['gap_pontos_percentuais'] < primeiro['gap_pontos_percentuais'] else 'aumentou ou se manteve estável'} "
        f"no período analisado."
    )


def gerar_insight(resumo_indicadores: str, manchetes: list[str], api_key: str = None) -> str:
    """
    Chama a API da Anthropic (Claude) para gerar o resumo executivo e o
    insight acionável, a partir do resumo estatístico e das manchetes.

    Retorna o texto gerado, ou uma mensagem de erro amigável caso a chave de
    API não esteja configurada ou a biblioteca `anthropic` não esteja
    instalada.
    """
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    if anthropic is None:
        return (
            "⚠️ A biblioteca 'anthropic' não está instalada. Rode "
            "`pip install anthropic` e tente novamente."
        )

    if not api_key:
        return (
            "⚠️ Nenhuma chave de API da Anthropic foi encontrada. Configure a "
            "variável de ambiente ANTHROPIC_API_KEY (veja o arquivo "
            ".env.example) para habilitar a geração de insights por IA."
        )

    client = anthropic.Anthropic(api_key=api_key)
    prompt_usuario = _montar_prompt_usuario(resumo_indicadores, manchetes)

    try:
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt_usuario}],
        )
        return resposta.content[0].text

    except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer erro de API e mostrar ao usuário
        return f"⚠️ Erro ao chamar a API da Anthropic: {exc}"
