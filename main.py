from flask import Flask, request, jsonify, render_template
from database import consultar

app = Flask(__name__)

validacao = {
    'manchete': lambda x: type(x) == str,
    'descricao': lambda x: type(x) == str,
    'idImagem': lambda x: type(x) == int and consultar('SELECT 1 FROM imagens WHERE id = %s', (x,)),
    'corpo': lambda x: type(x) == str,
    'autores': lambda x: type(x) == list and all([type(a) == int and consultar('SELECT 1 FROM autores WHERE id = %s;', (a,)) for a in x])
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/noticias', methods=['GET'])
def noticias():
    return render_template('index.html')

@app.route('/autores', methods=['GET'])
def autores():
    return render_template('index.html')

@app.route('/imagens', methods=['GET'])
def imagens():
    return render_template('index.html')


@app.route('/cadastrar-imagem', methods=['POST'])
def cadastrar_imagem():
    if not 'imagem' in request.files:
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: imagem.'})
    
    consultar('INSERT INTO imagens VALUES (DEFAULT, %s);', (request.files['imagem'].read(),))
    
    id = consultar('SELECT MAX(id) FROM imagens;')[0]['MAX(id)']

    return jsonify({'status': True, 'mensagem': f'Imagem com identificador "{id}" cadastrada com sucesso.', 'id': id})

@app.route('/deletar-imagem', methods=['POST'])
def deletar_imagem():
    dados = request.get_json()

    if not ('idImagem' in dados):
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idImagem.'})
    if dados['idImagem'] != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('DELETE FROM imagens WHERE id = %s', (dados['idImagem'],))

    return jsonify({'status': True, 'mensagem': f'Imagem com identificador {dados["idImagem"]} deletada com sucesso.'})

@app.route('/cadastrar-autor', methods=['POST'])
def cadastrar_autor():
    dados = request.get_json()

    if not 'autor' in dados:
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: autor.'})
    if type(dados['autor']) != str:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})
    
    consultar('INSERT INTO autores VALUES (DEFAULT, %s);', (dados['autor'],))

    id = consultar('SELECT MAX(id) FROM autores;')[0]['MAX(id)']

    return jsonify({'status': True, 'mensagem': f'Autor {dados["autor"]} com identificador "{id}" cadastrado com sucesso.', 'id': id})

@app.route('/atualizar-autor', methods=['POST'])
def atualizar_autor():
    dados = request.get_json()

    for a in ['idAutor', 'nome']:
        if a not in dados:
            return jsonify({'status': False, 'mensagem': f'Parâmetro obrigatório não informado: {a}.'})
    
    if (type(dados['idAutor']) != int) or (type(dados['nome']) != str):
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})
    
    consultar('UPDATE autores SET nome = %s WHERE id = %s;', (dados['nome'], dados['idAutor']))

    return jsonify({'status': True, 'mensagem': f'Autor com identificador {dados["idAutor"]} atualizado com sucesso.'})

@app.route('/deletar-autor', methods=['POST'])
def deletar_autor():
    dados = request.get_json()

    if not ('idAutor' in dados):
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idAutor.'})
    if dados['idAutor'] != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('DELETE FROM autores WHERE id = %s;', (dados['idAutor'],))

    return jsonify({'status': True, 'mensagem': f'Autor com identificador {dados["idAutor"]} deletado com sucesso.'})

@app.route('/cadastrar-noticia', methods=['POST'])
def cadastrar_noticia():
    dados = request.get_json()

    for i in validacao:
        if i not in dados:
            return jsonify({'status': False, 'mensagem': f'Parâmetro obrigatório não informado: {i}.'})
        if not validacao[i](dados[i]):
            return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('INSERT INTO noticias VALUES (DEFAULT, %s, %s, %s, CURRENT_TIMESTAMP(), NULL, %s);', (dados['manchete'], dados['descricao'], dados['idImagem'], dados['corpo']))

    for autor in dados['autores']:
        consultar('INSERT IGNORE INTO noticias_autores VALUES ((SELECT MAX(id) FROM noticias), %s);', (autor))

    return jsonify({'status': True, 'mensagem': f'Notícia "{dados["manchete"]}" cadastrada com sucesso.'})

@app.route('/atualizar-noticia', methods=['POST'])
def atualizar_noticia():
    dados = request.get_json()

    if not dados['idNoticia']:
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idNoticia.'})
    if type(dados['idNoticia']) != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})
    
    if not any([a in dados for a in validacao]):
        return jsonify({'status': False, 'mensagem': 'Deve ser informado ao menos um dado a ser atualizado.'})
    
    for a in dados:
        if a == 'idNoticia':
            if type(a) != str:
                return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})
        if a in validacao:
            if not validacao[a](dados[a]):
                return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})
            consultar('UPDATE noticias SET %s = %s WHERE id = %s', (a, dados[a], dados['idNoticia']))

    return jsonify({'status': True, 'mensagem': f'Notícia com identificador {dados["idNoticia"]} atualizada com sucesso.'})

@app.route('/deletar-noticia', methods=['POST'])
def deletar_noticia():
    dados = request.get_json()

    if not ('idNoticia' in dados):
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idNoticia.'})
    if dados['idNoticia'] != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('DELETE FROM noticias WHERE id = %s;', (dados['idNoticia'],))

    return jsonify({'status': True, 'mensagem': f'Notícia com identificador {dados["idNoticia"]} deletada com sucesso.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)