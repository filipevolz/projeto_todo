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























'''

# --- BATERIA DE TESTES COMPLETA DO CRUD ---

print("=== 1. CRIANDO TAREFAS ===")
criar_tarefa("Estudar Python", "Aprender lógica de dicionários e listas")
criar_tarefa("Treinar Git", "Fazer commit e push do projeto TO-DO")

print("\n=== 2. OBTER TODAS AS TAREFAS (GET /todo) ===")
print(obter_tarefas())

print("\n=== 3. OBTER TAREFA POR ID (GET /todo/:id) ===")
print("Busca ID 1:", obter_tarefa_por_id(1))
print("Busca ID 99:", obter_tarefa_por_id(99))

print("\n=== 4. ATUALIZAR TAREFA (PUT /todo/:id) ===")
print(atualizar_tarefa(1, "Estudar Python e FastAPI", "Concluir a lógica CRUD no main.py"))

print("\n=== 5. ALTERAR STATUS (PATCH /todo/:id) ===")
print(alterar_status_tarefa(1, "concluído"))

print("\n=== 6. DELETAR TAREFA (DELETE /todo/:id) ===")
print(deletar_tarefa(1))

print("\n=== 7. LISTA FINAL APÓS REMOÇÃO ===")
print(obter_tarefas())

'''