from ...config import *

propriedades_css = [
    {
        'nome': '--cor-erro',
        'tipo': 'cor',
        'heranca': 'não',
        'uso': 'variável de cor vermelha para indicar erros ou urgência.<br /><code>--cor-txt: var(--cor-erro)</code>',
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-ok",
        "tipo": "cor",
        "heranca": "não",
        "uso": "variável de cor verde para indicar sucesso.<br /><code>--cor-bg: var(--cor-ok)</code>",
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-alerta",
        "tipo": "cor",
        "heranca": "não",
        "uso": "variável de cor amarela para indicar alerta, aviso.<br /><code>--cor-txt: var(--cor-alerta)</code>",
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--sans",
        "tipo": "texto separado por vírgulas",
        "heranca": "não",
        "uso": "valor padrão para fontes sem serifa. Use como completemento, da fonte que for usar, se for personalizar.<br /><code>--fonte: var(--sans)</code>",
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--serif",
        "tipo": "texto separado por vírgulas",
        "heranca": "não",
        "uso": "valor padrão para fontes serifadas. Use como completemento, da fonte que for usar, se for personalizar.<br /><code>--fonte: var(--serif)</code>",
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-1",
        "tipo": "cor",
        "heranca": "não",
        "uso": "variável de paleta de cores, a cor principal.<br /><code>--cor-txt: var(--cor-1)</code>",
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-2",
        "tipo": "cor",
        "heranca": "não",
        "uso": "variável de paleta de cores, a cor secundária.<br /><code>--cor-txt: var(--cor-2)</code>",
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-3",
        "tipo": "cor",
        "heranca": "não",
        "uso": "variável de paleta de cores, a cor terciária.<br /><code>--cor-txt: var(--cor-3)</code>",
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--rd",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": f"variável para arredondar a borda. Diversos elementos em utilitários fazem uso dessa variável por padrão, de forma que ao alterar o valor inicial, vai alterar diversos elementos do {NOME}<br /><code>border-radius: var(--rd)</code>",
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--sombra",
        "tipo": "valores separados por espaço",
        "heranca": "sim",
        "uso": f"variável para a sombra padrão. Diversos elementos em utilitários fazem uso dessa variável por padrão, de forma que ao alterar o valor inicial, vai alterar diversos elementos do {NOME}<br /><code>box-shadow: var(--sombra)</code>",
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--transicao",
        "tipo": "valores separados por espaço",
        "heranca": "sim",
        "uso": f"variável para a transição padrão, sem indicar qual a nome afetada. Diversos elementos em utilitários fazem uso dessa variável por padrão, de forma que ao alterar o valor inicial, vai alterar diversos elementos do {NOME}<br /><br /><code>transition: var(--transicao)</code>",
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-base",
        "tipo": "cor",
        "heranca": "-",
        "uso": "variável usada em diversos elementos internos. Serve como base para que seja aplicado tons nos elementos e permitindo alterações rápidas em todo o componente alterando apenas essa variável.<br /><code>--cor-bg: hsl(from var(--cor-base) h s calc(l * 1.25)</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-secundaria",
        "tipo": "cor",
        "heranca": "-",
        "uso": "variável usada em diversos elementos internos (menos usada que a <code>--cor-base</code>). Serve como base de cor secundária para que seja aplicado tons nos elementos e permitindo alterações rápidas em todo o componente alterando apenas essa variável.<br /><code>--cor-txt: hsl(from var(--cor-sec) h calc(s - 10) calc(l * .25)</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-bg",
        "tipo": "cor",
        "heranca": "-",
        "uso": "variável usada em diversos elementos e tags, mesmo no reset, que já contam com <code>background-color</code> para essa cor, bastando alterar essa variável. <br /><code>--cor-bg: red</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-txt",
        "tipo": "cor",
        "heranca": "-",
        "uso": "variável usada em diversos elementos e tags, mesmo no reset, que já contam com <code>color</code> para essa cor, bastando alterar essa variável. <br /><code>--cor-txt: hsl(0, 0%, 0%)</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--modo",
        "tipo": "color-scheme",
        "heranca": "-",
        "uso": "Variável usada no :root e em eventual tema para determinar qual o modo de cor usado. O root já faz uso de<br /><code>color-scheme</code>, bastando alterar o modo quando indicado. Veja mais em <a href='cores'>cores</a><br /><code>--modo: dark</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--fonte",
        "tipo": "texto separado por vírgula",
        "heranca": "-",
        "uso": "variável usada no <code>&lt;body&gt;</code> e já conta com<code>font-family</code> para essa essa fonte, bastando alterar essa variável. Caso algum elemento vá apresentar outra fonte, chamar o <code>font-family</code> normalmente e declare nova variável de fonte no <code>:root</code>.<br /><code>--fonte: 'Roboto', var(--sans)</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--tema",
        "tipo": "texto",
        "heranca": "sim",
        "uso": "variável usada no <code>:root</code> para indicar qual o tema de cores utilizado. Valor inicial: \"padrão\".<br /><code>--tema: \"alto contraste\"</code>",
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
]