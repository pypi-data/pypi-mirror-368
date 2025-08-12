import os
import wget
import time
import shutil
import base64
import zipfile
import requests
import numpy as np
import pandas as pd
import tkinter as tk
from subprocess import run, PIPE
from tkinter import messagebox, Tk
from payconpy.utils.utils import *
from rapidfuzz import fuzz, process
from payconpy.fpython.fpython import *
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication

def wait_for_downloads(directory, timeout=600):
    """
    Waits until there are no files with .crdownload or .part extensions in the directory,
    indicating that all downloads have completed.

    Parameters:
    - directory: The directory to monitor for downloads.
    - timeout: Maximum time to wait for downloads to complete, in seconds.

    Returns:
    - True if all downloads are completed within the timeout period, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(directory)
        if not any(file.endswith((".crdownload", ".part")) for file in files):
            return True
        time.sleep(1)
    return False

def apaga_e_printa(frase, color="white"):
    os.system("cls" if os.name == "nt" else "clear")
    faz_log(frase, color=color)  # Assuming faz_log is defined elsewhere

def progress_bar(current, total, bar_length=40):
    """
    Generates a text-based progress bar.

    Args:
        current (int): The current progress.
        total (int): The value representing 100% progress.
        bar_length (int): The length of the progress bar (default is 20).

    Returns:
        str: A string representing the progress bar.
    """
    if total == 0:
        return "Progress: [ERROR - Total cannot be zero]"

    progress = current / total
    if progress > 1:
        progress = 1  # Cap the progress at 100%

    filled_length = int(bar_length * progress)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    percentage = progress * 100
    return f"PROGRESSO: [{bar}] {percentage:.1f}%"

def show_success_popup(titulo, mensagem):
    """Displays a success popup window."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(titulo, mensagem)
    root.destroy()

def find_elements_with_retry(driver, wait_time, locator, retries=3):
    """Finds elements and retries if a StaleElementReferenceException occurs."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import StaleElementReferenceException

    for attempt in range(retries):
        try:
            elements = WebDriverWait(driver, wait_time).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except StaleElementReferenceException:
            if attempt == retries - 1:
                raise

def find_element_text_with_retry(driver, wait_time, locator, retries=3):
    """Finds element text and retries on StaleElementReferenceException."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import StaleElementReferenceException

    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located(locator)
            )
            return element.text
        except StaleElementReferenceException:
            if attempt == retries - 1:
                raise

def download_file(file_id, access_token, download_path):
    headers = {"Authorization": f"Bearer {access_token}"}
    download_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
    response = requests.get(download_url, headers=headers, stream=True)

    if response.status_code == 200:
        with open(download_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {download_path}")
    else:
        print(f"Failed to download file: {response.json()}")

# List files in the folder and download each file
def list_and_download_files(
    access_token, folder_id, download_dir, scope, client_id, client_secret, tenant_id
):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children",
        headers=headers,
    )

    if response.status_code == 200:
        items = response.json().get("value", [])
        for item in items:
            if "file" in item:  # Check if the item is a file
                file_id = item["id"]
                file_name = item["name"]
                file_path = os.path.join(download_dir, file_name)
                download_file(file_id, access_token, file_path)
    elif response.status_code == 401:  # Token expired, retry with a new token
        app = ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret,
        )
        result = app.acquire_token_for_client(scopes=scope)
        if "access_token" in result:
            list_and_download_files(
                result["access_token"],
                folder_id,
                download_dir,
                scope,
                client_id,
                client_secret,
                tenant_id,
            )
        else:
            print("Failed to obtain access token.")
            print(result.get("error_description", "No error description available."))
            print(result.get("claims", "No claims available."))
    else:
        print(f"Failed to list files: {response.json()}")

def imprime_iframe(driver):
    iframe_id = driver.execute_script("return window.frameElement ? window.frameElement.id : '';")
    iframe_name = driver.execute_script("return window.frameElement ? window.frameElement.name : '';")
    
    faz_log(f"ID do iframe atual: {iframe_id}")
    faz_log(f"Nome do iframe atual: {iframe_name}")
    return

def retorna_id_iframe_para_variavel(driver):
    iframe_id = driver.execute_script("return window.frameElement ? window.frameElement.id : '';")

    return iframe_id

def pega_primeiro_arquivo_da_pasta(caminho):
    '''
    Retorna um padas dataframe com todas as colunas em formato string 
    para o primeiro arquivo da pasta que contém o caminho informado.
    
    Variáveis:
    caminho(string): Caminho relativo ao main branch da pasta que contém os arquivos.
    '''
    
    df = pd.read_excel(
            arquivos_com_caminho_absoluto_do_arquivo(caminho)[0],
            dtype=str,
        )
    
    return df

def simplify_name(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return parts[0], parts[0]
