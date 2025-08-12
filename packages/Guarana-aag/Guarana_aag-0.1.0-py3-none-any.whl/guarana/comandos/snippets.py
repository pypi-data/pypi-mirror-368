from pathlib import Path

from ..config import *

def gerar_snippets():
    raiz = Path(__file__).absolute().parent.parent.parent.parent/'.vscode'
    pasta_snippets = Path.cwd()/'.vscode'
    arquivos = ['guarana-html.code-snippets', 'guarana-css.code-snippets',
                'guarana-js.code-snippets']
    
    if not pasta_snippets.exists():
        pasta_snippets.mkdir()

    for arquivo in arquivos:
        texto = Path(raiz / arquivo).read_text()
        Path(pasta_snippets / arquivo).write_text(texto, encoding='utf-8')
