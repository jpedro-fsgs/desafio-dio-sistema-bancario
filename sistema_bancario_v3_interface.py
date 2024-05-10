from tkinter import *
from tkinter.ttk import *
import pickle
from tkinter import messagebox, simpledialog, filedialog
from sistema_bancario_v3 import *


class InterfaceBanco(Tk):
    def __init__(
        self,
        banco,
        screenName: str | None = None,
        baseName: str | None = None,
        className: str = "Tk",
        useTk: bool = True,
        sync: bool = False,
        use: str | None = None,
    ) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.banco = banco
        self._log = self.banco.log

        self.title(banco.nome_banco)
        self.geometry("300x170+380+280")

        self.botoes_contas = []
        self.janela_selecionar_usuario = None
        self.janela_adicionar_usuario = None
        self.janela_conta = None

        menubar = Menu(self)

        configuracoes = Menu(menubar, tearoff=0)

        configuracoes.add_command(label="Log de Eventos", command=self.ver_log_eventos)
        configuracoes.add_command(
            label="Limpar todos os dados", command=self.limpar_dados
        )
        configuracoes.add_command(
            label="Resetar aos padrões", command=self.resetar_padroes
        )

        menubar.add_cascade(label="Configurações", menu=configuracoes)

        self.config(menu=menubar)
        botao_selecionar = Button(
            self, text="Selecionar usuário", command=self.selecionar_usuario
        )
        botao_selecionar.pack(pady=25)
        botao_adicionar = Button(
            self, text="Adicionar usuário", command=self.adicionar_usuario
        )
        botao_adicionar.pack(pady=25)

        def on_closing():
            if self.janela_selecionar_usuario:
                self.janela_selecionar_usuario.destroy()
            if self.janela_adicionar_usuario:
                self.janela_adicionar_usuario.destroy()
            if self.janela_conta:
                self.janela_conta.destroy()
            self.destroy()

        self.protocol("WM_DELETE_WINDOW", on_closing)

        self.mainloop()

    def ver_log_eventos(self):
        if (
            diretorio := filedialog.askdirectory(
                initialdir=Path(__file__).parent, title="Salvar log"
            )
        ) == "":
            return
        try:
            with open(
                f"{diretorio}/log_{self.banco.nome_banco.lower().replace(' ', '_')}.txt",
                "w",
            ) as logtxt:
                logtxt.write(self.log)
        except OSError:
            with open(f"{diretorio}/log_bank.txt", "w") as logtxt:
                logtxt.write(self.log)
        except:
            messagebox.showerror(
                title="Log de Eventos", message="Não foi possível criar arquivo de log!"
            )
            return

        messagebox.showinfo(
            title="Log de Eventos", message="Arquivo de log criado com sucesso!"
        )

    def limpar_dados(self):
        confirm = messagebox.showwarning(
            title="Atenção",
            message="Esta ação irá deletar o banco e todos os dados de "
            + "clientes e contas. Deseja continuar?",
            type="okcancel",
        )
        if confirm == "ok":
            self.banco = Banco(
                simpledialog.askstring("Novo Banco", "Digite o novo nome do Banco")
            )
            self._log = self.banco.log
            self.title(self.banco.nome_banco)
            self.adicionar_log(self.limpar_dados)
            self.banco.houve_alteracao = True

    def resetar_padroes(self):
        confirm = messagebox.showwarning(
            title="Atenção",
            message="Esta ação irá apagar todos os clientes e "
            + "contas adicionadas. Deseja continuar?",
            type="okcancel",
        )
        if confirm == "ok":
            novo_banco = Banco("TWICE Bank")
            if novo_banco.carregar_clientes():
                messagebox.showerror(
                    title="Erro",
                    message="Arquivo dados_usuarios copy.json não encontrado",
                )
                return
            self.banco = novo_banco
            self._log = self.banco.log
            self.title(self.banco.nome_banco)
            self.adicionar_log(self.resetar_padroes)
            self.banco.houve_alteracao = True

    def salvar_dados_usuario(self, nome, data_nascimento, cpf, endereco):
        if not (nome and data_nascimento and cpf and endereco):
            messagebox.showerror(title="Erro", message="Não pode haver campos vazios")
            return
        try:
            cpf = int(cpf)
        except ValueError:
            messagebox.showerror(
                title="Erro", message="Digite apenas os números do CPF"
            )
            return
        if any([cpf == i.cpf for i in self.banco.clientes]):
            messagebox.showerror(title="Erro", message="Este CPF já está cadastrado")
            return

        self.banco.add_cliente(endereco, cpf, nome, data_nascimento)
        messagebox.showinfo(
            title="Usuário cadastrado", message=f"{nome} cadastrado(a) com sucesso!"
        )

        self.adicionar_log(self.salvar_dados_usuario)
        self.janela_adicionar_usuario.destroy()
        self.janela_adicionar_usuario = None

    def adicionar_usuario(self):
        if self.janela_selecionar_usuario:
            self.janela_selecionar_usuario.destroy()
            self.janela_selecionar_usuario = None

        if self.janela_conta:
            self.janela_conta.destroy()
            self.janela_conta = None

        if self.janela_adicionar_usuario:
            self.janela_adicionar_usuario.destroy()
            self.janela_adicionar_usuario = None

        self.janela_adicionar_usuario = Tk()
        self.janela_adicionar_usuario.title("Adicionar Usuário")
        self.janela_adicionar_usuario.geometry("350x250+680+280")

        label_titulo = Label(
            self.janela_adicionar_usuario, text="Insira os dados do usuário"
        )
        label_titulo.pack(padx=15, pady=15)

        frame_dados = Frame(self.janela_adicionar_usuario)
        frame_dados.pack()

        label_nome = Label(frame_dados, text="Nome: ")
        entry_nome = Entry(frame_dados, width=31)
        label_nome.grid(row=0, column=0, padx=5, pady=5)
        entry_nome.grid(row=0, column=1, padx=5, pady=5)

        label_data_nascimento = Label(frame_dados, text="Data de Nascimento: ")
        entry_data_nascimento = Entry(frame_dados, width=31)
        label_data_nascimento.grid(row=1, column=0, padx=5, pady=5)
        entry_data_nascimento.grid(row=1, column=1, padx=5, pady=5)

        label_cpf = Label(frame_dados, text="CPF: ")
        entry_cpf = Entry(frame_dados, width=31)
        label_cpf.grid(row=2, column=0, padx=5, pady=5)
        entry_cpf.grid(row=2, column=1, padx=5, pady=5)

        label_endereco = Label(frame_dados, text="Endereço: ")
        entry_endereco = Entry(frame_dados, width=31)
        label_endereco.grid(row=3, column=0, padx=5, pady=5)
        entry_endereco.grid(row=3, column=1, padx=5, pady=5)

        botao_confirmar = Button(
            self.janela_adicionar_usuario,
            text="Adicionar",
            command=lambda: self.salvar_dados_usuario(
                nome=entry_nome.get(),
                data_nascimento=entry_data_nascimento.get(),
                cpf=entry_cpf.get(),
                endereco=entry_endereco.get(),
            ),
        )

        botao_confirmar.pack(padx=15, pady=15)

        def on_closing():
            self.janela_adicionar_usuario.destroy()
            self.janela_adicionar_usuario = None

        self.janela_adicionar_usuario.protocol("WM_DELETE_WINDOW", on_closing)

    def update_botoes(self, cliente, label_info_contas, frame_botoes):
        ncontas = len(cliente.contas)
        if ncontas < 1:
            label_info_contas["text"] = f"Não há contas correntes registradas"
        elif ncontas == 1:
            label_info_contas["text"] = f"{ncontas} conta corrente registrada"
        else:
            label_info_contas["text"] = f"{ncontas} contas correntes registradas"

        for i in self.botoes_contas:
            i.destroy()
        self.botoes_contas.clear()

        for conta in cliente.contas:
            self.botoes_contas.append(
                Button(
                    frame_botoes,
                    text=f"Agência: {conta.agencia}\nC/C: {conta.numero}",
                    command=lambda x=conta: self.abrir_janela_conta(x),
                )
            )
            self.botoes_contas[-1].pack(side="left", padx=5)

        botao = Button(
            frame_botoes,
            text="Criar nova conta corrente",
            command=lambda: self.criar_conta(
                cliente, frame_botoes=frame_botoes, label_info_contas=label_info_contas
            ),
        )
        self.botoes_contas.append(botao)
        botao.pack(side="left", padx=5)

    def mostrar_info(
        self, label_info_contas, label_titulo, lista_usuarios, frame_botoes
    ):
        index = lista_usuarios.curselection()
        if not index:
            return
        else:
            index = index[0]

        cliente = self.banco.clientes[index]
        label_titulo["text"] = cliente.dados()

        label_info_contas.pack(anchor="w")

        self.update_botoes(
            cliente, label_info_contas=label_info_contas, frame_botoes=frame_botoes
        )

    def criar_conta(self, cliente, frame_botoes, label_info_contas):
        self.banco.add_conta(cliente)
        self.update_botoes(cliente, label_info_contas, frame_botoes)
        self.adicionar_log(self.criar_conta)

    def selecionar_usuario(self):

        if self.janela_adicionar_usuario:
            self.janela_adicionar_usuario.destroy()
            self.janela_adicionar_usuario = None

        self.botoes_contas.clear()

        if self.janela_selecionar_usuario:
            self.janela_selecionar_usuario.destroy()
            self.janela_selecionar_usuario = None

        self.janela_selecionar_usuario = Tk()
        self.janela_selecionar_usuario.title("Selecionar Usuário")
        self.janela_selecionar_usuario.geometry("700x275+680+280")

        frame_usuarios = Frame(self.janela_selecionar_usuario)
        frame_usuarios.grid(row=0, column=0, pady=25, padx=25)

        lista_usuarios = Listbox(frame_usuarios, width=31)
        lista_usuarios.pack()

        frame_info = Frame(self.janela_selecionar_usuario)
        frame_info.grid(row=0, column=1, pady=25, padx=25)

        label_titulo = Label(frame_info, justify="left")
        label_titulo.pack(side="top", padx=15, pady=15)
        if self.banco.clientes:
            label_titulo["text"] = "Selecione o Usuário"
        else:
            label_titulo["text"] = "Não há usuários cadastrados"

        label_info_contas = Label(frame_info, justify="left")

        frame_botoes = Frame(self.janela_selecionar_usuario)
        frame_botoes.grid(row=1, column=1, sticky="W")

        for i in self.banco:
            lista_usuarios.insert("end", i)

        lista_usuarios.bind(
            "<ButtonRelease-1>",
            lambda x: self.mostrar_info(
                label_info_contas=label_info_contas,
                label_titulo=label_titulo,
                lista_usuarios=lista_usuarios,
                frame_botoes=frame_botoes,
            ),
        )

        def on_closing():
            if self.janela_conta:
                self.janela_conta.destroy()
                self.janela_conta = None
            self.janela_selecionar_usuario.destroy()
            self.janela_selecionar_usuario = None

        self.janela_selecionar_usuario.protocol("WM_DELETE_WINDOW", on_closing)

    def abrir_janela_conta(self, conta):

        def sacar():
            valor = simpledialog.askstring(
                "Operação de saque", "Digite o valor a ser sacado"
            )
            if not valor:
                return

            try:
                valor = float(valor)
            except ValueError:
                messagebox.showerror(title="Erro", message="Digite um valor numérico!")
                return

            if valor <= 0:
                messagebox.showerror(title="Erro", message="Valor Inválido!")
                return

            registro = Saque(valor).registrar(conta)
            if registro != "sucesso":
                messagebox.showerror(title="Erro", message=registro)
                return
            att_saldo()
            self.adicionar_log(sacar)
            self.banco.houve_alteracao = True

        def depositar():

            valor = simpledialog.askstring(
                "Operação de depósito", "Digite o valor a ser depositado"
            )
            if not valor:
                return

            try:
                valor = float(valor)
            except ValueError:
                messagebox.showerror(title="Erro", message="Digite um valor numérico!")
                return

            if valor <= 0:
                messagebox.showerror(title="Erro", message="Valor Inválido!")
                return

            Deposito(valor).registrar(conta)
            att_saldo()
            self.adicionar_log(depositar)
            self.banco.houve_alteracao = True

        def emitir_extrato():
            mensagem_extrato = conta.historico.extrato(
                mostrar_saque=check_saque_var.get(),
                mostrar_deposito=check_deposito_var.get(),
            )
            messagebox.showinfo(title=conta, message=mensagem_extrato)
            self.adicionar_log(emitir_extrato)

        def emitir_extrato_hoje():
            mensagem_extrato = conta.historico.extrato(
                mostrar_saque=check_saque_var.get(),
                mostrar_deposito=check_deposito_var.get(),
                hoje=True,
            )

            messagebox.showinfo(title=conta, message=mensagem_extrato)
            self.adicionar_log(emitir_extrato_hoje)

        def att_saldo():
            label_saldo["text"] = (
                f"{conta.cliente}\nAgência: {conta.agencia} C/C: {conta.numero}\nSaldo: R$ {conta.saldo:.2f}"
            )

        if self.janela_conta:
            self.janela_conta.destroy()
            self.janela_conta = None

        self.janela_conta = Tk()
        self.janela_conta.title("Operações Financeiras")
        self.janela_conta.geometry("525x225+680+586")

        frame_saldo = Frame(self.janela_conta)
        frame_saldo.pack(padx=50, pady=25)

        label_saldo = Label(
            frame_saldo, text=f"{conta.cliente}\n{conta}\nSaldo: R$ {conta.saldo:.2f}"
        )
        label_saldo.grid(row=0, column=0)

        frame_botoes = Frame(self.janela_conta)
        frame_botoes.pack(pady=25)

        botao_depositar = Button(frame_botoes, text="Depositar", command=depositar)
        botao_depositar.grid(row=0, column=0, padx=15)

        botao_sacar = Button(frame_botoes, text="Sacar", command=sacar)
        botao_sacar.grid(row=0, column=1, padx=15)

        botao_extrato_hoje = Button(
            frame_botoes, text="Extrato Hoje", command=emitir_extrato_hoje, width=15
        )
        botao_extrato_hoje.grid(row=0, column=2, padx=15)

        botao_extrato = Button(
            frame_botoes, text="Extrato Geral", command=emitir_extrato, width=15
        )
        botao_extrato.grid(row=1, column=2, padx=15)

        check_saque_var = BooleanVar(frame_botoes, value=True)
        check_deposito_var = BooleanVar(frame_botoes, value=True)

        check_saque_button = Checkbutton(
            frame_botoes, text="Saque", var=check_saque_var
        )
        check_saque_button.grid(row=0, column=3, sticky="W")

        check_deposito_button = Checkbutton(
            frame_botoes, text="Depósito", var=check_deposito_var
        )
        check_deposito_button.grid(row=1, column=3, sticky="W")

        def set_limite_valor_saque():
            valor = simpledialog.askstring(
                "Limite do valor de saque",
                f"Digite o valor do limite de saque\nAtual: R${conta.limite:.2f}",
            )
            if not valor:
                return

            try:
                valor = float(valor)
            except ValueError:
                messagebox.showerror(title="Erro", message="Digite um valor numérico!")
                return

            if valor <= 0:
                messagebox.showerror(title="Erro", message="Valor Inválido!")
                return

            conta.limite = valor
            self.adicionar_log(set_limite_valor_saque)
            self.banco.houve_alteracao = True

        def set_limite_saques():
            valor = simpledialog.askstring(
                "Limite de saques",
                (
                    "Digite a quantidade do limite de saques\n"
                    + f"Atual: {conta.limite_saques}\n"
                    + f"Utilizados: {conta.saques_diarios}"
                ),
            )
            if not valor:
                return
            try:
                valor = int(valor)
            except ValueError:
                messagebox.showerror(
                    title="Erro", message="Digite um valor numérico inteiro!"
                )
                return

            if valor <= 0:
                messagebox.showerror(title="Erro", message="Valor Inválido!")
                return

            conta.limite_saques = valor
            self.adicionar_log(set_limite_saques)
            self.banco.houve_alteracao = True

        menubar = Menu(self.janela_conta)
        configuracoes = Menu(menubar, tearoff=0)

        configuracoes.add_command(
            label="Mudar limite do valor de saque", command=set_limite_valor_saque
        )
        configuracoes.add_command(
            label="Mudar limite de saques", command=set_limite_saques
        )

        menubar.add_cascade(label="Configurações", menu=configuracoes)

        self.janela_conta.config(menu=menubar)

        def on_closing():
            self.janela_conta.destroy()
            self.janela_conta = None

        self.janela_conta.protocol("WM_DELETE_WINDOW", on_closing)

    def adicionar_log(self, funcao):
        self._log += f"{datetime.now()}: {funcao.__name__.upper()}\n"

    @property
    def log(self):

        if self._log:
            return self._log
        return "VAZIO"


if __name__ == "__main__":
    try:
        with open(Path(__file__).parent / "bankdata.pkl", "rb") as file:
            twice_bank = pickle.load(file)
    except FileNotFoundError:
        twice_bank = Banco(
            simpledialog.askstring("Novo Banco", "Digite o novo nome do Banco")
        )
        twice_bank.houve_alteracao = True

    UIB = InterfaceBanco(twice_bank)

    if UIB.banco.houve_alteracao:
        if messagebox.askyesno(title="Salvamento", message="Salvar alterações?"):
            with open(Path(__file__).parent / "bankdata.pkl", "wb") as file:
                UIB.banco.log = UIB.log
                UIB.banco.houve_alteracao = False
                pickle.dump(UIB.banco, file)
