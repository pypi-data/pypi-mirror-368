import tomllib
import colorama
from pathlib import Path

try:
    _PROJETO = Path(__file__).parent.parent.parent / 'pyproject.toml'
    with open(_PROJETO, 'rb') as arquivo:
        _PROJETO_TOML = tomllib.load(arquivo)
    # Pega os dados da seção [project do TOML]
    PROJETO_METADATA = _PROJETO_TOML.get("project", {})
except (FileNotFoundError, tomllib.TOMLDecodeError):
    # Fallback caso o arquivo não seja encontrado ou seja inválido
    PROJETO_METADATA = {}

APP = PROJETO_METADATA.get('name', 'Front_End_Base')
NOME = APP.replace('_aag', '')
VERSAO = PROJETO_METADATA.get('version', '0.0.0-dev')
_autores = PROJETO_METADATA.get('authors', [{'name': 'Alessandro Guarita'}])
AUTOR = _autores[0].get('name', 'Alessandro Guarita') if _autores else 'Alessandro Guarita'

PORTA_LOCAL = 5000

PASTA_ORIGEM = Path(__file__).parent/'origem'
PASTA_APP = 'app'
PASTA_STATIC = 'static'
PASTA_CSS = 'css'
PASTA_JS = 'js'
PASTA_UTILS = f'utils_{NOME.lower()}'
PASTA_VIEWS = 'views'
ARQUIVO_BASE = '_guarana_base.css'

COR_AMARELO = colorama.Fore.YELLOW
COR_VERMELHO = colorama.Fore.RED
COR_AZUL = colorama.Fore.BLUE
COR_VERDE = colorama.Fore.GREEN
COR_BRANCO = colorama.Fore.WHITE

COR_FUNDO_VERMELHO = colorama.Back.RED
COR_FIM = colorama.Style.RESET_ALL
