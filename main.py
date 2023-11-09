from flask import Flask, request, jsonify
from database import consultar

app = Flask(__name__)

validacao = {
    'manchete': lambda x: type(x) == str,
    'descricao': lambda x: type(x) == str,
    'idImagem': lambda x: type(x) == int and consultar('SELECT 1 FROM imagens WHERE id = %s', (x,)),
    'corpo': lambda x: type(x) == str,
    'autores': lambda x: type(x) == list and all([type(a) == str for a in x])
}

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    dados = request.get_json()

    for i in validacao:
        if i not in dados:
            return jsonify({'status': False, 'mensagem': f'Parâmetro obrigatório não informado: {i}.'})
        if not validacao[i](dados[i]):
            return jsonify({'status': 'erro', 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('INSERT INTO noticias VALUES (DEFAULT, %s, %s, %s, CURRENT_TIMESTAMP(), NULL, %s);', (dados['manchete'], dados['descricao'], dados['idImagem'], dados['corpo']))

    for autor in dados['autores']:
        consultar('INSERT IGNORE INTO autores VALUES (%s);', (autor))
        consultar('INSERT IGNORE INTO noticias_autores VALUES ((SELECT LAST_INSERT_ID() FROM noticias), %s);', (autor))

    return jsonify({'status': True, 'mensagem': f'Notícia "{dados["manchete"]}" cadastrada com sucesso.'})

@app.route('/cadastrar-imagem', methods=['POST'])
def cadastrar_imagem():
    if not 'imagem' in request.files:
        return jsonify({'status': 'erro', 'mensagem': 'Parâmetro obrigatório não informado: imagem.'})
    
    consultar('INSERT INTO imagens VALUES (DEFAULT, %s);', (request.files['imagem'].read(),))
    
    id = consultar('SELECT MAX(id) FROM imagens;')[0]['MAX(id)']

    return jsonify({'status': True, 'mensagem': f'Imagem com identificador "{id}" cadastrada com sucesso.', 'id': id})

# @app.route('/atualizar', methods=['POST'])
# def atualizar():
#     dados = request.get_json()
#     if not dados['idNoticia']:
#         return jsonify({'erro': 'Parâmetro obrigatório não informado: idNoticia.'})
#     if not any([a in dados for a in validacao]):
#         return jsonify({'erro': 'Deve ser informado ao menos a ser atualizado.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)