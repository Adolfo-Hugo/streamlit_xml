import os
import time
import streamlit as st
from playwright.sync_api import sync_playwright

def download_xml_with_playwright(manual_keys, download_path):
    if 'is_stopped' not in st.session_state:
        st.session_state.is_stopped = False
    if 'files_saved' not in st.session_state:
        st.session_state.files_saved = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Inicia o navegador headless
        context = browser.new_context()
        page = context.new_page()

        link = "https://meudanfe.com.br"
        page.goto(link)
        time.sleep(5)  # Tempo de espera para garantir o carregamento do site

        chaves = manual_keys.strip().split("\n") if manual_keys else []
        if not chaves:
            st.warning("Nenhuma chave fornecida. Insira as chaves manualmente.")
            return

        for i, codigo_chave in enumerate(chaves):
            if st.session_state.is_stopped:
                st.warning("Automação interrompida.")
                break

            try:
                # Localiza o campo de entrada e insere a chave
                page.fill('xpath=//*[@id="get-danfe"]/div/div/div[1]/div/div/div/input', codigo_chave)
                time.sleep(2)

                # Clica no botão de busca
                page.click('xpath=//*[@id="get-danfe"]/div/div/div[1]/div/div/div/button')
                time.sleep(2)

                # Aguarda e clica no botão de download
                if page.locator('xpath=/html/body/div[1]/div/div[1]/div/div[2]/button[1]').is_visible():
                    page.click('xpath=/html/body/div[1]/div/div[1]/div/div[2]/button[1]')
                    st.session_state.files_saved += 1
                    time.sleep(1)

                    # Renomeia o arquivo baixado
                    downloaded_file = max([f for f in os.listdir(download_path)], key=lambda x: os.path.getctime(os.path.join(download_path, x)))
                    new_file_name = f"{codigo_chave}.xml"
                    os.rename(os.path.join(download_path, downloaded_file), os.path.join(download_path, new_file_name))
                else:
                    st.warning(f"Captcha não resolvido para a chave {codigo_chave}. Pulando para a próxima chave.")
                    continue

                # Fecha a janela do modal de download
                page.click('xpath=/html/body/div[1]/div/div[1]/div/div[1]/button')
                time.sleep(1)

            except Exception as e:
                st.error(f"Erro ao processar a chave {codigo_chave}: {e}")

        browser.close()
    st.success("Processo concluído!" if not st.session_state.is_stopped else "Processo interrompido!")
    st.info(f"Número total de arquivos salvos: {st.session_state.files_saved}")

# Função principal para a interface Streamlit
def main():
    st.title("Download de XML")

    manual_keys = st.text_area("Insira as chaves de acesso (uma por linha):", key="manual_keys")
    download_path = st.text_input("Informe o caminho de salvamento do XML:", value=os.getcwd())

    start_button = st.button("Iniciar Download")
    stop_button = st.button("Interromper", on_click=lambda: toggle_stop())
    clear_button = st.button("Limpar", on_click=clear_input)

    if start_button:
        st.session_state.is_stopped = False
        download_xml_with_playwright(manual_keys, download_path)

    st.markdown("<div style='text-align: right;'>Criado por Hugo Silva.</div>", unsafe_allow_html=True)

def toggle_stop():
    st.session_state.is_stopped = True

def clear_input():
    st.session_state.manual_keys = ""
    st.session_state.is_stopped = False
    st.session_state.files_saved = 0

if __name__ == "__main__":
    main()
