from socket import *
import random
from bitarray import bitarray

#informacoes do servidor
porta_servidor = 50000
ip_server =  "15.228.191.109"

socket_cliente = socket(AF_INET,SOCK_DGRAM)

while(True):
    
    print('1 - Data e hora atual')
    print('2 - Uma mensagem motivacional para o fim do semestre')
    print('3 - A quantidade de respostas emitidas pelo servidor até o momento')
    print('4 - Sair')
    
    entrada = input('Digite um numero: ')
    
    #tratamento diferente para a requisicao 3
    requisicao_3 = False
    
    mensagem = bitarray()
    # 4 bits para requisicao/response, nesse caso só requisição
    mensagem += bitarray('0000')
    # coloca os 4 bits relacionados ao tipo de requisicao
    if entrada == '1': 
        mensagem += bitarray('0000')
    elif entrada == '2':
        mensagem += bitarray('0001')
    elif entrada == '3':
        mensagem += bitarray('0010')
        requisicao_3 = True
    elif entrada == '4':
        print("saindo\n")
        socket_cliente.close()
        break
    else:
        print('\nvalor de entrada invalido\n')
        continue
    
    print(f"\nBitarray de requisição: {mensagem}")
    
    # Identificador para a requisicao, recebe o valor em 2 bytes
    identificador = random.randint(1,65535).to_bytes(2)
    
    mensagem.frombytes(identificador)
    
    # Transforma mensagem para bytes e envia para o servidor
    socket_cliente.sendto(mensagem.tobytes(),(ip_server,porta_servidor))

    resposta, endereco_sevidor = socket_cliente.recvfrom(50000)
    # Pula o cabecalho da resposta ( 4 bytes ) e pega o restante
    resposta = resposta[4:]
    if requisicao_3:
        # Converte os bytes para um valor numerico inteiro
        resposta = int.from_bytes(resposta,"big")
        print('=========================================\n')
        print(f'Número de respostas: {resposta}\n')
        print('=========================================\n')
        # False para requisicao 3 ate a entrada ser 3 novamente
        requisicao_3 = False
    else:
        print('=========================================\n')
        print(f'Resposta: {resposta.decode()}\n')
        print('=========================================\n')