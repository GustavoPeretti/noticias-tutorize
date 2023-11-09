import pymysql
import dotenv

env = dotenv.dotenv_values()

def consultar(instrucao, argumentos=[]):
    with pymysql.connect(
        host=env['BD_HOST'],
        user=env['BD_USER'],
        password=env['BD_PASSWORD'],
        database=env['BD_DATABASE'],
        port=int(env['BD_PORT']),
        cursorclass=pymysql.cursors.DictCursor
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(instrucao, argumentos)
            resultado = cursor.fetchall()
            conexao.commit()
            return resultado
            