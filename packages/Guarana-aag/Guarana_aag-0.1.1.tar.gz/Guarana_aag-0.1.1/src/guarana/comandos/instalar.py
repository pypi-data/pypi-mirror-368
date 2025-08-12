from pathlib import Path

from ..config import *
from .helpers import criar_pasta, copiar_arquivo, copiar_pasta_inteira, separador, caminho_pasta_existente
from .atualizar import atualizar

#region flask
def criar_flask():
    print(f'{COR_AMARELO}Criando estrutura básica\n{separador('-')}{COR_FIM}')
    criar_pasta('app')
    criar_pasta('app/templates')

    print(f'\n{COR_AMARELO}Criando base do Flask\n{separador('-')}{COR_FIM}')
    criar_requirements()
    copiar_arquivo('rodar.py', 'rodar.py')
    copiar_pasta_inteira('app', 'app')
    copiar_pasta_inteira('templates', 'app/templates')


def criar_requirements():
    arquivo = 'requirements.txt'
    arquivo_origem = PASTA_ORIGEM / arquivo
    conteudo = Path.read_text(arquivo_origem)
    conteudo += f'{APP}=={VERSAO}'

    arquivo_final = Path(arquivo)
    if arquivo_final.exists():
        print(
            f'Arquivo {COR_VERMELHO}{arquivo}{COR_FIM} já existe, não foi criado')
    else:
        arquivo_final.write_text(conteudo, encoding='utf-8')
        print(f'Arquivo {COR_VERDE}{arquivo}{COR_FIM} criado')
# endregion


def retornar_pasta_static(criou_flask:bool=False):
    pasta_atual = Path.cwd()

    if caminho_pasta_existente(PASTA_STATIC):
        return caminho_pasta_existente(PASTA_STATIC)

    if criou_flask:
        return pasta_atual/PASTA_APP/PASTA_STATIC
        
    return pasta_atual/PASTA_STATIC


def prosseguir_atualizacao():
    pergunta = input(f'Já existe uma versão de {PASTA_STATIC}, deseja atualizar. S/n ')
    prosseguir = False if pergunta.lower() == 'n' else True

    if prosseguir:
        atualizar(True)
        return


def instalar_guarana(flask: bool=False):
    if flask:
        criar_flask()

    pasta_static = retornar_pasta_static(flask)

    if pasta_static.exists():
        prosseguir_atualizacao()
        return

    criar_pasta('.vscode')
    criar_pasta(pasta_static)
    criar_pasta(f'{pasta_static}/{PASTA_CSS}')
    criar_pasta(f'{pasta_static}/{PASTA_JS}')

    atualizar(True)

