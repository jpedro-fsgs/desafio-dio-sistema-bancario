from tkinter import Tk, Label, Button, Frame, simpledialog, messagebox, Entry, Listbox, Menu
import json

LIMITE = 500
LIMITE_SAQUES = 3

contas_correntes = []
dados_usuarios = []

def get_index(id, cpf):

    return_conta = {}
    return_usuario = {}
    index_conta = 0
    index_usuario = 0

    for i in contas_correntes:
        if i['id'] == id:
            return_conta = i
            index_conta = contas_correntes.index(i)
            break

    for i in dados_usuarios:
        if i['cpf'] == cpf:
            return_usuario = i
            index_usuario = dados_usuarios.index(i)
            break

    return return_conta, return_usuario, index_conta, index_usuario
        
 
def abrir_janela_conta(id, cpf):
    
    def sacar(conta_index):
    
        global contas_correntes
        
        if contas_correntes[conta_index]['numero_saques'] >= contas_correntes[conta_index]['LIMITE_SAQUE']:
            messagebox.showerror(title='Limite atingido', message='Você ultrapassou o limite de saques diários')
            return
        
        valor = simpledialog.askstring('Operação de saque', 'Digite o valor a ser sacado')
        if not valor: return
        
        try:
            valor = float(valor)
        except:
            messagebox.showerror(title='Erro', message='Digite um valor numérico!')
            return
        
        if valor <= 0:
            messagebox.showerror(title='Erro', message='Valor Inválido!')
            return
        
        if valor > contas_correntes[conta_index]['limite']:
            messagebox.showerror(title='Erro', message='Valor acima do limite')
            return
        
        if valor > contas_correntes[conta_index]['saldo']:
            messagebox.showerror(title='Erro', message='Saldo não suficiente')
            return
        
        contas_correntes[conta_index]['saldo'] -= valor
        contas_correntes[conta_index]['numero_saques'] += 1
        contas_correntes[conta_index]['extrato'] += f'Saque: -R$ {valor:.2f}\n'
        att_saldo()


    def depositar(conta_index):
        
        global contas_correntes
        
        valor = simpledialog.askstring('Operação de depósito', 'Digite o valor a ser depositado')
        if not valor: return

        try:
            valor = float(valor)
        except:
            messagebox.showerror(title='Erro', message='Digite um valor numérico!')
            return
        
        if valor <= 0:
            messagebox.showerror(title='Erro', message='Valor Inválido!')
            return
        
        contas_correntes[conta_index]['saldo'] += valor
        contas_correntes[conta_index]['extrato'] += f'Depósito: +R$ {valor:.2f}\n'
        att_saldo()
            

    def emitir_extrato(conta_index):
        
        global contas_correntes

        mensagem_extrato = f'Transações Bancárias da Conta {conta_index}: \n\n'
        if contas_correntes[conta_index]['extrato']: mensagem_extrato += contas_correntes[conta_index]['extrato']
        else: mensagem_extrato += 'Não há transações bancárias registradas'

        messagebox.showinfo(title=f'Extrato Conta {conta_index}', message=mensagem_extrato)

    def att_saldo():
        label_saldo['text'] = f'{nome}\n Conta: {index_conta}\nSaldo: R$ {contas_correntes[index_conta]['saldo']:.2f}'
    
    
    dados = get_index(id, cpf)
    nome = dados[1]['nome']
    index_conta = dados[2]

    
    
    janela_usuario = Tk()
    janela_usuario.title("Operações Financeiras")
    janela_usuario.geometry('300x180')
    janela_usuario.eval('tk::PlaceWindow . center')
    

    frame_saldo = Frame(janela_usuario)
    frame_saldo.pack(padx=50, pady=25)

    label_saldo = Label(frame_saldo, text=f'{nome}\n Conta: {index_conta}\nSaldo: R$ {contas_correntes[index_conta]['saldo']:.2f}')
    label_saldo.grid(row=0, column=0)

    frame_botoes = Frame(janela_usuario)
    frame_botoes.pack(pady=25)

    botao_depositar = Button(frame_botoes, text='Depositar', command=lambda: depositar(index_conta))
    botao_depositar.grid(row=0, column=0, padx=15)

    botao_sacar = Button(frame_botoes, text='Sacar', command=lambda: sacar(index_conta))
    botao_sacar.grid(row=0, column=1, padx=15)

    botao_extrato = Button(frame_botoes, text='Extrato', command=lambda: emitir_extrato(index_conta))
    botao_extrato.grid(row=0, column=2, padx=15)


    janela_usuario.mainloop()


