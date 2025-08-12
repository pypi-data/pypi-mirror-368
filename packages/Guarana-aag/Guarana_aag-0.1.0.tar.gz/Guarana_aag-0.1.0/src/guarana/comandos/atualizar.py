from pathlib import Path

from ..config import *
from .helpers import criar_pasta, copiar_arquivo, copiar_pasta_inteira, separador, caminho_pasta_existente
from .js import gerar_js
from .snippets import gerar_snippets
from .criar_css import criar_base_css, criar_estilo_css


def atualizar(resetar:bool=False):
    pasta_static = caminho_pasta_existente('static')
    if not pasta_static:
        print(f'{COR_VERMELHO}Guaraná não foi detectado{COR_FIM}. Execute o comando {COR_AMARELO}instalar{COR_FIM}')
        return
    
    criar_base_css()
    criar_estilo_css(resetar)
    gerar_js(resetar)
    gerar_snippets()
