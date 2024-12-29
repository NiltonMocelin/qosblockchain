# server para receber chave.pub
import socket
# import struct 
import os
import sys
import json
import subprocess

from new_blockchain_pbft_funcao import criar_blockchain
from sawtooth_cli.sawadm import main as sawtooth_keygen
from client.main_qos_cli import main as main_client

SERVER_IP='0.0.0.0'
SERVER_PORT=5555
MY_IP = SERVER_IP
TEST_MODE = False
SUDO_PASS = '214336414'

### recebe FRED como txt
#- carrega FRED from txt
#- inicia o container do blockchain genesis com os ips pares e portas de rede vindos do contrato
#- (se este for o genesis) copia as chaves publicas do FRED para /pbft-shared/validators/ no container 
#- o blockchain vai iniciar
#- Se este não for o genesis, enviar para o host origem


# FRED modelo: identificacao do fluxo, identificacao de QoS previsto, chaves_nos, genesis, ip_nos,
# (identificacao de fluxo)
#  ip_ver
#  ip_proto
#  ip_src
#  ip_dst
#  src_port
#  dst_port
#  mac_src
#  mac_dst
#  -
# (qos previsto)
#  banda
#  prioridade
#  classe
#  bandiwdth 
#  loss 
#  delay 
#  jitter
#  label 
# -
# (chaves publicas, nó genesis, ip_nos)
# ip_genesis (host origem do primeiro fluxo de uma blockchain)
# lista chaves publicas []
# lista ip_nós []
########

class Fred:
    def __init__(self, blockchain_name, AS_src_ip_range, AS_dst_ip_range, ip_ver, proto, ip_src, ip_dst, src_port, dst_port, mac_src, 
                 mac_dst, prioridade,classe,bandiwdth, loss, delay,jitter, label, ip_genesis, lista_chaves, lista_nos):
        self.ip_ver:str = ip_ver
        self.proto:str = proto
        self.ip_src:str  = ip_src 
        self.ip_dst:str = ip_dst
        self.src_port:str = src_port
        self.dst_port:str = dst_port
        self.mac_src:str = mac_src
        self.mac_dst:str  = mac_dst 
        
        self.prioridade:str = prioridade
        self.classe:str = classe
        self.bandiwdth:str = bandiwdth
        self.loss:str = loss
        self.delay:str = delay
        self.jitter:str  = jitter
        self.label:str = label

        self.blockchain_name:str = blockchain_name
        self.AS_src_ip_range:list = AS_src_ip_range
        self.AS_dst_ip_range:list = AS_dst_ip_range
        self.ip_genesis:str = ip_genesis
        self.lista_chaves:list = lista_chaves
        self.lista_nos:list = lista_nos
        
    def toString(self):

        str_AS_src_ip_range = ''
        str_AS_dst_ip_range = ''
        str_lista_chaves = ''
        str_lista_nos = ''

        for s in self.AS_src_ip_range:
            str_AS_src_ip_range+=',\"%s\"' % (s)

        for s in self.AS_dst_ip_range:
            str_AS_dst_ip_range+=',\"%s\"' % (s)
        
        for s in self.lista_chaves:
            str_lista_chaves+=',\"%s\"' % (s)
        
        for s in self.lista_nos:
            str_lista_nos+=',\"%s\"' % (s)
        
        str_AS_src_ip_range = str_AS_src_ip_range.replace(',','',1)
        str_AS_dst_ip_range = str_AS_dst_ip_range.replace(',','',1)
        str_lista_chaves = str_lista_chaves.replace(',','',1)
        str_lista_nos = str_lista_nos.replace(',','',1)

        return """{
    "ip_ver":"{}",
    "proto":"{}",
    "ip_src":"{}",
    "ip_dst":"{}",
    "src_port":"{}",
    "dst_port":"{}",
    "mac_src":"{}",
    "mac_dst":"{}",

    "prioridade":"{}",
    "classe":"{}",
    "bandiwdth":"{}",
    "loss":"{}",
    "delay":"{}",
    "jitter":"{}",
    "label":"{}",

    "blockchain_name":"{}",
    "AS_src_ip_range":[{}],
    "AS_dst_ip_range":[{}],
    "ip_genesis":"{}",
    "lista_chaves":[{}],
    "lista_nos":[{}]
    }""".format(self.ip_ver,self.proto,self.ip_src,self.ip_dst,self.src_port,self.dst_port,self.mac_src,self.mac_dst,
                self.prioridade,self.classe,self.bandiwdth,self.loss,self.delay,self.jitter,self.label,self.blockchain_name,
                str_AS_src_ip_range,str_AS_dst_ip_range,self.ip_genesis,str_lista_chaves,str_lista_nos)    

