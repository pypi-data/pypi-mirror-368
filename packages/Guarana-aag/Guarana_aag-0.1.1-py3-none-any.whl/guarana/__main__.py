import argparse

from . import comandos
from .config import *

descricao = f"{NOME}: estrutura de front-end para Flask. Versão: {VERSAO}"


def main():
    parser = argparse.ArgumentParser(description=descricao)
    subparsers = parser.add_subparsers(dest='comando')

    flask_help = 'Instala a estrutura básica de flask'
    instalar = subparsers.add_parser(
        'instalar',
        help=f'Instala o'
        f' {COR_AMARELO}{NOME}{COR_FIM} na pasta {COR_VERDE}{PASTA_STATIC}/{COR_FIM}, '
        f'criando as subpastas {COR_VERDE}/{PASTA_CSS}/{COR_FIM} '
        f'e {COR_VERDE}/{PASTA_CSS}/{COR_FIM}, junto de seus conteúdo\t'
        f'{COR_AMARELO}--flask{COR_FIM}: {flask_help}'
    )
    instalar.add_argument(
        '--flask', action='store_true',
        help=flask_help
    )

    atualizar = subparsers.add_parser(
        'atualizar',
        help=f'Atualiza a base do '
             f'{COR_AMARELO}{NOME}{COR_FIM} '
             f'recriando o arquivo {COR_VERDE}{ARQUIVO_BASE}{COR_FIM} '
             f'com todas suas atualizações e alterações. '
    )

    resetar = subparsers.add_parser(
        'resetar',
        help=f'Gera todos os arquivos de usuário novamente para o '
             f'{COR_AMARELO}{NOME}{COR_FIM}.'
             f'\n {COR_BRANCO}{COR_FUNDO_VERMELHO}ATENÇÃO:'
             f'{COR_FIM}'
             f' essa ação é irreversível e tudo o que você tenha feito será perdido'
             f' a menos que você tenha backup ou esteja usando GIT'
    )

    minificar = subparsers.add_parser(
        'min',
        help=f'Observa qualquer alteração na pasta {PASTA_CSS} e recria '
             f'o arquivo {COR_AMARELO}estilo-min.css{COR_FIM} a cada alteração'
    )

    rodar = subparsers.add_parser(
        'rodar',
        help=f'Roda a documentação e exemplos para o caso de não estar usando o Flask.\n'
             f'Endereço é http://localhost:{PORTA_LOCAL}'
    )

    args = parser.parse_args()
    match args.comando:
        case 'instalar': comandos.instalar_guarana(args.flask)
        case 'atualizar': comandos.atualizar(resetar=False)
        case 'resetar': comandos.atualizar(resetar=True)
        case 'min': comandos.observar_min_css()
        case 'rodar': comandos.rodar_doc()
        case _: parser.print_help()

if __name__ == "__main__":
    main()
    