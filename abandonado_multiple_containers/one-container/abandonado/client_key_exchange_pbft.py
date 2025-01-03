# server para receber chave.pub
import socket
import struct 
import os
import sys

SERVER_IP='0.0.0.0'
SERVER_PORT=5555
ARQUIVO = ''

def key_client():

    print("Enviando %s para -> %s:%s\n" % (ARQUIVO,SERVER_IP,SERVER_PORT))

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((SERVER_IP, SERVER_PORT))

    try:
        file = open(ARQUIVO)

        dados = file.read()
        print(dados)

        # tcp.send(len(dados))
        tcp.send(dados.encode())

        tcp.close()

    except:
        print("ERRO ao enviar arquivo !")
        
def salvar_arquivo(caminho_arquivo, nome_arquivo, dados):

    #mkdir if doesn't exist
    try:
        os.makedirs(caminho_arquivo)
    except:
        print("Folder %s já existente, seguindo..." % (caminho_arquivo))

    #write
    file = open(caminho_arquivo+nome_arquivo,'w+')
    file.write(dados)
    file.close()
    print("Aquivo %s escrito" % (caminho_arquivo+nome_arquivo))

# client para enviar chave.pub


if len(sys.argv) != 4:
    print("[erro-modo de usar->] python client_key_exchange_pbft.py <ip_destino> <port> <caminho>\n")
    exit(0)

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
ARQUIVO = sys.argv[3]

key_client()
