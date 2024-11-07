import streamlit as st
import os
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Função para download de XML com barra de progresso atualizada em tempo real
def download_xml(manual_keys, download_path):
    if 'is_stopped' not in st.session_state:
        st.session_state.is_stopped = False
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'files_saved' not in st.session_state:
        st.session_state.files_saved = 0

    # Configuração do Chrome
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    navegador = webdriver.Chrome(options=chrome_options)
    link = "https://meudanfe.com.br"
    navegador.get(link)
    time.sleep(5)

    # Configuração da barra de progresso no Streamlit
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    chaves = manual_keys.strip().split("\n") if manual_keys else []
    if not chaves:
        st.warning("Nenhuma chave fornecida. Insira as chaves manualmente.")
        return

    for i, codigo_chave in enumerate(chaves):
        if st.session_state.is_stopped:
            st.warning("Automação interrompida.")
            break

        try:
            input_element = WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="get-danfe"]/div/div/div[1]/div/div/div/input'))
            )
            input_element.send_keys(codigo_chave)
            time.sleep(2)

            botao_buscar = navegador.find_element(By.XPATH, '//*[@id="get-danfe"]/div/div/div[1]/div/div/div/button')
            botao_buscar.click()
            time.sleep(2)

            try:
                botao_download = WebDriverWait(navegador, 5).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/button[1]'))
                )
                botao_download.click()
                st.session_state.files_saved += 1
                time.sleep(1)
            except Exception:
                st.warning(f"Captcha não resolvido para a chave {codigo_chave}. Pulando para a próxima chave.")
                continue

            downloaded_file = max([f for f in os.listdir(download_path)], key=lambda x: os.path.getctime(os.path.join(download_path, x)))
            new_file_name = f"{codigo_chave}.xml"
            os.rename(os.path.join(download_path, downloaded_file), os.path.join(download_path, new_file_name))

            navegador.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[1]/button').click()
            time.sleep(1)

        except Exception as e:
            st.error(f"Erro ao processar a chave {codigo_chave}: {e}")

        # Atualizar barra de progresso e percentual
        progress_percentage = (i + 1) / len(chaves)
        progress_bar.progress(progress_percentage)
        progress_text.text(f"Progresso: {progress_percentage * 100:.2f}% concluído")

    navegador.quit()
    st.success("Processo concluído!" if not st.session_state.is_stopped else "Processo interrompido!")
    st.info(f"Número total de arquivos salvos: {st.session_state.files_saved}")

# Função para limpar a entrada e a barra de progresso
def clear_input():
    st.session_state.manual_keys = ""
    st.session_state.is_stopped = False
    st.session_state.files_saved = 0
    st.session_state.current_index = 0
    st.empty()  # Limpar o campo de progresso

# Função principal
def main():
    st.title("Download de XML")

    manual_keys = st.text_area("Insira as chaves de acesso (uma por linha):", key="manual_keys")
    download_path = st.text_input("Informe o caminho de salvamento do XML:", value=os.getcwd())

    start_button = st.button("Iniciar Download")
    stop_button = st.button("Interromper", on_click=lambda: toggle_stop())
    clear_button = st.button("Limpar", on_click=clear_input)  # Botão de limpar

    if start_button:
        st.session_state.is_stopped = False
        st.session_state.current_index = 0
        st.session_state.files_saved = 0
        download_xml(manual_keys, download_path)

    st.markdown("<div style='text-align: right;'>Criado por Hugo Silva.</div>", unsafe_allow_html=True)

def toggle_stop():
    st.session_state.is_stopped = True

if __name__ == "__main__":
    main()
