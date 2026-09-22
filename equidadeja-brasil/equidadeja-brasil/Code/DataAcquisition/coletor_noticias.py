import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def coletar_noticias():
    print("Iniciando coleta de notícias com Beautiful Soup...")
    
    # URL do feed RSS do Google News sobre equidade de gênero
    url = "https://news.google.com/rss/search?q=equidade+de+genero+mercado+de+trabalho&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resposta = requests.get(url, headers=headers)
    
    if resposta.status_code != 200:
        print(f"Erro ao acessar o feed: status {resposta.status_code}")
        return

    # Usando Beautiful Soup para parsing do XML/HTML
    soup = BeautifulSoup(resposta.content, 'xml')
    itens = soup.find_all('item')
    
    dados_noticias = []
    textos_completos = []

    for item in itens[:15]:  # Pega as 15 notícias mais recentes
        titulo = item.title.text if item.title else "Sem título"
        link = item.link.text if item.link else ""
        data_pub = item.pubDate.text if item.pubDate else ""
        fonte = item.source.text if item.source else "Fonte desconhecida"
        
        dados_noticias.append({
            'titulo': titulo,
            'fonte': fonte,
            'data': data_pub,
            'link': link
        })
        textos_completos.append(titulo)

    # Garante a criação da pasta Data/Processed no caminho relativo correto
    caminho_dados = os.path.join('Data', 'Processed')
    os.makedirs(caminho_dados, exist_ok=True)

    # 1. Salva a tabela de notícias tratada em CSV
    df = pd.DataFrame(dados_noticias)
    caminho_csv = os.path.join(caminho_dados, 'noticias_equidade.csv')
    df.to_csv(caminho_csv, index=False, encoding='utf-8')
    print(f"✅ Arquivo CSV criado com sucesso em: {caminho_csv}")

    # 2. Salva o texto das manchetes em TXT (para alimentar a Nuvem de Palavras)
    caminho_txt = os.path.join(caminho_dados, 'corpus_noticias.txt')
    with open(caminho_txt, 'w', encoding='utf-8') as f:
        f.write(" ".join(textos_completos))
    print(f"✅ Arquivo TXT criado com sucesso em: {caminho_txt}")

if __name__ == "__main__":
    coletar_noticias()