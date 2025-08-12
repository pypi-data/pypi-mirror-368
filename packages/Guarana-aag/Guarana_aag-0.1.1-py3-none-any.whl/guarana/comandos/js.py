from pathlib import Path
from datetime import date

from ..config import *
from .helpers import separador, caminho_pasta_existente

hoje = date.today().strftime("%d/%m/%Y")

texto_abertura = \
f"""// {separador()}
// ARQUIVO BASE DE {NOME}
// NÃO ALTERE! ELE É GERADO AUTOMATICAMENTE E TUDO SE PERDE AO ATUALIZAR
// FAÇA SUAS INCLUSÕES E USOS DESSAS FUNÇÕES EM OUTRO ARQUIVO
// {separador('-')}
// Versão: {VERSAO}
// Última alteração nesse sistema em: {hoje}
// {separador()}\n\n
"""

def gerar_js(resetar: bool = False):
    origem = PASTA_ORIGEM/PASTA_JS/'guarana.js'
    destino = caminho_pasta_existente(PASTA_JS)/'guarana.js'

    if destino.exists() and not resetar:
        return

    texto_origem = origem.read_text('utf-8')
    destino.write_text(texto_abertura + texto_origem)