def fromJsonToFred(_json):
    """{
    "ip_ver":"",
    "ip_proto":"",
    "ip_src":"",
    "ip_dst":"",
    "src_port":"",
    "dst_port":"",
    "mac_src":"",
    "mac_dst":"",

    "prioridade":"",
    "classe":"",
    "bandiwdth":"",
    "loss":"",
    "delay":"",
    "jitter":"",
    "label":"",

    "blockchain_name":"",
    "ASN_src":"",
    "ASN_dst":"",
    "AS_src_ip_range":[],
    "AS_dst_ip_range":[],
    "ip_genesis":"",
    "lista_chaves":[],
    "lista_nos":[]
    }"""

    try:
        ip_ver = _json["ip_ver"]
        proto = _json["proto"]
        ip_src = _json["ip_src"]
        ip_dst = _json["ip_dst"]
        src_port = _json["src_port"]
        dst_port = _json["dst_port"]
        mac_src = _json["mac_src"]
        mac_dst = _json["mac_dst"]

        prioridade = _json["prioridade"]
        classe = _json["classe"]
        bandiwdth = _json["bandiwdth"]
        loss = _json["loss"]
        delay = _json["delay"]
        jitter = _json["jitter"]
        label = _json["label"]

        blockchain_name = _json["blockchain_name"]
        AS_src_ip_range = _json["AS_src_ip_range"]
        AS_dst_ip_range = _json["AS_dst_ip_range"]
        ip_genesis = _json["ip_genesis"]
        lista_chaves = _json["lista_chaves"]
        lista_nos = _json["lista_nos"]
    except:
        print("Error loading FRED from JSON !")

    return Fred(blockchain_name, AS_src_ip_range, AS_dst_ip_range, ip_ver, proto, ip_src, ip_dst, src_port, dst_port, mac_src, 
                 mac_dst, prioridade,classe,bandiwdth, loss, delay,jitter, label, ip_genesis, lista_chaves, lista_nos)

def consultar_blockchains(ip_src, ip_dst):
    return False

def ler_chave_publica(file_name):

    try:
        dados = open(file_name,'r').read()
    except:
        print("ERROR: Check the file name > ", file_name)

    return dados

