import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile

# Configuração do acesso ao link do site
URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
DIR = "Dados do site do Governo"
ZIP_NAME = "Web Scrapping - Governo Federal.zip"

# Criando diretório para salvar os arquivos corretamente!
os.makedirs(DIR, exist_ok=True)

# Obtendo os links dos anexos.
response = requests.get(URL)
if response.status_code != 200:
    print("Erro ao acessar a página")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Extraindo links dos PDFs que contêm "Anexo" no nome...
pdf_links = [
    a["href"] if a["href"].startswith("http") else "https://www.gov.br" + a["href"]
    for a in soup.find_all("a", href=True)
    if "Anexo" in a["href"]
]

if not pdf_links:
    print("Nenhum anexo encontrado!")
    exit()

# Baixando PDFs...
arquivos = []
for link in pdf_links:
    nome_arquivo = os.path.join(DIR, link.split("/")[-1])
    
    try:
        pdf_response = requests.get(link, stream=True)
        pdf_response.raise_for_status()  # Garante que o download funciona!

        with open(nome_arquivo, "wb") as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                f.write(chunk)

        arquivos.append(nome_arquivo)
        print(f"Baixado: {nome_arquivo}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar {link}: {e}")

# Compactando arquivos...
if arquivos:
    with ZipFile(ZIP_NAME, "w") as zipf:
        for arquivo in arquivos:
            zipf.write(arquivo, os.path.basename(arquivo))  # Corrigido o nome no ZIP

    print(f"Arquivos compactados em: {ZIP_NAME}")
else:
    print("Nenhum arquivo foi baixado com sucesso.")

