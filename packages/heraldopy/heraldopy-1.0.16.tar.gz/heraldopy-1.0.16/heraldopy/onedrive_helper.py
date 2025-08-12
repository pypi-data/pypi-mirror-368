import os
import re
import time
import base64
import requests
from msal import ConfidentialClientApplication


def baixar_arquivos_onedrive(
    client_id,
    client_secret,
    tenant_id,
    caminho_pasta,
    folder_link,
    comentarios=False
    # baixar_tudo=False,
    # pasta_registros="base",
    # nome_coluna="caso",
    # nome_pasta="historico",
):
    '''
    A função original criada para o SPC possui uma lógica que verifica se o arquivo já foi baixado
    Esta parte foi removida para não ser preciso passar diversas variáveis desnecessárias
    A parte removida se encontrava no else após o if baixar_tudo
    '''
    if comentarios:
        print("Iniciando o download do banco de dados dos processos encontrados")

    local_download_path = caminho_pasta
    # dataset_path = f"{pasta_registros}/{nome_pasta}.xlsx"  # Path to your dataset

    # Carregando o nome do arquivos já baixados
    # if comentarios:
        # print("Carregando o nome do arquivos já baixados")
    # df = pd.read_excel(dataset_path)
    # downloaded_files = set(
    #     df[nome_coluna]
    # )  # Assuming 'nome' column contains the file names

    # Gerando token de acesso
    if comentarios:
        print("Gerando token de acesso")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    token_response = requests.post(token_url, data=token_data)
    token_response.raise_for_status()
    access_token = token_response.json().get("access_token")

    # Codificando o link da pasta no formato base64
    if comentarios:
        print("Codificando o link da pasta no formato base64")
    encoded_link = base64.b64encode(folder_link.encode()).decode()
    encoded_link = encoded_link.replace("/", "_").replace("+", "-").replace("=", "")

    # Acessando a pasta do OneDrive
    if comentarios:
        print("Acessando a pasta do OneDrive")
    headers = {"Authorization": f"Bearer {access_token}"}
    shared_link_url = (
        f"https://graph.microsoft.com/v1.0/shares/u!{encoded_link}/driveItem"
    )
    shared_link_response = requests.get(shared_link_url, headers=headers)
    shared_link_response.raise_for_status()
    drive_item = shared_link_response.json()

    # Listando os arquivos na pasta do OneDrive
    if comentarios:
        print("Codificando o link da pasta no formato base64")
    folder_id = drive_item["id"]
    files_url = f'https://graph.microsoft.com/v1.0/drives/{drive_item["parentReference"]["driveId"]}/items/{folder_id}/children'
    files_response = requests.get(files_url, headers=headers)
    files_response.raise_for_status()
    files = files_response.json().get("value", [])

    # Baixando arquivos pendentes
    if comentarios:
        print("Baixando arquivos pendentes")
    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)

    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bearer {access_token}"})

        for file in files:
            file_name = file["name"]
            # if baixar_tudo:
            if comentarios:
                print(f"Baixando arquivo entitulado {file_name}")

            for attempt in range(3):  # Retry up to 3 times
                try:
                    file_id = file["id"]
                    download_url = f'https://graph.microsoft.com/v1.0/drives/{drive_item["parentReference"]["driveId"]}/items/{file_id}/content'
                    file_response = session.get(
                        download_url, timeout=30
                    )  # Increased timeout
                    file_response.raise_for_status()

                    with open(
                        os.path.join(local_download_path, file_name), "wb"
                    ) as f:
                        f.write(file_response.content)

                    if comentarios:
                        print(f"Arquivo baixado com sucesso!")
                    break  # Exit loop if successful
                except requests.exceptions.ConnectionError as e:
                    if attempt < 2:  # Check if this is not the last attempt
                        time.sleep(5)  # Wait for 5 seconds before retrying
                        continue  # Retry
                    else:
                        raise e  # Re-raise the exception after all retries
    if comentarios:
        print(
            f"\nProcesso de atualização do banco de dados concluido!"
        )

def generate_access_token(client_id, client_secret, tenant_id):
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    token_response = requests.post(token_url, data=token_data)
    token_response.raise_for_status()
    return token_response.json().get("access_token")

def get_site_drive_folder_ids(folder_link, access_token):
    # Ensure folder_link is a string
    if not isinstance(folder_link, str):
        raise ValueError(
            "Expected a string for 'folder_link', got: " + str(type(folder_link))
        )

    # Encode the folder link to base64
    encoded_link = base64.b64encode(folder_link.encode()).decode()
    encoded_link = encoded_link.replace("/", "_").replace("+", "-").replace("=", "")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 1: Get the drive item details from the shared link
    shared_link_url = (
        f"https://graph.microsoft.com/v1.0/shares/u!{encoded_link}/driveItem"
    )
    response = requests.get(shared_link_url, headers=headers)
    response.raise_for_status()
    drive_item = response.json()

    # Extract the drive ID, folder ID, and site ID from the drive item
    drive_id = drive_item["parentReference"]["driveId"]
    folder_id = drive_item["id"]
    site_id = drive_item["parentReference"]["siteId"]

    return site_id, drive_id, folder_id

def upload_file_to_onedrive(
    client_id, client_secret, tenant_id, file_path, folder_link
):
    """
    Uploads a file to a specific folder in OneDrive using Microsoft Graph API.

    Parameters:
    - client_id (str): Azure AD application client ID.
    - client_secret (str): Azure AD application client secret.
    - tenant_id (str): Azure AD tenant ID.
    - file_path (str): The local path to the file to upload.
    - folder_link (str): The shared link to the folder in OneDrive.

    Returns:
    - None: No output to terminal.
    """
    # Generate access token using the provided function
    access_token = generate_access_token(client_id, client_secret, tenant_id)

    # Get site_id, drive_id, and folder_id using the existing function
    site_id, drive_id, folder_id = get_site_drive_folder_ids(folder_link, access_token)

    # Get file name from the path
    file_name = os.path.basename(file_path)

    # Construct the upload URL
    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{folder_id}:/{file_name}:/content"

    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/octet-stream",
    }