from xmlrpc.client import ServerProxy
import re
from tabulate import tabulate

proxy = ServerProxy('http://localhost:3000')

regex = {
    'nome': r'^[A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]+$',
    'matricula': r'\b\d{6}\b'
}

if __name__ == '__main__':
    operation = input('Selecione a operação a ser realizada: \n 1. Cadastrar aluno \n ' + 
                '2. Consultar alunos cadastrados \n 3. Cadastrar Nota do aluno\n 4. Consultar Nota do aluno\n' +
                ' 5. Consultar Notas do aluno \n 6. Consultar CR do aluno\n')
    if(re.match('[1-6]',operation)):
        operation = int(operation)
    else:
        print('Opção inválida')

    
    if operation == 1:
        parametros = {
            'nome': input('Nome do aluno: '),
            'matricula': input('Insira a matricula do aluno: ')
        }
        if(re.match(regex['nome'], parametros['nome'])):
            if(re.match(regex['matricula'], parametros['matricula'])):
                print(proxy.cadastrar_aluno(parametros))

            else:
                print('Matrícula inválida. Digite um valor numérico no padrao DDDDDD, exemplo: 202101')
        else:
            print('Nome inválido. São aceitos nomes compostos por letras, espaços e acentos')

    if operation == 2:
        alunos_tuple = proxy.consultar_alunos()

        if(alunos_tuple):
            tabela = []
            for aluno in alunos_tuple:
                tabela.append([aluno[0], aluno[1]])

            print(tabulate(tabela, headers=['matricula', 'nome']))

        
    if operation == 3:
        parametros = {
            'matricula':input('Insira a matricula do aluno: '),
            'cod_disciplina': input('Insira o código da disciplina: '),
            'valor': input('Insira a nota da disciplina: ')
        }
        parametros['valor'] = parametros['valor'].replace(',','.')

        if(re.match(regex['matricula'], parametros['matricula'])):
            try:
                parametros['valor'] = float(parametros['valor'])

            except ValueError:
                print('A nota deve ser um valor numérico inteiro ou decimal entre 0 e 10')
                exit()
                
            except TypeError:
                print('A nota deve ser um valor numérico inteiro ou decimal entre 0 e 10')   
                exit()   
        
        else:
            print('Matrícula inválida. Digite um valor numérico no padrao DDDDDD, exemplo: 202101')
            exit()
        
        if parametros['valor'] > 0 and parametros['valor'] < 10:
            print(proxy.cadastrar_nota(parametros))
        
        else:
            print("A nota deve estar entre 0 e 10")

    if operation == 4:
        parametros = {
            'matricula':input('Insira a matricula do aluno: '),
            'cod_disciplina': input('Insira o código da disciplina: ')
        }
        if(re.match(regex['matricula'], parametros['matricula'])):
            print(proxy.consultar_nota(parametros))
        
        else:
            print('Matrícula inválida. Digite um valor numérico no padrao DDDDDD, exemplo: 202101')
        

    if operation == 5:
        parametros = {
            'matricula': input('Insira a matricula do aluno: ')
        } 
        if(re.match(regex['matricula'], parametros['matricula'])):
            notas_tuple = proxy.consultar_notas(parametros)
            
            if(notas_tuple):
                tabela = []
                for nota in notas_tuple:
                    tabela.append([nota[1], nota[2]])

                print(tabulate(tabela, headers=['cod_disciplina', 'nota']))
            else:
                print('O aluno não possui notas')
                exit()
        
        else:
            print('Matrícula inválida. Digite um valor numérico no padrao DDDDDD, exemplo: 202101')
            

    if operation == 6:
        parametros = {
            'matricula':input('Insira a matricula do aluno: ')
        }
        if(re.match(regex['matricula'], parametros['matricula'])):
            print(proxy.consultar_CR(parametros))
 
        else:
            print('Matrícula inválida. Digite um valor numérico no padrao DDDDDD, exemplo: 202101')