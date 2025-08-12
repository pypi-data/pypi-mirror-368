from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

from .helpers import caminho_pasta_existente
from ..config import *
from .criar_css import criar_estilo_css_min

ARQUIVO_EXCECAO = 'estilo-min.css'


class ObservarPastaCSS(FileSystemEventHandler):
    def on_modified(self, event):
        caminho = Path(event.src_path)
        if not caminho.is_dir():
            if caminho.name == ARQUIVO_EXCECAO:
                return
            
            print(f'Arquivo modificado: {COR_AMARELO}{caminho.name}{COR_FIM}.')
            criar_estilo_css_min()


def observar_min_css():
    print('Monitorando alterações no CSS... Aperte ctrl+c para cancelar')
    pasta_monitorada = Path(caminho_pasta_existente(PASTA_CSS))

    observer = Observer()
    observer.schedule(ObservarPastaCSS(), path=str(
        pasta_monitorada), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
