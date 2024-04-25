from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import locale
import json
locale.setlocale(locale.LC_TIME, 'pt_BR')


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

    def __str__(self):
        return self.nome
    
    def dados(self):
        info = f'Nome: {self.nome}\n'
        info += f'Data de Nascimento: {self.data_nascimento}\n'
        str_cpf = f'{self.cpf:011}'
        str_cpf = f'{str_cpf[0:3]}.{str_cpf[3:6]}.{str_cpf[6:9]}-{str_cpf[9:11]}'
        info += f'CPF: {str_cpf}\n'
        info += f'Endereço: {self.endereco}\n'
        return info


class Conta:
    def __init__(self, cliente, numero, saldo=0):
        self.saldo = saldo
        self.numero = numero
        self.agencia = 1 #f'{agencia:04}'
        self.cliente = cliente
        self.historico = Historico()

    def sacar(self, transacao):
        valor = transacao.valor
        if valor > saldo:
            return False
        saldo -= valor
        return True, 'sucesso'
        
    def depositar(self, transacao):
        valor = transacao.valor
        self.saldo += valor
        return True, 'sucesso'
    
    @property
    def agencia(self):
        return f'{self._agencia:04}'
    
    @agencia.setter
    def agencia(self, agencia):
        self._agencia = agencia
    
    def __str__(self):
        return (f'Titular da conta: {self.cliente}\n'+
                f'Agência: {self.agencia}\n'+
                f'Número da Conta: {self.numero}\n'+
                f'Saldo: {self.saldo}\n')
    
class ContaCorrente(Conta):
    _limite_padrao = 500
    _limite_saques_padrao = 10
    
    def __init__(self, cliente, numero, saldo=0):
        super().__init__(cliente, numero, saldo)
        self.limite = ContaCorrente._limite_padrao
        self.limite_saques = ContaCorrente._limite_saques_padrao
        self._saques_diarios =  0
        self._last_att = datetime.now()

    @property
    def saques_diarios(self):
        now = datetime.now()
        if now.date() > self._last_att.date():
            self._saques_diarios = 0
        self._last_att = now
        return self._saques_diarios
    
    @saques_diarios.setter
    def saques_diarios(self, saques):
        self._saques_diarios = saques

    def sacar(self, transacao):
        if self.saques_diarios >= self.limite_saques:
            return False, 'Limite de saques atingido'
        valor = transacao.valor
        if valor > self.limite:
            return False, 'Valor maior que limite de saque'
        if valor > self.saldo:
            return False, 'Saldo insuficiente'
        self.saldo -= valor
        self.saques_diarios += 1
        return True, 'sucesso'
    
    def __str__(self):
        return (f'Agência: {self.agencia:04} '+
                f'C/C: {self.numero}')


class Historico:
    def __init__(self):
        self.transacoes = []
    
    def adicionar_transacao(self, transacao):
    
        tipo = 'Depósito' if transacao.__class__.__name__ == 'Deposito' else 'Saque'

        self.transacoes.append({
            "tipo": tipo,
            "horario": datetime.now(),
            "valor": transacao.valor
            })


    def log_transacao(self, mostrar_saque=True, mostrar_deposito=True, hoje=False):
        
        output = ''
        for transacao in self.transacoes:
            if hoje and transacao["horario"].date() != datetime.now().date():
                continue
            if (transacao["tipo"] == 'Saque' and mostrar_saque) or (transacao["tipo"] == 'Depósito' and mostrar_deposito):
                output += (f'{transacao["tipo"]} no valor de R$ {transacao["valor"]:.2f} '+
                        f'às {transacao["horario"].strftime('%H:%M do dia %d de %B de %Y')}\n\n')
                
        if not output: return 'Histórico de Transações Vazio\n'
        return '\tHistórico de Transações:\n\n' + output
    
    def __str__(self):
        return self.log_transacao()

class Transacao(ABC):
    @abstractclassmethod
    def registrar(conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        sucesso = conta.sacar(self)
        if sucesso[0]:
            conta.historico.adicionar_transacao(self)
            return 'sucesso'
        else:
            return sucesso[1]



class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def registrar(self, conta):
        sucesso = conta.depositar(self)
        if sucesso[0]:
            conta.historico.adicionar_transacao(self)
            return 'sucesso'
        else:
            return sucesso[1]
        

class Banco:
    def __init__(self, nome_banco) -> None:
        self.nome_banco = nome_banco 
        self.clientes = []
        self.contas = []
        self.houve_alteracao = False
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            cliente = self.clientes[self.index]
            self.index += 1
            return cliente
        except:
            self.index = 0
            raise StopIteration
    
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
    
    def carregar_clientes(self):
        try:
            with open('desafio-dio-sistema-bancario/dados_usuarios copy.json', 'r') as dados_usuario_arquivo:
                dados_geral = json.load(dados_usuario_arquivo)
                for cliente in dados_geral["dados_usuarios"]:
                    self.add_cliente(endereco=cliente["endereco"],
                                    cpf=cliente["cpf"],
                                    nome=cliente["nome"],
                                    data_nascimento=cliente["data_nascimento"])
        except: 
            return 'Erro'


if __name__ == '__main__':
    print('Por favor execute o arquivo sistema_bancario_v3_interface.py')
    input()
