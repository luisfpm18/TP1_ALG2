import os
import time
import math
from flask import Flask, render_template, request, url_for
from Indexador import Indexador
from Recuperador import Recuperador

PASTA_BBC = 'bbc'
ARQUIVO_INDICE = 'indice_salvo.txt'
RESULTADOS_POR_PAGINA = 10

app = Flask(__name__,
            template_folder='../front',
            static_folder='../front')

print("Iniciando servidor...")

indexador_global = Indexador(PASTA_BBC)

if os.path.exists(ARQUIVO_INDICE):
    indexador_global.carregar_indice(ARQUIVO_INDICE)
else:
    indexador_global.criar_indice()
    indexador_global.salvar_indice(ARQUIVO_INDICE)

recuperador_global = Recuperador(indexador_global)
print("Servidor pronto para receber consultas.")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search')
def search():
    consulta_usuario = request.args.get('consulta_usuario', '')
    pagina = int(request.args.get('pagina', 1))

    if not consulta_usuario:
        return render_template('index.html')

    start_time = time.time()
    resultados_completos = recuperador_global.buscar(consulta_usuario)
    duracao = time.time() - start_time

    total_resultados = len(resultados_completos)
    maxima_pagina = math.ceil(total_resultados / RESULTADOS_POR_PAGINA)

    indice_inicio = (pagina - 1) * RESULTADOS_POR_PAGINA
    indice_fim = indice_inicio + RESULTADOS_POR_PAGINA

    resultados_paginados = resultados_completos[indice_inicio:indice_fim]

    estatisticas = {
        "total": total_resultados,
        "duracao": duracao,
        "pagina": pagina,
        "maxima_pagina": maxima_pagina,
        "consulta_usuario": consulta_usuario
    }

    return render_template(
        'index.html',
        resultados=resultados_paginados,
        estatisticas=estatisticas,
        consulta_usuario=consulta_usuario
    )


@app.route('/documento/<int:doc_id>')
def ver_documento(doc_id):
    caminho_arquivo = indexador_global.id_doc_mapa.get(doc_id)

    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        return "Documento não encontrado", 404

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        conteudo = f"Erro ao ler o arquivo: {e}"

    titulo = "/".join(caminho_arquivo.split(os.path.sep)[-2:])
    return render_template('documento.html', titulo=titulo, conteudo=conteudo)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)