import re
from pathlib import Path
from datetime import date

from ..config import *
from .helpers import separador, caminho_pasta_existente

hoje = date.today().strftime("%d/%m/%Y")

# region HEADERS
texto_base_header =\
f"""
/*
{separador()}
ARQUIVO BASE DE {NOME}
NÃO ALTERE! ELE É GERADO AUTOMATICAMENTE E TUDO SE PERDE AO ATUALIZAR
FAÇA ALTERAÇÕES NO estilo.css
{separador('-')}
Versão: {VERSAO}
Última alteração nesse sistema em: {hoje}
{separador()}
*/\n
"""

texto_estilo_header =\
f"""
/*
{separador()}
Arquivo principal do sistema utilizando {NOME}
Se for o usar o estilo-min.css, altere tudo aqui e execute o comando:
python -m {NOME.lower()} min
{separador('-')}
Criado nesse sistema em: {hoje}
Versão do {NOME} neste arquivo: {VERSAO}
{separador()}
*/
"""
# endregion


def criar_base_css():
    """
    Cria o arquivo SCSS base, que vai incluir todos os elementos e será importado
    para o arquivo principal
    """
    pasta_base = PASTA_ORIGEM/PASTA_CSS/'base'
    pasta_destino = caminho_pasta_existente(PASTA_CSS)
    arquivo_destino = pasta_destino/ARQUIVO_BASE
    arquivos = list(pasta_base.glob('*'))

    texto = texto_base_header

    for arquivo in arquivos:
        texto += arquivo.read_text()

    if not arquivo_destino.exists():
        print(f'Arquivo {COR_VERDE}{pasta_destino}/{ARQUIVO_BASE}{COR_FIM} criado')
    else:
        print(f'Arquivo {COR_VERMELHO}{pasta_destino}/{ARQUIVO_BASE}{COR_FIM} reescrito')

    arquivo_destino.write_text(texto)


def criar_import_utils_css():
    # TODO: verifica a pasta PASTA_UTILS no sistema e importa tudo
    pass


def criar_estilo_css(resetar:bool=False):
    """
    Cria o arquivo CSS estilo.css para o usuário trabalhar
    """
    arquivo_original = PASTA_ORIGEM/PASTA_CSS/'estilo.css'
    pasta_destino = caminho_pasta_existente(PASTA_CSS)
    arquivo_destino = pasta_destino/'estilo.css'

    texto = texto_estilo_header
    texto += arquivo_original.read_text()
    texto = texto.replace('ARQUIVO_BASE', ARQUIVO_BASE)

    if not arquivo_destino.exists():
        print(
            f'Arquivo {COR_VERDE}{pasta_destino}/estilo.css{COR_FIM} criado')
    elif resetar:
        print(
            f'Arquivo {COR_VERMELHO}{pasta_destino}/estilo.css{COR_FIM} reescrito')
    else:
        criar_estilo_css_min()
        return


    arquivo_destino.write_text(texto)
    criar_estilo_css_min()


def criar_estilo_css_min():
    pasta_destino = caminho_pasta_existente(PASTA_CSS)
    arquivo_destino = pasta_destino/'estilo-min.css'

    header = f'/*{NOME}:{hoje}*/'
    texto = Path(pasta_destino/'estilo.css').read_text()

    while '@import' in texto:
        texto = substituir_imports(texto)

    if arquivo_destino.exists():
        print(f'Atualizado {COR_AMARELO}estilo-min.css{COR_FIM}')
    else:
        print(f'Gerando {COR_AMARELO}estilo-min.css{COR_FIM}')

    arquivo_destino.write_text(header+minificar_css(texto))


def substituir_imports(css:str):
    padrao = r'@import\s+url\(([^)]+)\);'
    matches = re.findall(padrao, css)
    pasta_destino = caminho_pasta_existente(PASTA_CSS)

    for caminho in matches:
        try:
            arquivo = pasta_destino/caminho.strip()
            conteudo = arquivo.read_text()
            css = re.sub(
                rf'@import\s+url\({re.escape(caminho)}\);',
                conteudo, 
                css)
        except FileNotFoundError:
            print(f"Arquivo '{caminho}' não encontrado.")
        except Exception as e:
            print(f"Erro ao ler '{caminho}': {e}")

    return css


def minificar_css(css:str):
    css_sem_comentarios = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    
    # Remove quebras de linha, tabulações e espaços extras
    css_minificado = re.sub(r'\s+', ' ', css_sem_comentarios)

    # Remove espaços ao redor de símbolos comuns
    css_minificado = re.sub(r'\s*([{};:,])\s*', r'\1', css_minificado)
    
    return css_minificado.strip()
