from flask import Flask, request, jsonify
from database import consultar
import re

app = Flask(__name__)

validacao = {
    'manchete': lambda x: type(x) == str,
    'descricao': lambda x: type(x) == str,
    'corpo': lambda x: type(x) == str,
    'autores': lambda x: type(x) == list and all([type(a) == int for a in x])
}

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.get_json()

    for i in validacao:
        if i not in dados:
            return jsonify({'erro': f'Parâmetro obrigatório não informado: {i}.'})
        if not validacao[i](dados[i]):
            return jsonify({'erro': 'Os dados foram recebidos em formato inválido.'})
    
    consultar('INSERT INTO noticias VALUES (DEFAULT, %s, %s, CUR(), NULL, %s);', [dados[i] for i in ('manchete', 'descricao', 'corpo')])
    consultar

    return jsonify({'sucesso': f'Notícia "{dados["manchete"]}" cadastrada com sucesso.'})

@app.route('/atualizar', methods=['POST'])
def atualizar():
    dados = request.get_json()
    if not dados['idNoticia']:
        return jsonify({'erro': 'Parâmetro obrigatório não informado: idNoticia.'})
    if not any([a in dados for a in validacao]):
        return jsonify({'erro': 'Deve ser informado ao menos a ser atualizado.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)