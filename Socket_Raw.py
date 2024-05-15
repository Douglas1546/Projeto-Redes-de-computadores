from socket import *
import struct
import random
from bitarray import bitarray
from dotenv import load_dotenv
import os

load_dotenv()

# Cria socket raw com o protocolo UDP
socketRaw = socket(AF_INET,SOCK_RAW,IPPROTO_UDP)
ip_server = "15.228.191.109"    
porta_servidor = 50000          
porta_local = 50000             
meu_ip = os.getenv('MEU_IP') # Endereco de IP local, Crie um arquivo chamado ".env" e adicione 'MEU_IP = "seu-ip-aqui"'

def checksum(mensagem):
    # Calcula o checksum para garantir a integridade dos dados
    sum = 0
    # Adicao de um byte de zeros, caso o tamanho do payload + cabeçalho UDP seja um valor ímpar
    if len(mensagem) % 2 == 1:
        mensagem += b'\x00'
        
    for i in range(0, len(mensagem), 2):                # Aqui iteramos o loop para 2 bytes de cada vez
        par_byte = mensagem[i] + (mensagem[i+1] << 8)   # Aqui reordenamos os bytes devido ao sistema estar utilizando Little Endian
                                                        # Little Endian coloca o byte menos significativo primeiro e o byte mais significativo logo em seguida
        sum += par_byte
        sum = (sum & 0xffff) + (sum >> 16) # garante que o sum seja do tamanho de 2 bytes e soma com o(s) bit(s) excedentes

    checksum_valor = ~sum & 0xffff # Aqui garantimos novamente que o sum tenha um tamanho de 2 bytes e por fim pegamos o complemento dele
    return checksum_valor

def udp_cabecalho(payload, ip_server = ip_server, porta_servidor = porta_servidor, meu_ip = meu_ip, porta_local = porta_local):
    # Monta o cabeçalho UDP com checksum para enviar os dados.
    length = 8 + len(payload)                                                                       # Comprimento do cabeçalho UDP + payload
    pseudo_cabecalho = inet_aton(meu_ip) + inet_aton(ip_server) + struct.pack('!HH', 17, length)    # 17 indica o protocolo UDP
    cabecalho_udp = struct.pack('!HHHH', porta_servidor, porta_local, length, 0)                    # Monta o cabeçalho sem o checksum
    checksum_data = pseudo_cabecalho + cabecalho_udp + payload                                      # Combina o cabeçalho pseudo, o cabeçalho UDP e o payload para o cálculo do checksum
    udp_checksum = checksum(checksum_data)                                                          # Calcula Checksum
    
    cabecalho_udp = struct.pack('!HHH', porta_local, porta_servidor, length) + struct.pack('H', udp_checksum) # Reconstrói o cabeçalho UDP incluindo o checksum calculado
    pacote = cabecalho_udp + payload # Combina o cabeçalho UDP completo e o payload para formar o pacote final
    return pacote

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
        socketRaw.close() # Fecha o socket
        break
    else:
        print('\nvalor de entrada invalido\n')
        continue
    
    print(f"\nBitarray de requisição: {mensagem}\n")
    
    #identificador para a requisicao, recebe o valor em 2 bytes
    identificador = random.randint(1,65535).to_bytes(2)
    
    #coloca o valor recebido em bit no final da variavel mensagem
    mensagem.frombytes(identificador)
    mensagem = mensagem.tobytes()
    
    # Monta o pacote com o cabeçalho UDP
    pacote = udp_cabecalho(mensagem)
    
    # Envia o pacote para o servidor
    socketRaw.sendto(pacote,(ip_server,porta_servidor))
    
    valid_response = False
    while not valid_response:
        try:
            # Espera pela resposta do servidor
            resposta, enderecoServidor = socketRaw.recvfrom(50000)
            
            # Remove o cabeçalho da resposta
            resposta = resposta[32:]
            
            if requisicao_3:
                #converte os bytes para um valor numerico inteiro
                resposta = int.from_bytes(resposta, "big")
                if resposta < 1000000:  # Aqui a gente colocou um limite para o numero de respostas, para evitar problemas de overflow
                    print('\n=========================================\n')
                    print(f'Número de respostas: {resposta}')
                    print('\n=========================================\n')
                    #False para requisicao 3 ate a entrada ser 3 novamente
                    valid_response = True
                else:
                    print("Requisição falhou, tentando novamente...")
            else:
                # Decodifica a resposta para string
                decoded_resposta = resposta.decode('utf-8')
                print('\n=========================================\n')
                print(f'Resposta: {decoded_resposta}')
                print('\n=========================================\n')
                valid_response = True
        except UnicodeDecodeError:
            print("Requisição falhou, tentando novamente...")
        except ValueError:
            print("Requisição falhou, tentando novamente...")
