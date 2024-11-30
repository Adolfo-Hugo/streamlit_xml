import os
import requests
import streamlit as st
from time import time

# URL base da API
BASE_URL = "https://ws.meudanfe.com/api/v1/get/nfe/"
HEADERS = {
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://www.meudanfe.com.br",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Função para verificar ou criar o diretório
def verificar_ou_criar_diretorio(caminho):
    """
    Verifica se o diretório existe, e o cria caso não exista.
    Retorna o caminho absoluto do diretório.
    """
    if not os.path.exists(caminho):
        try:
            os.makedirs(caminho)
        except Exception as e:
            raise Exception(f"Erro ao criar o diretório: {e}")
    return caminho

# Função para consultar a nota fiscal
def consultar_nota_fiscal(id_nota_fiscal):
    url = f"{BASE_URL}data/MEUDANFE/{id_nota_fiscal}"
    try:
        response = requests.post(url, headers=HEADERS, data="{}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao consultar: {response.status_code}")
    except Exception as e:
        raise Exception(f"Erro na consulta da nota fiscal {id_nota_fiscal}: {e}")

# Função para baixar o XML
def baixar_xml(id_nota_fiscal, diretorio):
    url = f"{BASE_URL}xml/{id_nota_fiscal}"
    try:
        response = requests.post(url, headers=HEADERS, data="{}")
        if response.status_code == 200:
            filepath = os.path.join(diretorio, f"{id_nota_fiscal}.xml")
            with open(filepath, "wb") as file:
                file.write(response.content)
        else:
            raise Exception(f"Erro ao baixar: {response.status_code}")
    except Exception as e:
        raise Exception(f"Erro ao baixar XML {id_nota_fiscal}: {e}")

# Interface Streamlit
st.title("Consulta e Download de XML de NF-e")
st.subheader("Insira os IDs das notas fiscais")

# Entrada de IDs
ids_input = st.text_area("IDs das notas fiscais (um por linha)", height=150)

# Seleção de diretório
diretorio = st.text_input("Diretório para salvar os arquivos XML", os.getcwd())

# Botão para iniciar o processamento
if st.button("Processar"):
    if not ids_input.strip():
        st.warning("Por favor, insira os IDs das notas fiscais.")
    else:
        try:
            # Verifica ou cria o diretório
            diretorio_absoluto = verificar_ou_criar_diretorio(diretorio)
            ids = list(set(ids_input.strip().split("\n")))
            total_ids = len(ids)
            st.info(f"Iniciando o processamento de {total_ids} notas fiscais...")

            # Progresso
            progress_bar = st.progress(0)
            sucesso = 0
            inicio = time()

            # Processa cada ID
            for i, id_nota in enumerate(ids, start=1):
                try:
                    consultar_nota_fiscal(id_nota)  # Opcional: para validar a nota
                    baixar_xml(id_nota, diretorio_absoluto)
                    sucesso += 1
                except Exception as e:
                    st.error(f"Erro no ID {id_nota}: {e}")

                # Atualiza progresso
                progress_bar.progress(i / total_ids)

            fim = time()
            st.success(f"Processamento concluído! {sucesso}/{total_ids} arquivos baixados.")
            st.write(f"Tempo total: {fim - inicio:.2f} segundos")
            st.write(f"Arquivos salvos em: {diretorio_absoluto}")
        except Exception as e:
            st.error(f"Erro: {e}")
