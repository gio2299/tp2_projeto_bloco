"""
Módulo de Web Scraping — coleta de manchetes recentes sobre equidade de
gênero no mercado de trabalho, via feed RSS público do Google News.

Por que RSS e não scraping de HTML de sites de notícia?
- O feed RSS é uma interface pública, desenhada para consumo/syndication,
  o que o torna uma fonte mais estável e menos sujeita a bloqueios do que
  fazer scraping direto do HTML de um portal de notícias.
- Coletamos apenas metadados (título, fonte, data, link) — não o conteúdo
  integral das matérias — o que respeita direitos autorais dos veículos.

Este módulo faz o parsing manual do XML (sem depender de bibliotecas de
RSS de terceiros), usando apenas `requests` e `xml.etree.ElementTree`,
que já vêm no requirements.txt / biblioteca padrão do Python.
"""

import xml.etree.ElementTree as ET

import pandas as pd
import requests

RSS_BASE_URL = "https://news.google.com/rss/search"

TERMOS_BUSCA_PADRAO = [
    "equidade de gênero trabalho Brasil",
    "diferença salarial mulheres homens Brasil",
    "mulheres liderança empresas Brasil",
]


def buscar_noticias(termo: str, max_resultados: int = 10) -> pd.DataFrame:
    """
    Busca notícias recentes para um termo específico via feed RSS do Google
    News, em português do Brasil.

    Retorna um DataFrame com colunas: titulo, fonte, data, link, termo_busca.
    Em caso de falha de rede, retorna um DataFrame vazio.
    """
    params = {
        "q": termo,
        "hl": "pt-BR",
        "gl": "BR",
        "ceid": "BR:pt-419",
    }

    try:
        response = requests.get(RSS_BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        items = root.findall(".//item")[:max_resultados]

        rows = []
        for item in items:
            titulo = item.findtext("title", default="")
            link = item.findtext("link", default="")
            data_pub = item.findtext("pubDate", default="")
            fonte_el = item.find("source")
            fonte = fonte_el.text if fonte_el is not None else ""

            rows.append(
                {
                    "titulo": titulo,
                    "fonte": fonte,
                    "data": data_pub,
                    "link": link,
                    "termo_busca": termo,
                }
            )

        return pd.DataFrame(rows)

    except (requests.RequestException, ET.ParseError):
        return pd.DataFrame(columns=["titulo", "fonte", "data", "link", "termo_busca"])


def buscar_todas_noticias(termos: list[str] = None, max_por_termo: int = 5) -> pd.DataFrame:
    """Busca notícias para uma lista de termos e concatena os resultados."""
    termos = termos or TERMOS_BUSCA_PADRAO
    frames = [buscar_noticias(termo, max_resultados=max_por_termo) for termo in termos]
    non_empty = [f for f in frames if not f.empty]
    if not non_empty:
        return pd.DataFrame(columns=["titulo", "fonte", "data", "link", "termo_busca"])
    df = pd.concat(non_empty, ignore_index=True)
    return df.drop_duplicates(subset="titulo").reset_index(drop=True)
