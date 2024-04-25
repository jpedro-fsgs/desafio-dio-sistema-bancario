from tkinter import Tk, Label, Button, Frame, simpledialog, messagebox, Entry, Listbox, Menu
import pickle
from sistema_bancario_v3 import *

class Banco:
    def __init__(self, nome_banco) -> None:
        self.nome_banco = nome_banco 
        self.clientes = []
        self.contas = []
        self.houve_alteracao = False

    def add_cliente(self, endereco, cpf, nome, data_nascimento):
        self.clientes.append(PessoaFisica(endereco, cpf, nome, data_nascimento))
        self.houve_alteracao = True
        return True

    def add_conta(self, cliente, saldo=0):
        id_conta = len(self.contas) + 1
        nova_conta = ContaCorrente(cliente, id_conta, saldo)
        self.contas.append(nova_conta)
        cliente.adicionar_conta(nova_conta)
        self.houve_alteracao = True
        return True

class InterfaceBanco(Tk):
    def __init__(self, banco, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.banco = banco
        
        self.title(banco.nome_banco)
        self.geometry('300x170')
        self.eval('tk::PlaceWindow . center')

        self.botoes_contas = []

        menubar = Menu(self)
        configuracoes = Menu(menubar, tearoff=0)

        configuracoes.add_command(label='Limpar todos os dados', command=self.limpar_dados)

        menubar.add_cascade(label='Configurações', menu=configuracoes)

        self.config(menu=menubar)        
        
        botao_selecionar = Button(self, text='Selecionar usuário', command=self.selecionar_usuario)
        botao_selecionar.pack(pady=25)

        botao_adicionar = Button(self, text='Adicionar usuário', command=self.adicionar_usuario)
        botao_adicionar.pack(pady=25)
        self.mainloop()
        
    def limpar_dados(self):
        confirm = messagebox.showwarning(title='Atenção', message='Esta ação irá deletar o banco e todos os dados de clientes e contas. Deseja continuar?', type='okcancel') 
        if confirm == 'ok':
            self.banco = Banco(simpledialog.askstring('Novo Banco', 'Digite o novo nome do Banco'))
            self.title(self.banco.nome_banco)
            self.banco.houve_alteracao = True

    
    def salvar_dados_usuario(self, janela, nome, data_nascimento, cpf, endereco):      
            if not (nome and data_nascimento and cpf and endereco):
                messagebox.showerror(title='Erro', message='Não pode haver campos vazios')
                return
            
            try:
                cpf = int(cpf)
            except:
                messagebox.showerror(title='Erro', message='Digite apenas os números do CPF')
                return
            
            if any([cpf == i.cpf for i in self.banco.clientes]):
                messagebox.showerror(title='Erro', message='Este CPF já está cadastrado')
                return

            self.banco.add_cliente(endereco, cpf, nome, data_nascimento)
            messagebox.showinfo(title='Usuário cadastrado', message=f'{nome} cadastrado(a) com sucesso!')

            janela.destroy()
    
    def adicionar_usuario(self):
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

        botao_confirmar = Button(janela_adicionar_usuario, text='Adicionar', command=lambda: self.salvar_dados_usuario(janela=janela_adicionar_usuario, 
                                                                                                                       nome=entry_nome.get(),
                                                                                                                       data_nascimento=entry_data_nascimento.get(),
                                                                                                                       cpf=entry_cpf.get(),
                                                                                                                       endereco=entry_endereco.get()))
        botao_confirmar.pack(padx=15, pady=15)

        janela_adicionar_usuario.mainloop()

    def update_botoes(self, cliente, label_info_contas, frame_botoes):
            ncontas = len(cliente.contas)
            if ncontas < 1: label_info_contas['text'] = f'Não há contas correntes registradas'
            elif ncontas == 1: label_info_contas['text'] = f'{ncontas} conta corrente registrada'
            else: label_info_contas['text'] = f'{ncontas} contas correntes registradas'
            
            for i in self.botoes_contas: 
                i.destroy()
            self.botoes_contas.clear()
            
            for conta in cliente.contas:
                    self.botoes_contas.append(Button(frame_botoes, text=f'Agência: {conta.agencia}\nC/C: {conta.numero}', command=lambda x=conta: self.abrir_janela_conta(x)))
                    self.botoes_contas[-1].pack(side='left', padx=5)

            botao = Button(frame_botoes, text='Criar nova conta corrente', command=lambda:self.criar_conta(cliente, frame_botoes=frame_botoes, 
                                                                                                           label_info_contas=label_info_contas))
            self.botoes_contas.append(botao)
            botao.pack(side='left', padx=5)
    
    def mostrar_info(self, label_info_contas, label_titulo, lista_usuarios, frame_botoes):
            index = lista_usuarios.curselection()
            if not index: return
            else: index = index[0]
            
            cliente = self.banco.clientes[index]
            label_titulo['text'] = cliente.dados()

            label_info_contas.pack()

            self.update_botoes(cliente, label_info_contas=label_info_contas, 
                             frame_botoes=frame_botoes)

    def criar_conta(self, cliente, frame_botoes, label_info_contas):
         self.banco.add_conta(cliente)
         self.update_botoes(cliente, label_info_contas, frame_botoes)
         
    def selecionar_usuario(self):
        self.botoes_contas.clear()
        
        janela_selecionar_usuario = Tk()
        janela_selecionar_usuario.title('Selecionar Usuário')
        janela_selecionar_usuario.geometry('700x275')
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

        for i in self.banco.clientes: lista_usuarios.insert('end', i)
        
        lista_usuarios.bind("<ButtonRelease-1>", lambda x: self.mostrar_info(label_info_contas=label_info_contas, 
                                                                             label_titulo=label_titulo, 
                                                                             lista_usuarios=lista_usuarios,
                                                                             frame_botoes=frame_botoes))

    def abrir_janela_conta(self, conta):
        
        def sacar():
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
            
            registro = Saque(valor).registrar(conta)
            if registro != 'sucesso':
                 messagebox.showerror(title='Erro', message=registro)
            att_saldo()
            self.banco.houve_alteracao = True

        def depositar():

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
            
            Deposito(valor).registrar(conta)
            att_saldo()
            self.banco.houve_alteracao = True

        def emitir_extrato():
            mensagem_extrato = conta.historico

            messagebox.showinfo(title=conta, message=mensagem_extrato)
        
        def att_saldo():
             label_saldo["text"] = f'{conta.cliente}\nAgência: {conta.agencia} C/C: {conta.numero}\nSaldo: R$ {conta.saldo:.2f}'


        janela_usuario = Tk()
        janela_usuario.title("Operações Financeiras")
        janela_usuario.geometry('400x200')
        janela_usuario.eval('tk::PlaceWindow . center')
        

        frame_saldo = Frame(janela_usuario)
        frame_saldo.pack(padx=50, pady=25)

        label_saldo = Label(frame_saldo, text=f'{conta.cliente}\n{conta}\nSaldo: R$ {conta.saldo:.2f}')
        label_saldo.grid(row=0, column=0)

        frame_botoes = Frame(janela_usuario)
        frame_botoes.pack(pady=25)

        botao_depositar = Button(frame_botoes, text='Depositar', command=depositar)
        botao_depositar.grid(row=0, column=0, padx=15)

        botao_sacar = Button(frame_botoes, text='Sacar', command=sacar)
        botao_sacar.grid(row=0, column=1, padx=15)

        botao_extrato = Button(frame_botoes, text='Extrato', command=emitir_extrato)
        botao_extrato.grid(row=0, column=2, padx=15)

        def set_limite_valor_saque():  
            valor = simpledialog.askstring('Limite do valor de saque', f'Digite o valor do limite de saque\nAtual: R${conta.limite:.2f}')
            if not valor: return

            try:
                valor = float(valor)
            except:
                messagebox.showerror(title='Erro', message='Digite um valor numérico!')
                return
            
            if valor <= 0:
                messagebox.showerror(title='Erro', message='Valor Inválido!')
                return
            
            conta.limite = valor

        def set_limite_saques():  
            valor = simpledialog.askstring('Limite de saques', f'Digite a quantidade do limite de saques\nAtual: {conta.limite_saques}\nUtilizados: {conta.saques_diarios}')
            if not valor: return
            try:
                valor = int(valor)
            except:
                messagebox.showerror(title='Erro', message='Digite um valor numérico inteiro!')
                return
            
            if valor <= 0:
                messagebox.showerror(title='Erro', message='Valor Inválido!')
                return
            
            conta.limite_saques = valor
        
        menubar = Menu(janela_usuario)
        configuracoes = Menu(menubar, tearoff=0)

        configuracoes.add_command(label='Mudar limite do valor de saque', command=set_limite_valor_saque)
        configuracoes.add_command(label='Mudar limite de saques', command=set_limite_saques)

        menubar.add_cascade(label='Configurações', menu=configuracoes)

        janela_usuario.config(menu=menubar)


        janela_usuario.mainloop()

if __name__ == '__main__':
    try:
        with open('desafio-dio-sistema-bancario/twicebankdata.pkl', 'rb') as file:
            twice_bank = pickle.load(file)
    except:
        twice_bank = Banco(simpledialog.askstring('Novo Banco', 'Digite o novo nome do Banco'))
        twice_bank.houve_alteracao = True
    
    UIB = InterfaceBanco(twice_bank)

    if UIB.banco.houve_alteracao:
        if messagebox.askokcancel(title='Salvamento', message='Salvar Alterações?'):
            with open('desafio-dio-sistema-bancario/twicebankdata.pkl', 'wb') as file:
                UIB.banco.houve_alteracao = False
                pickle.dump(UIB.banco, file)