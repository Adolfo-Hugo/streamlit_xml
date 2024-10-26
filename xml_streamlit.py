import streamlit as st
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Inicializa as variáveis de sessão
if 'is_stopped' not in st.session_state:
    st.session_state.is_stopped = False
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0  # Índice da chave atual
if 'files_saved' not in st.session_state:
    st.session_state.files_saved = 0  # Contador de arquivos salvos

# Função principal
def main():
    st.title("Download de XML")

    # Entrada manual de chaves de acesso
    manual_keys = st.text_area("Insira as chaves de acesso (uma por linha):")

    # Escolha do diretório de salvamento
    download_path = st.text_input("Informe o caminho de salvamento do XML:", value=os.getcwd())
    
    # Botões de controle
    start_button = st.button("Iniciar Download")
    stop_button = st.button("Interromper", on_click=lambda: toggle_stop())

    # Iniciar processo se o botão for clicado
    if start_button:
        st.session_state.is_stopped = False  # Reiniciar interrupção ao iniciar uma nova execução
        st.session_state.current_index = 0   # Reiniciar índice ao iniciar uma nova execução
        st.session_state.files_saved = 0      # Reiniciar contador de arquivos salvos
        
        # Processar chaves fornecidas manualmente
        chaves = manual_keys.strip().split("\n") if manual_keys else []
        
        if not chaves:
            st.warning("Nenhuma chave fornecida. Insira as chaves manualmente.")
            return

        # Configuração do navegador Chrome
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        navegador = webdriver.Chrome(service=Service(ChromeDriverManager(version="94.0.4606.61").install()), options=chrome_options)
        link = "https://meudanfe.com.br"
        navegador.maximize_window()
        navegador.get(link)
        time.sleep(5)

        # Configurar barra de progresso no Streamlit
        progress_bar = st.progress(0)
        progress_text = st.empty()  # Espaço para mostrar o percentual de progresso

        # Iteração sobre as chaves
        for i in range(st.session_state.current_index, len(chaves)):
            if st.session_state.is_stopped:
                st.warning("Automação interrompida.")
                break
            
            codigo_chave = chaves[i]
            try:
                # Preencher e submeter a chave de acesso
                navegador.find_element(By.XPATH, '//*[@id="get-danfe"]/div/div/div[1]/div/div/div/input').send_keys(codigo_chave)
                time.sleep(2)
                
                navegador.find_element(By.XPATH, '//*[@id="get-danfe"]/div/div/div[1]/div/div/div/button').click()
                time.sleep(2)
                
                # Esperar pelo botão de download com limite de 5 segundos
                try:
                    botao = WebDriverWait(navegador, 5).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/button[1]'))
                    )
                    botao.click()
                    st.write(f'Chave {codigo_chave} salva com sucesso.')
                    st.session_state.files_saved += 1  # Incrementa o contador de arquivos salvos
                    time.sleep(1)
                except:
                    st.warning(f"Captcha não resolvido para a chave {codigo_chave}. Pulando para a próxima chave.")
                    continue
                
                # Renomear o arquivo baixado
                downloaded_file = max([f for f in os.listdir(download_path)], key=lambda x: os.path.getctime(os.path.join(download_path, x)))
                new_file_name = f"{codigo_chave}.xml"
                os.rename(os.path.join(download_path, downloaded_file), os.path.join(download_path, new_file_name))
                
                # Fechar o modal
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

    # Rodapé
    st.markdown("<div style='text-align: right;'>Criado por Hugo Silva.</div>", unsafe_allow_html=True)

# Função para interromper a execução
def toggle_stop():
    st.session_state.is_stopped = True

if __name__ == "__main__":
    main()
