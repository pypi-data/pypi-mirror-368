# Guaraná
Baseado no Front_Alego, gem de Ruby que desenvolvi para a Assembleia Legislativa do Estado de Goiás, esse módulo Python instala um framework css funcional para módulos Flask ou mesmo para HTML estático, que dá a base para trabalhar, sem limitar com um estilo fixo caso decida alterar, mas também permite fazer um site rápido com mudanças mínimas.

Além dos arquivos de CSS, inclui alguns JS básicos para algumas funcionalidades pontuais e vários snippets de VSCode para facilitar o uso.

[Changelog](changelog.md)

## Instalando
Para o funcionamento é necessário Python 3.12 ou superior. No seu ambiente virtual execute:

```bash
pip install guarana_aag
```

Na pasta do seu sistema execute o comando
```bash
python -m guarana instalar
```

Como parâmetro opcional, utilize `--flask` caso seu sistema esteja zerado, isso vai instalar também os arquivos básicos para um sistema em flask, incluindo views como a 404.html

Para atualizar os arquivos do guarana, utilize o comando:
```bash
python -m guarana atualizar
```
Esse comando vai substituir o arquivo base com a nova versão do Guaraná.

Para uma atualização mais profunda, utilize o comando:
```bash
python -m guarana resetar
```
Esse comando vai gerar novamente os arquivos do Guaraná, incluindo os de usuário, como o `estilo.css`. Tenha um backup antes de utilizar esse comando ou você perderá muito de seu trabalho


## CSS a ser usado
Depois de instalado, serão criados alguns arquivos de `.css` na raíz.

- `_guarana_base.css` - esse arquivo contém a base do Guaraná e não deve ser alterado, já que é gerado dinamicamente
- `estilo.css` - o arquivo a ser trabalhado. Ele pode ser importado diretamente no HTML. Note, porém, que há muitos `@import` o que gera várias requisições HTTP
- `estilo-min.css` - todo o Guaraná compactado em um único CSS, importe no HTML para ser mais eficiente posteriormente. Esse arquivo é gerado dinamicamente através do comando:

```bash
python -m guarana min
```

## Estrutura Flask instalada
Os seguinte arquivos são instalados quando executa da função `--flask`:

- `rodar.py` - ativa o servidor para rodar o sistema
- `requirements.txt` - os módulos básicos necessários para rodar o Guaraná
- `app/config.py` - utilize esse arquivo para configurar o sistema com constantes utilizadas nos demais arquivos
- `app/routes.py` - as rotas para o índice e a tela de login
- `templates/...` - os 4 modelos básicos, incluindo o `modelo.html` que é a base para o Guaraná e todas as views. `login.html` e `internas.html` separa os tipos de páginas.

### Configurações
O arquivo de configurações (`config.py`) inclue as seguintes constantes:
- `ESTILO` - escolha qual o CSS a ser usado (como indicado na seção de CSS):
    - `padrao` - o estilo tradicional, não compactado
    - `min` - o estilo minificado. Esse é o valor padrão
- `TITULO` - inclua aqui o título do sistema, que aparece na tag `<title>`
