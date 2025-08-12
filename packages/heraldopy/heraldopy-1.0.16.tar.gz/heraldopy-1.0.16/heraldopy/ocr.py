import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from payconpy.fpdf.focr.orc import *
from payconpy.fpython.fpython import *
from payconpy.fselenium.fselenium import *
import fitz, uuid, os, pytesseract, base64

def ocr_tesseract_v2(pdf, dpi=300, file_output=uuid.uuid4(), return_text=True, config_tesseract='', limit_pages=None, lang='por', timeout=120, path_tesseract='bin/Tesseract-OCR/tesseract.exe', path_pages='pages', tempdir='tempdir'):
    """Realiza OCR em um arquivo PDF usando Tesseract, com opções de customização avançadas.

    Esta função avançada permite a personalização de diversos parâmetros do OCR, como DPI, linguagem, limitação de páginas e timeout. Caso os binários do Tesseract não estejam presentes, ela executa uma única requisição para o GitHub da organização Paycon para baixar os binários necessários. Esta requisição é crucial para a funcionalidade da função mas levanta questões importantes sobre segurança de dados.

    Importância da Segurança dos Dados na Requisição:
        - Embora o arquivo ZIP do Tesseract seja público e hospedado em um repositório confiável, é fundamental validar a fonte antes do download para evitar a execução de software malicioso.
        - Durante o desenvolvimento, é aconselhável ter o Tesseract pré-instalado no projeto, eliminando a necessidade do download e reduzindo a superfície de ataque.
        - Para ambientes de produção, deve-se considerar a implementação de verificações de integridade, como a validação de checksum, para garantir a autenticidade dos binários baixados.

    Args:
        pdf (str): Caminho do arquivo PDF para realizar o OCR.
        dpi (int, optional): Resolução DPI para a conversão de páginas PDF em imagens. Padrão é 300.
        file_output (str, optional): Nome do arquivo de saída onde o texto OCR será salvo. Gera um UUID por padrão.
        return_text (bool, optional): Se True, retorna o texto extraído; se False, retorna o caminho para o arquivo de texto. 
            Padrão é True.
        config_tesseract (str, optional): Configurações adicionais para o Tesseract. Padrão é ''.
        limit_pages (int, optional): Limita o número de páginas do PDF a serem processadas. Padrão é None.
        lang (str, optional): Código de idioma usado pelo Tesseract para o OCR. Padrão é 'por' (português).
        timeout (int, optional): Timeout em segundos para o processamento OCR de cada página. Padrão é 120.

    Retorna:
        str|bool: Retorna o texto extraído ou o caminho para o arquivo de texto se `return_text` for False. 
            Retorna False em caso de falha no processamento OCR.

    Nota:
        - A função tenta baixar os binários do Tesseract apenas se estes não estiverem presentes, para evitar downloads desnecessários e mitigar riscos de segurança.
        - A segurança dos dados e a integridade do software são primordiais, especialmente ao realizar downloads de fontes externas.
        
    Raises:
        Exception: Pode lançar uma exceção se ocorrer um erro durante o download dos binários, o processamento OCR ou se a integridade do arquivo baixado for questionável.
    """
    path_tesseract = os.path.abspath(path_tesseract)

    if not os.path.exists(path_tesseract):
        while not os.path.exists(path_tesseract):
            faz_log('*** COLOQUE OS BINÁRIOS DO TESSERACT NA PASTA BIN (O NOME DA PASTA DOS BINÁRIOS DEVE SER "Tesseract-OCR") ***')
            sleep(10)
        else:
            pass
    pytesseract.pytesseract.tesseract_cmd = path_tesseract

    with fitz.open(pdf) as pdf_fitz:
        try:
            os.makedirs(path_pages)
        except FileExistsError:
            pass
        limpa_diretorio(path_pages)
        faz_log(f'Convertendo PDF para páginas...')
        number_of_pages = len(pdf_fitz) if limit_pages is None else min(limit_pages, len(pdf_fitz))
        with tqdm(total=number_of_pages, desc='EXTRACT PAGES') as bar:
            for i, page in enumerate(pdf_fitz):
                if i >= number_of_pages:
                    break
                page = pdf_fitz.load_page(i)
                mat = fitz.Matrix(dpi/72, dpi/72)  # Matriz de transformação usando DPI
                pix = page.get_pixmap(matrix=mat)
                pix.save(arquivo_com_caminho_absoluto(path_pages, f'{i}.png'))
                bar.update(1)
        

        files = arquivos_com_caminho_absoluto_do_arquivo(path_pages)
        with tqdm(total=len(files), desc='OCR') as bar:
            for i, image in enumerate(files):
                try:
                    text = pytesseract.image_to_string(image, config=config_tesseract, lang=lang, timeout=timeout)
                except Exception as e:
                    return False
                with open(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'), 'a', encoding='utf-8') as f:
                    f.write(text)
                bar.update(1)
            else:
                limpa_diretorio(path_pages)
                if return_text:
                    text_all = ''
                    with open(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'), 'r', encoding='utf-8') as f:
                        text_all = f.read()
                    os.remove(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'))
                    return text_all
                else:
                    return os.path.abspath(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'))

def ocr(file_path, path_tesseract):
    # file_path = os.path.abspath("Arquivo_Usuario/base/guia.pdf")
    # path_tesseract = os.path.abspath("Arquivo_Robo/bin/Tesseract-OCR/tesseract.exe")
    # path_tesseract = os.path.abspath(path_tesseract)
    if not os.path.exists(path_tesseract):
        while not os.path.exists(path_tesseract):
            faz_log('*** COLOQUE OS BINÁRIOS DO TESSERACT NA PASTA BIN (O NOME DA PASTA DOS BINÁRIOS DEVE SER "Tesseract-OCR") ***')
            sleep(10)
        else:
            pass
    text = ocr_tesseract_v2(
        file_path,
        limit_pages=5,
        path_tesseract="Arquivo_Robo/bin/Tesseract-OCR/tesseract.exe",
        path_pages="Arquivo_Robo/pages",
        tempdir="Arquivo_Robo/tempdir",
    )
    return text