def adicionar_usuario():
    
    global dados_usuarios
    def salvar_dados_usuario(nome, data_nascimento, cpf, endereco):
        
        if not (nome and data_nascimento and cpf and endereco):
            messagebox.showerror(title='Erro', message='Não pode haver campos vazios')
            return
        
        try:
            cpf = int(cpf)
        except:
            messagebox.showerror(title='Erro', message='Digite apenas os números do CPF')
            return
        
        if any([cpf == i['cpf'] for i in dados_usuarios]):
            messagebox.showerror(title='Erro', message='Este CPF já está cadastrado')
            return

        dados = dict()
        dados['nome'] = nome
        dados['data_nascimento'] = data_nascimento
        dados['cpf'] = cpf
        dados['endereco'] = endereco
        dados['contas'] = []
        
        dados_usuarios.append(dados)
        messagebox.showinfo(title='Usuário cadastrado', message=f'{dados['nome']} cadastrado(a) com sucesso!')

        janela_adicionar_usuario.destroy()



    janela_adicionar_usuario = Tk()
    janela_adicionar_usuario.title('Adicionar Usuário')
    janela_adicionar_usuario.eval('tk::PlaceWindow . center')

    label_titulo = Label(janela_adicionar_usuario, text='Insira os dados do usuário')
    label_titulo.pack(padx=15, pady=15)
    
    frame_dados = Frame(janela_adicionar_usuario)
    frame_dados.pack()

    label_nome = Label(frame_dados, text='Nome: ')
    entry_nome = Entry(frame_dados, width=31)
    label_nome.grid(row=0, column=0, padx=5, pady=5)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    label_data_nascimento = Label(frame_dados, text='Data de Nascimento: ')
    entry_data_nascimento = Entry(frame_dados, width=31)
    label_data_nascimento.grid(row=1, column=0, padx=5, pady=5)
    entry_data_nascimento.grid(row=1, column=1, padx=5, pady=5)

    label_cpf = Label(frame_dados, text='CPF: ')
    entry_cpf = Entry(frame_dados, width=31)
    label_cpf.grid(row=2, column=0, padx=5, pady=5)
    entry_cpf.grid(row=2, column=1, padx=5, pady=5)

    label_endereco = Label(frame_dados, text='Endereço: ')
    entry_endereco = Entry(frame_dados, width=31)
    label_endereco.grid(row=3, column=0, padx=5, pady=5)
    entry_endereco.grid(row=3, column=1, padx=5, pady=5)

    botao_confirmar = Button(janela_adicionar_usuario, text='Adicionar', command=lambda: salvar_dados_usuario(nome=entry_nome.get(), 
                                                                                                               data_nascimento=entry_data_nascimento.get(),
                                                                                                               cpf=entry_cpf.get(),
                                                                                                               endereco=entry_endereco.get()))
    botao_confirmar.pack(padx=15, pady=15)

    janela_adicionar_usuario.mainloop()


