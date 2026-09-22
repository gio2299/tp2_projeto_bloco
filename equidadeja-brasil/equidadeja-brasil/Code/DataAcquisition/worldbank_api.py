"""
Módulo de coleta de dados via World Bank Open Data API.

Coleta indicadores de participação de gênero no mercado de trabalho e de
representatividade em posições de decisão, para o Brasil.

API pública, sem necessidade de chave: https://api.worldbank.org/v2/
"""

import pandas as pd
import requests

BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

INDICATORS = {
    "SL.TLF.CACT.FE.ZS": "Taxa de participacao na forca de trabalho - Mulheres (%)",
    "SL.TLF.CACT.MA.ZS": "Taxa de participacao na forca de trabalho - Homens (%)",
    "SG.GEN.PARL.ZS": "Assentos ocupados por mulheres no parlamento (%)",
}


def fetch_indicator(country: str = "BRA", indicator: str = "SL.TLF.CACT.FE.ZS",
                     start_year: int = 2000, end_year: int = 2023) -> pd.DataFrame:
    """
    Busca uma série histórica de um indicador do Banco Mundial para um país.

    Retorna um DataFrame com colunas: ano, valor, indicador.
    Em caso de falha na API, retorna um DataFrame vazio (o chamador deve
    tratar o fallback para dados de amostra locais).
    """
    url = BASE_URL.format(country=country, indicator=indicator)
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 1000,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            return pd.DataFrame(columns=["ano", "valor", "indicador"])

        records = payload[1]
        rows = [
            {
                "ano": int(item["date"]),
                "valor": item["value"],
                "indicador": INDICATORS.get(indicator, indicator),
            }
            for item in records
            if item.get("value") is not None
        ]

        df = pd.DataFrame(rows).sort_values("ano").reset_index(drop=True)
        return df

    except (requests.RequestException, ValueError, KeyError):
        return pd.DataFrame(columns=["ano", "valor", "indicador"])


def fetch_all_indicators(country: str = "BRA") -> pd.DataFrame:
    """Busca todos os indicadores definidos em INDICATORS e concatena o resultado."""
    frames = [fetch_indicator(country=country, indicator=code) for code in INDICATORS]
    non_empty = [f for f in frames if not f.empty]
    if not non_empty:
        return pd.DataFrame(columns=["ano", "valor", "indicador"])
    return pd.concat(non_empty, ignore_index=True)


def calcular_gap_participacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    A partir do DataFrame de indicadores, calcula o gap (diferença em pontos
    percentuais) entre a participação masculina e feminina na força de
    trabalho, ano a ano. Útil para destacar a desigualdade de forma direta.
    """
    fem = df[df["indicador"] == INDICATORS["SL.TLF.CACT.FE.ZS"]][["ano", "valor"]].rename(
        columns={"valor": "mulheres"}
    )
    masc = df[df["indicador"] == INDICATORS["SL.TLF.CACT.MA.ZS"]][["ano", "valor"]].rename(
        columns={"valor": "homens"}
    )
    merged = pd.merge(fem, masc, on="ano", how="inner")
    merged["gap_pontos_percentuais"] = merged["homens"] - merged["mulheres"]
    return merged.sort_values("ano").reset_index(drop=True)
