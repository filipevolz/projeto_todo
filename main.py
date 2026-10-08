from datetime import datetime

# Projeto TO-DO

lista_de_tarefas = []
proximo_id = 1

def criar_tarefa(title, description):
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    global proximo_id

    nova_tarefa = {
        "id": proximo_id,
        "title": title,
        "description": description,
        "status": "pendente",
        "created_at": data_atual,
        "updated_at": data_atual
    }

    lista_de_tarefas.append(nova_tarefa)
    proximo_id += 1
    return nova_tarefa

def obter_tarefas():
    return lista_de_tarefas


def obter_tarefa_por_id(id):
    for tarefa in lista_de_tarefas:
        if tarefa["id"] == id:
            return tarefa
     
    return f'O ID {id} não foi encontrado'

def atualizar_tarefa(id, title, description):
    for tarefa in lista_de_tarefas:
        if tarefa["id"] == id:
            tarefa["title"] = title
            tarefa["description"] = description
            tarefa["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return tarefa

    return f'O ID {id} não foi encontrado'

def alterar_status_tarefa(id, novo_status):
    for tarefa in lista_de_tarefas:
        if tarefa["id"] == id:
            tarefa["status"] = novo_status
            tarefa["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return tarefa

    return f'O ID {id} não foi encontrado'

def deletar_tarefa(id):
    for tarefa in lista_de_tarefas:
        if tarefa["id"] == id:
            lista_de_tarefas.remove(tarefa)
            return f'A tarefa {tarefa["title"]} foi removida com sucesso!'
        
    return f'O ID {id} não foi encontrado'


while True:
    print('1 - CRIAR TAREFA')
    print('2 - LISTAR TAREFA')
    print('3 - BUSCAR TAREFA')
    print('4 - ATUALIZAR TAREFA')
    print('5 - ALTERAR STATUS')
    print('6 - DELETAR TAREFA')
    print('7 - SAIR')

    opcao = int(input('Escolha uma opção: '))

    if opcao == 1:
        titulo = input('Digite o título da tarefa: ')
        descricao = input('Digite a descrição da tarefa: ')

        tarefa_criada = criar_tarefa(titulo, descricao)
        print(f'A tarefa {titulo} foi criada com sucesso!')


    elif opcao == 2:
        tarefas = obter_tarefas()
        print(tarefas)

    elif opcao == 3:
        id_busca = int(input('Digite o ID da tarefa: '))
        resultado = obter_tarefa_por_id(id_busca)
        print(resultado)

    elif opcao == 4:
        id_atualizar = int(input('Digite o ID da tarefa: '))
        novo_titulo = input('Digite o novo título: ')
        nova_descricao = input('Digite a nova descrição: ')
        print(atualizar_tarefa(id_atualizar, novo_titulo, nova_descricao))

    elif opcao == 5:
        id_status = int(input('Digite o ID da tarefa: '))
        novo_status = input('Digite o novo status: ')
        print(alterar_status_tarefa(id_status, novo_status))

    elif opcao == 6:
        id_deletar = int(input('Digite o ID da tarefa: '))
        print(deletar_tarefa(id_deletar))

    elif opcao == 7:
        print('Saindo do sistema...')
        break