def key_server():
    print("Iniciando servidor de Freds....\n")

    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #um desses funfa
    tcp.bind((SERVER_IP, SERVER_PORT))

    tcp.listen(5)

    while True:
        conn, addr = tcp.accept()

        print(" Recebendo FRED de ", addr)

        data = conn.recv(512).decode()

        fred_obj = fromJsonToFred(data)

        fred_rcvd = json.loads(data)

        print(fred_rcvd)

        conn.close()

        # procurar o nome de container utilizando o ip_destino
        # se container não existir
        ## criar container
        ## Criar a chave necessária
        ## copiar a chave para o container
        ## Se este for o nó gênesis, copiar as chaves do FRED para o container
        ## Se este não for o nó gênesis, copiar a chave gerada para o FRED
        ## enviar para FRED para o nó genesis gÊnesis

        # se for

        is_genesis = False

        if MY_IP == fred_rcvd['ip_src']:
            is_genesis = True

        ip_src = fred_rcvd['ip_src']
        ip_dst = fred_rcvd['ip_dst']

        nome_blockchain = fred_rcvd['blockchain_name']

        if nome_blockchain == '':
            nome_blockchain = ip_src+'_'+ip_dst

        if consultar_blockchains(ip_src, ip_dst):
            print("Já existe uma blockchain para esse fluxo... skipping")

            # montar mensagem e enviar como transação

            continue

        peers_ip_list = fred_rcvd['lista_nos']
        peers_ip_str = ''

        for ip in peers_ip_list:
            peers_ip_list+=',tcp://'+ip

        peers_ip_str = peers_ip_str.replace(',','',1)
        
        # portas expostas REST-API e NETWORK-PORT
        # listar portas expostas, escolher duas e anunciar
        VALIDADOR_PORT  = '4004'
        REST_API_PORT   = '8080'
        NETWORK_PORT    = '8800'
        CONSENSUS_PORT  = '5050'

        container_id = criar_blockchain(is_genesis= is_genesis, nome_blockchain=nome_blockchain, VALIDADOR_IP=SERVER_IP, VALIDADOR_PORT=VALIDADOR_PORT,
                         REST_API_IP=SERVER_IP,REST_API_PORT=REST_API_PORT,CONSENSUS_IP=SERVER_IP,CONSENSUS_PORT=CONSENSUS_PORT,NETWORK_IP=SERVER_IP,
                         NETWORK_PORT=NETWORK_PORT,PEERS_IP=peers_ip_str)

        ### CONDICAO: É O GENESIS
        if is_genesis:
            
            # copiando chaves publicas dos pares
            id_chave = 1
            for chave in fred_obj.lista_chaves:
                try:
                    nova_chave = open('$HOME/keys/validator-{}.pub'.format(id_chave),'w+')
                    nova_chave.write(chave)
                    nova_chave.close()
                except:
                    print('Erro ao escrever chaves publicas dos pares (EM nó gêneis)')
                subprocess.run(["docker", "cp", "$HOME/keys/validator-{}.pub".format(id_chave), container_id+":/pbft-shared/validators/validator-{}.pub".format(id_chave)], input=SUDO_PASS)
                id_chave+=1


            # salvar_arquivo('/pbft-shared/validators/', addr+'.pub', data)
            # gerar as chaves publicas e privadas sawadm e enviar para /etc/.... como validator-0
            sawtooth_keygen(prog_name="fred_server", args=["keygen", "--f"]) ## salva em /etc/sawtooth/keys/validator.pub e .priv OPS, modificado para salvar em $HOME/keys/validator.pub e .priv

            # todos precisam fazer -> genesis ou não
            subprocess.run(["docker", "cp", "$HOME/keys/validator.pub", container_id+":/etc/sawtooth/keys/validator.pub"], input=SUDO_PASS)
            subprocess.run(["docker", "cp", "$HOME/keys/validator.priv", container_id+":/etc/sawtooth/keys/validator.priv"], input=SUDO_PASS)
            # o próprio container vai copiar /etc/sawtooth/keys/validator.pub para /pbft-shared/validators/validator-0.pub

            # criar primeira transacao, com o
            main_client('fred_server', ["reg_qos", "{}_{}:{}_{}:{}_{}".format(fred_obj.ip_ver, fred_obj.ip_src, fred_obj.src_port, fred_obj.ip_dst, fred_obj.dst_port, fred_obj.proto), "\"{}\"".format(fred_obj.toString()), "--username", "host"])

        else: 
            # preencher o FRED e encaminhar para o nó genesis de origem. ---> se for um nó sdn, deve preencher e mandar via icmpv6 para frente
            
            sawtooth_keygen(prog_name="fred_server", args=["keygen", "--f"]) ## salva em /etc/sawtooth/keys/validator.pub e .priv OPS, modificado para salvar em $HOME/keys/validator.pub e .priv

            # todos precisam fazer -> genesis ou não
            subprocess.run(["docker", "cp", "$HOME/keys/validator.pub", container_id+":/etc/sawtooth/keys/validator.pub"], input=SUDO_PASS)
            subprocess.run(["docker", "cp", "$HOME/keys/validator.priv", container_id+":/etc/sawtooth/keys/validator.priv"], input=SUDO_PASS)
            # o próprio container vai copiar /etc/sawtooth/keys/validator.pub para /pbft-shared/validators/validator-0.pub

            #enviar FRED para o host genesis
            if TEST_MODE:
                continue

            #adicionar a chave publica criada no FRED e informações do genesis
            chave_publica = ler_chave_publica("$HOME/keys/validator.pub")

            fred_obj.lista_chaves.append(chave_publica)
            fred_obj.ip_genesis = MY_IP+':'+NETWORK_PORT
            fred_obj.lista_nos.append(MY_IP+':'+NETWORK_PORT)

            # enviar para host_genesis
            enviar_fred(fred_obj.toString(), fred_obj.ip_genesis, SERVER_PORT)
            

def enviar_fred(msg, server_ip, server_port):
    print("Enviando fred para -> %s:%s\n" % (server_ip,server_port))

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((SERVER_IP, SERVER_PORT))

    try:
        # tcp.send(len(dados))
        tcp.send(msg.encode())

        tcp.close()

    except:
        print("ERRO ao enviar fred !")
            

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


if __name__ == '__main__':
    """python server_fred_exchange_pbft.py"""
    """-M <my-ip-address> for identify the genesis node """
    """-S <server-ip> -> bind server-ip"""
    """-P <server-port> -> <bind server-port>"""
    """--test -> for testing mode"""

    if ( len(sys.argv) > 8):
        print('Error')
        raise SyntaxError('Too many options')

    for i in range(0, len(sys.argv)):
        if sys.argv[i] == '-S':
            try:
                SERVER_IP = sys.argv[i+1]
            except:
                print("Error: server-ip expected after -S")
        elif sys.argv[i] == '-P':
            try:
                SERVER_PORT = sys.argv[i+1]
            except:
                print("Error: server-port expected after -P")
        elif sys.argv[i] == '-M':
            try:
                MY_IP = sys.argv[i+1]
            except:
                print("Error: my-ip expected after -M")
        elif sys.argv[i] == '--test':
            TEST_MODE = True

    # client para enviar chave.pub
    key_server()