from tkinter import Tk, Label, Button, Frame, simpledialog, messagebox

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

def sacar():
    
    global saldo, limite, extrato, numero_saques, LIMITE_SAQUES
    
    if numero_saques >= LIMITE_SAQUES:
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
    
    if valor > limite:
        messagebox.showerror(title='Erro', message='Valor acima do limite')
        return
    
    if valor > saldo:
        messagebox.showerror(title='Erro', message='Saldo não suficiente')
        return
    
    saldo -= valor
    numero_saques += 1
    extrato += f'Saque: -R$ {valor:.2f}\n'
    label_saldo['text'] = f'Saldo: R$ {saldo:.2f}'


def depositar():
    
    global saldo, extrato
    
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
    
    saldo += valor
    extrato += f'Depósito: +R$ {valor:.2f}\n'
    label_saldo['text'] = f'Saldo: R$ {saldo:.2f}'
        

def emitir_extrato():
    
    global extrato

    if extrato: mensagem_extrato = 'Transações Bancárias: \n\n' + extrato
    else: mensagem_extrato = 'Não há transações bancárias registradas'

    messagebox.showinfo(title='Extrato', message=mensagem_extrato)


janela = Tk()
janela.title("Sistema Bancário")
janela.geometry('300x150')

frame_saldo = Frame(janela)
frame_saldo.pack(padx=50, pady=25)

label_saldo = Label(frame_saldo, text=f'Saldo: R$ {saldo:.2f}')
label_saldo.grid(row=0, column=0)

frame_botoes = Frame(janela)
frame_botoes.pack(pady=25)

botao_depositar = Button(frame_botoes, text='Depositar', command=depositar)
botao_depositar.grid(row=0, column=0, padx=15)

botao_sacar = Button(frame_botoes, text='Sacar', command=sacar)
botao_sacar.grid(row=0, column=1, padx=15)

botao_extrato = Button(frame_botoes, text='Extrato', command=emitir_extrato)
botao_extrato.grid(row=0, column=2, padx=15)


janela.mainloop()
