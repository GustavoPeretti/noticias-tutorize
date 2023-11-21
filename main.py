from flask import Flask, request, jsonify, render_template
from database import consultar
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

host = 'smtp.gmail.com'
port = '587'
login = 'tutorizeoficial@gmail.com'
pword = 'xkwb jtzk crce wcve'

app = Flask(__name__)

validacao = {
    'manchete': lambda x: type(x) == str,
    'descricao': lambda x: type(x) == str,
    'idImagem': lambda x: type(x) == int and consultar('SELECT 1 FROM imagens WHERE id = %s;', (x,)),
    'corpo': lambda x: type(x) == str,
    'autores': lambda x: type(x) == list and all([type(a) == int and consultar('SELECT 1 FROM autores WHERE id = %s;', (a,)) for a in x])
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/noticias', methods=['GET'])
def noticias():
    noticias = consultar('SELECT noticias.*, imagens.imagem, GROUP_CONCAT(autores.id SEPARATOR ", ") AS id_autores, GROUP_CONCAT(autores.nome SEPARATOR ", ") AS nome_autores FROM imagens INNER JOIN noticias INNER JOIN noticias_autores INNER JOIN autores ON imagens.id = noticias.id_imagem AND noticias_autores.id_autor = autores.id AND noticias_autores.id_noticia = noticias.id GROUP BY noticias.id;')
    noticias = [{'id': n['id'], 'manchete': n['manchete'], 'descricao': n['descricao'], 'id_imagem': n['id_imagem'], 'data_publicacao': n['data_publicacao'], 'data_atualizacao': n['data_atualizacao'], 'corpo': n['corpo'], 'imagem': str(base64.b64encode(n['imagem']))[2:-1], 'id_autores': n['id_autores'], 'nome_autores': n['nome_autores']} for n in noticias]
    return render_template('noticias.html', noticias=noticias)

@app.route('/noticias/<int:idnoticia>', methods=['GET'])
def pagina_noticia(idnoticia):
    noticia = consultar('SELECT noticias.*, imagens.imagem, GROUP_CONCAT(autores.id SEPARATOR ", ") AS id_autores, GROUP_CONCAT(autores.nome SEPARATOR ", ") AS nome_autores FROM imagens INNER JOIN noticias INNER JOIN noticias_autores INNER JOIN autores ON imagens.id = noticias.id_imagem AND noticias_autores.id_autor = autores.id AND noticias_autores.id_noticia = noticias.id GROUP BY noticias.id HAVING noticias.id = %s;', idnoticia)
    noticia = [{'id': n['id'], 'manchete': n['manchete'], 'descricao': n['descricao'], 'id_imagem': n['id_imagem'], 'data_publicacao': n['data_publicacao'], 'data_atualizacao': n['data_atualizacao'], 'corpo': n['corpo'], 'imagem': str(base64.b64encode(n['imagem']))[2:-1], 'id_autores': n['id_autores'], 'nome_autores': n['nome_autores']} for n in noticia]
    return render_template('editar-noticia.html', noticia=noticia, autores=consultar('SELECT * FROM autores;'), imagens=consultar('SELECT * FROM imagens;'))

@app.route('/noticias/nova', methods=['GET'])
def nova_noticia():
    return render_template('cadastrar-noticia.html', autores=consultar('SELECT * FROM autores;'), imagens=consultar('SELECT * FROM imagens;'))

@app.route('/autores', methods=['GET'])
def autores():
    return render_template('autores.html', autores=consultar('SELECT * FROM autores;'))

@app.route('/autores/<int:idautor>', methods=['GET'])
def pagina_autor(idautor):
    return render_template('editar-autor.html', autor=consultar('SELECT * FROM autores WHERE id = %s;', (idautor,)))

@app.route('/autores/novo', methods=['GET'])
def novo_autor():
    return render_template('cadastrar-autor.html')

@app.route('/imagens', methods=['GET'])
def imagens():
    print(consultar('SELECT * FROM imagens;'))
    return render_template('imagens.html', imagens=[{'id': i['id'], 'imagem': str(base64.b64encode(i['imagem']))[2:-1]} for i in consultar('SELECT * FROM imagens;')])

@app.route('/blob-imagem', methods=['POST'])
def blob_imagem():
    dados = request.get_json()

    if not ('idImagem' in dados):
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idImagem.'})
    if type(dados['idImagem']) != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    imagem = consultar('SELECT imagem FROM imagens WHERE id = %s', (dados['idImagem'],))[0]['imagem']
    imagem = str(base64.b64encode(imagem))[2:-1]

    return jsonify({'status': True, 'mensagem': f'Imagem "{dados["idImagem"]}" retornada com sucesso.', 'blob': imagem})

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
    if type(dados['idImagem']) != int:
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

    print(dados)

    if not ('idAutor' in dados):
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idAutor.'})
    if type(dados['idAutor']) != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('DELETE FROM autores WHERE id = %s;', (dados['idAutor'],))

    return jsonify({'status': True, 'mensagem': f'Autor com identificador "{dados["idAutor"]}" deletado com sucesso.'})

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

    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.login(login, pword)

    for p in consultar('SELECT * FROM newsletter;'):
        msg = MIMEMultipart()
        msg['From'] = login
        msg['Subject'] = dados['manchete']
        msg.attach(MIMEText(f'<h1 style="text-align=\'center\'">{dados["manchete"]}</h1><br><p>Olá, {p["nome"]}!</p><br><p>Notificamos a publicação da notícia <a href="http://localhost/noticias/">{dados["manchete"]}</a></p><br><p>{dados["descricao"]}</p><br><a href="http://localhost/remover-cadastro?token={p["token"]}">Cancelar notificações</a>', 'html'))
        msg['To'] = p['email']
        server.sendmail(msg['From'], msg['To'], msg.as_string())

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
            if a != 'autores':
                consultar(f'UPDATE noticias SET {"id_imagem" if a == "idImagem" else a} = %s WHERE id = %s;', (dados[a], dados['idNoticia']))

    return jsonify({'status': True, 'mensagem': f'Notícia com identificador {dados["idNoticia"]} atualizada com sucesso.'})

@app.route('/deletar-noticia', methods=['POST'])
def deletar_noticia():
    dados = request.get_json()

    if not ('idNoticia' in dados):
        return jsonify({'status': False, 'mensagem': 'Parâmetro obrigatório não informado: idNoticia.'})
    if type(dados['idNoticia']) != int:
        return jsonify({'status': False, 'mensagem': 'Os dados foram recebidos em formato inválido.'})

    consultar('DELETE FROM noticias WHERE id = %s;', (dados['idNoticia'],))

    return jsonify({'status': True, 'mensagem': f'Notícia com identificador {dados["idNoticia"]} deletada com sucesso.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)