def selecionar_usuario():

    botoes_contas = []
    
    def update_botoes(index):
        
        ncontas = len(dados_usuarios[index]['contas'])
        if ncontas < 1: label_info_contas['text'] = f'Não há contas correntes registradas'
        elif ncontas == 1: label_info_contas['text'] = f'{ncontas} conta corrente registrada'
        else: label_info_contas['text'] = f'{ncontas} contas correntes registradas'
        
        for i in botoes_contas: i.destroy()
        botoes_contas.clear()
  
        for i in dados_usuarios[index]['contas']:
            botoes_contas.append(Button(frame_botoes, text=f'Conta: {i}', command=lambda x=i: abrir_janela_conta(x, dados_usuarios[index]['cpf'])))
            botoes_contas[-1].pack(side='left', padx=5)

        # for i in enumerate(botoes_contas):
        #     i['command'] = lambda: print(i)

        
        botao = Button(frame_botoes, text='Criar nova conta corrente', command=lambda:criar_conta(index))
        botoes_contas.append(botao)
        botao.pack(side='left', padx=5)
    
    def mostrar_info(event):
        
        index = lista_usuarios.curselection()[0]
        
        info = f'Nome: {dados_usuarios[index]['nome']}\n'
        info += f'Data de Nascimento: {dados_usuarios[index]['data_nascimento']}\n'
        info += f'CPF: {dados_usuarios[index]['cpf']}\n'
        info += f'Endereço: {dados_usuarios[index]['endereco']}\n'
        # info += f'Contas: {dados_usuarios[index]['contas']}'
        
        label_titulo['text'] = info

        label_info_contas.pack()

        update_botoes(index)
    

    def criar_conta(index):
        global LIMITE, LIMITE_SAQUES
        
        cpf = dados_usuarios[index]['cpf']
        for i in dados_usuarios:
            if i['cpf'] == cpf:
                id_conta = len(contas_correntes)
                contas_correntes.append({
                    'id': id_conta,
                    'cpf': i['cpf'],
                    'saldo': 0,
                    'limite': LIMITE,
                    'extrato': '',
                    'numero_saques': 0,
                    'LIMITE_SAQUE': LIMITE_SAQUES
    })
                i['contas'].append(id_conta)
                update_botoes(index)
                return
    
    janela_selecionar_usuario = Tk()
    janela_selecionar_usuario.title('Selecionar Usuário')
    janela_selecionar_usuario.geometry('600x250')
    janela_selecionar_usuario.eval('tk::PlaceWindow . center')

    frame_usuarios = Frame(janela_selecionar_usuario)
    frame_usuarios.grid(row=0, column=0, pady=25, padx=25)

    lista_usuarios = Listbox(frame_usuarios, width=31)
    lista_usuarios.pack()

    frame_info = Frame(janela_selecionar_usuario)
    frame_info.grid(row=0, column=1, pady=25, padx=25)

    label_titulo = Label(frame_info, text='Selecione o Usuário', justify='left')
    label_titulo.pack(side='top', padx=15, pady=15)

    label_info_contas = Label(frame_info, justify='left')

    frame_botoes = Frame(janela_selecionar_usuario)
    frame_botoes.grid(row=1, column=1)

   


    for i in dados_usuarios: lista_usuarios.insert('end', i['nome'])
    
    lista_usuarios.bind("<ButtonRelease-1>", mostrar_info)


def limpar_dados():
    global contas_correntes, dados_usuarios
    contas_correntes = []
    dados_usuarios = []


def set_limite_valor_saque():  
    global LIMITE
    valor = simpledialog.askstring('Limite do valor de saque', 'Digite o valor do limite de saque')
    if not valor: return

    try:
        valor = float(valor)
    except:
        messagebox.showerror(title='Erro', message='Digite um valor numérico!')
        return
    
    if valor <= 0:
        messagebox.showerror(title='Erro', message='Valor Inválido!')
        return
    
    LIMITE = valor


def set_limite_saques():  
    global LIMITE_SAQUES
    valor = simpledialog.askstring('Limite de saques', 'Digite a quantidade do limite de saques')
    
    if not valor: return


    try:
        valor = int(valor)
    except:
        messagebox.showerror(title='Erro', message='Digite um valor numérico inteiro!')
        return
    
    if valor <= 0:
        messagebox.showerror(title='Erro', message='Valor Inválido!')
        return
    
    LIMITE_SAQUES = valor


with open('desafio-dio-sistema-bancario/dados_usuarios.json', 'r') as dados_usuario_arquivo:
    dados_geral = json.load(dados_usuario_arquivo)

dados_usuarios = dados_geral["dados_usuarios"]
contas_correntes = dados_geral["contas_correntes"]

janela = Tk()
janela.title("Sistema Bancário")
janela.geometry('300x170')
janela.eval('tk::PlaceWindow . center')

menubar = Menu(janela)
configuracoes = Menu(menubar, tearoff=0)

configuracoes.add_command(label='Limpar todos os dados', command=limpar_dados)
configuracoes.add_command(label='Mudar limite do valor de saque', command=set_limite_valor_saque)
configuracoes.add_command(label='Mudar limite de saques', command=set_limite_saques)

menubar.add_cascade(label='Configurações', menu=configuracoes)

janela.config(menu=menubar)

botao_selecionar = Button(janela, text='Selecionar usuário', command=selecionar_usuario)
botao_selecionar.pack(pady=25)

botao_adicionar = Button(janela, text='Adicionar usuário', command=adicionar_usuario)
botao_adicionar.pack(pady=25)
janela.mainloop()

with open('desafio-dio-sistema-bancario/dados_usuarios.json', 'w') as dados_usuario_arquivo:
    dados_geral = json.dump({"dados_usuarios": dados_usuarios, "contas_correntes": contas_correntes}, dados_usuario_arquivo, indent=4)
