from xmlrpc.server import SimpleXMLRPCServer
import sqlite3

server = SimpleXMLRPCServer(('localhost', 3000), logRequests=True, allow_none=True)
conn = sqlite3.connect('repositorio.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS alunos (
                    matricula integer primary key unique,
                    nome text
                    )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS notas (
                id integer primary key AUTOINCREMENT,
                cod_disciplina integer,
                valor integer NOT NULL,
                matricula_ID REFERENCES alunos(matricula)
                )""")

conn.commit()

"""Servico cadastrar_aluno, permite cadastrar um novo aluno no sistema
    Parametros: {
            nome: nome do aluno, composto por palavras
            matricula: matricula do aluno, composto por 6 digitos numericos
        }
    Retorno: Mensagem de confirmacao do cadastro 
    """
def cadastrar_aluno(parametros):
    parametros['matricula'] = int(parametros['matricula'])
    with conn:
            try:
                cursor.execute("INSERT INTO alunos VALUES (:matricula, :nome)", {'matricula': parametros['matricula'], 'nome': parametros['nome']})
                conn.commit()

            except:
                return 'Já existe um aluno com a matrícula inserida'

    return 'Aluno cadastrado !'

"""Servico consultar_alunos, permite consultar quais alunos estao cadastrados no sistema
    Parametros: Nao ha
    Retorno: Retorna um data frame com todos os alunos cadastrados no sistema, composto por {
        nome: nome do aluno cadastrado,
        matricula: matricula do aluno, composto por 6 digitos numericos
    }
    """
def consultar_alunos():
    cursor.execute("SELECT * FROM alunos")
    conn.commit()
    
    alunos = cursor.fetchall()

    if(alunos):
        return alunos
    else:
        return 'Não há alunos cadastrados' 
    

"""Servico cadastrar_nota, permite cadastrar uma nota de uma disciplina para um aluno
    Parametros: {
        matricula: matricula do aluno, composto por 6 digitos numericos
        cod_disciplina: codigo da disciplina, formato livre alfanumerico
        valor: valor da nota, podendo ser um numero decimal entre 0 e 10
    }
    Retorno: Mensagem de confirmacao sobre o cadastro da nota
    """
def cadastrar_nota(parametros):
    with conn:
        cursor.execute("""
                        SELECT * 
                        FROM alunos 
                        WHERE matricula=:matricula""", {
                            'matricula': parametros['matricula']
                            })
        conn.commit()

        if(not cursor.fetchall()):
            return 'Aluno não cadastrado'

        cursor.execute("""
                        SELECT * 
                        FROM notas 
                        WHERE matricula_ID=:matricula 
                        AND cod_disciplina=:disciplina""", {
                        'matricula': parametros['matricula'], 
                        'disciplina': parametros['cod_disciplina']
                        })
        conn.commit()

        registro = cursor.fetchone()
        
        if(registro):
            cursor.execute("""
                            UPDATE notas
                            SET valor=:valor
                            WHERE id=:id""", {
                                'valor': parametros['valor'],
                                'id':registro[0]
                            })
            conn.commit()
            return 'Nota alterada com sucesso !'

        else:
            cursor.execute("""INSERT INTO notas VALUES (:id, :cod_disciplina, :valor, :matricula_ID)""", {
                            'id': None,
                            'cod_disciplina': parametros['cod_disciplina'],
                            'valor': parametros['valor'],
                            'matricula_ID': parametros['matricula']
                            })
            conn.commit()
            return 'Nota Cadastrada com sucesso !'

"""Servico consultar_nota, permite consultar uma nota de uma disciplina para um aluno
    Parametros: {
        matricula: matricula do aluno, composto por 6 digitos numericos
        cod_disciplina: codigo da disciplina, formato livre alfanumerico
    }
    Retorno: {
        valor: valor da nota, podendo ser um numero decimal entre 0 e 10
    }
    """
def consultar_nota(parametros):
    with conn:

        cursor.execute("""
                        SELECT * 
                        FROM alunos 
                        WHERE matricula=:matricula""", {
                            'matricula': parametros['matricula']
                            })
        conn.commit()

        if(not cursor.fetchall()):
            return 'Aluno não cadastrado'

        cursor.execute("""
                        SELECT * 
                        FROM notas 
                        WHERE cod_disciplina=:disciplina
                        AND matricula_ID=:matricula""", {
                            'disciplina': parametros['cod_disciplina'],
                            'matricula': parametros['matricula']
                            })
        conn.commit()
        registro = cursor.fetchone()

        if(registro):
            return 'A nota do aluno para a disciplina {} é {}'.format(parametros['cod_disciplina'],registro[2])
        else:
            return 'O aluno não possui nota para a disciplina {}'.format(parametros['cod_disciplina'])

"""Servico consultar_notas, permite consultar todas as notas de um aluno
    Parametros: {
        matricula: matricula do aluno, composto por 6 digitos numericos
    }
    Retorno: um dataframe composto por {
        cod_disciplina: codigo da disciplina, formato livre alfanumerico
        valor: valor da nota, podendo ser um numero decimal entre 0 e 10
    }
    """
def consultar_notas(parametros):
    with conn:
        cursor.execute("""
                        SELECT * 
                        FROM notas 
                        WHERE matricula_ID=:matricula""", {
                            'matricula': parametros['matricula']})
        conn.commit()

        registro = cursor.fetchall()
        
        if(registro):
            return registro
        else:
            return False


"""Servico consultar_CR, permite consultar o CR do aluno para suas disciplinas
    Parametros: {
        matricula: matricula do aluno, composto por 6 digitos numericos
    }
    Retorno: O CR do aluno
    """
def consultar_CR(parametros):
    with conn:
        cursor.execute("""
                        SELECT * 
                        FROM alunos 
                        WHERE matricula=:matricula""", {
                            'matricula': parametros['matricula']
                            })
        conn.commit()

        if(not cursor.fetchall()):
            return 'Aluno não cadastrado'

        cursor.execute("""
                        SELECT (SUM(valor)/COUNT(*)) as media 
                        FROM notas 
                        WHERE matricula_ID=:matricula""", {
                            'matricula': parametros['matricula']})

        conn.commit()
        CR_tuple = cursor.fetchone()

        if(CR_tuple[0] == None):
            return 'O aluno não possui notas para cálculo de CR'
        else:
            return 'A média do aluno para as disciplinas é {:.2f}'.format(CR_tuple[0])
    
server.register_function(cadastrar_aluno)
server.register_function(consultar_alunos)
server.register_function(cadastrar_nota)
server.register_function(consultar_nota)
server.register_function(consultar_notas)
server.register_function(consultar_CR)

if __name__ == '__main__':
    try:
        print('Serving...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')

conn.close()