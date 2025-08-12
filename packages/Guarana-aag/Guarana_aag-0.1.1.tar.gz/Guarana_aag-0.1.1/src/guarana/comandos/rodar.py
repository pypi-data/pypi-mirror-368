from flask import Flask, render_template, abort
from pathlib import Path
from datetime import date
import markdown
import json
import re

from ..config import *
from ..doc.tabelas import *

dia_hoje = date.today().day

def rodar_doc():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['PORT'] = PORTA_LOCAL
    app.static_folder = '../doc/static'
    app.template_folder = '../doc/templates'

    print('Rodando o Front_End em segundo plano.')
    print(f'Endereço para acessar: {COR_VERMELHO}http://localhost:{PORTA_LOCAL}{COR_FIM}')

    # --------------------------------------------------------------------------
    # Coleta de Contexto
    # --------------------------------------------------------------------------
    # Os dados são coletados uma vez na inicialização para otimizar o desempenho.
    arquivo_atual = Path(__file__).resolve()
    # Navega para o diretório raiz do projeto
    raiz = arquivo_atual.parent.parent.parent.parent

    # Importa o changelog
    md = {}
    try:
        with open(raiz / 'changelog.md', 'r', encoding='utf-8') as f:
            md_lido = f.read()
            md['changelog'] = markdown.markdown(md_lido)
    except FileNotFoundError:
        md['changelog'] = '<p>Arquivo changelog.md não encontrado.</p>'

    # Importa os snippets
    snippets_path = raiz / '.vscode'
    snippets = {}
    for tipo in ['js', 'css', 'html']:
        arquivo = snippets_path / f'guarana-{tipo}.code-snippets'
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                snippets[tipo] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            snippets[tipo] = {}


    # Mapeia as views a partir dos arquivos HTML para a criação do menu
    pasta_modelos = Path(__file__).absolute().parent.parent / 'doc/templates/views'
    padrao_article = r"<article\s+[^>]*class=['\"]conteudo__artigo[^'\"]*['\"][^>]*>"
    padrao_header = r"<h1>(.*?)</h1>"
    padrao_id = r"id=['\"]([^'\"]+)['\"]"
    padrao_categoria = r"data-categoria=['\"]([^'\"]+)['\"]"
    views = []
    valid_view_ids = set()

    if pasta_modelos.exists() and pasta_modelos.is_dir():
        for view_file in sorted(pasta_modelos.glob('*.html')):
            texto = view_file.read_text(encoding='utf-8')
            article_tag_match = re.search(padrao_article, texto)

            if not article_tag_match:
                continue

            article_tag = article_tag_match.group(0)
            id_match = re.search(padrao_id, article_tag)
            view_id = id_match.group(1) if id_match else None

            if view_id:
                header_match = re.search(padrao_header, texto)
                categoria_match = re.search(padrao_categoria, article_tag)

                titulo = header_match.group(
                    1) if header_match else view_id.capitalize()

                views.append({
                    'arquivo': view_file.name,
                    'id': view_id,
                    'categoria': categoria_match.group(1) if categoria_match else 'Sem categoria',
                    'titulo': titulo
                })
                valid_view_ids.add(view_id)


    # Dicionário com todo o contexto a ser passado para o template
    template_context = {
        'app': NOME.replace('na', 'ná'),
        'versao': VERSAO,
        'pasta_utils': PASTA_UTILS,
        'pasta_views': PASTA_VIEWS,
        'md': md,
        'snippets': snippets,
        'views': views,
        'prop_css': propriedades_css,
        'hoje': dia_hoje
    }

    # --------------------------------------------------------------------------
    #  GERANDO AS ROTAS
    # --------------------------------------------------------------------------
    @app.route('/')
    @app.route('/<string:view_id>')
    def show_page(view_id=None):
        """
        Renderiza a página principal.
        Esta função lida tanto com a raiz ('/') quanto com as views específicas ('/tabela').
        """
        # Se um view_id for fornecido na URL, verifica se ele é válido
        if view_id and view_id not in valid_view_ids:
            abort(404)

        return render_template(
            'index.html' if not view_id else f'views/{view_id}.html',
            **template_context)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    app.run()
