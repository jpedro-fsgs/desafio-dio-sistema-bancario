from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import locale
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
    _limite_saques_padrao = 3
    
    def __init__(self, cliente, numero, saldo=0):
        super().__init__(cliente, numero, saldo)
        self.limite = ContaCorrente._limite_padrao
        self.limite_saques = ContaCorrente._limite_saques_padrao
        self.saques_diarios =  0

    def sacar(self, transacao):
        if self.saques_diarios >= self.limite_saques:
            return False, 'Limite de saque atingido'
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


    def __str__(self):
        
        if not self.transacoes: return 'Histórico de Transações Vazio\n'
        output = '\tHistórico de Transações:\n'
        for transacao in self.transacoes:
            output += (f'{transacao["tipo"]} no valor de R$ {transacao["valor"]:.2f} '+
                    f'às {transacao["horario"].strftime('%H:%M do dia %d de %B de %Y')}\n\n')
        return output



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


if __name__ == '__main__':
    print('Por favor execute o arquivo sistema_bancario_v3_interface.py')
    input()