
# server para receber chave.pub
import socket
# import struct 
import os
import sys
import json
import subprocess


# poder importar from parent directory
# sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )+"/client" )
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )

from new_blockchain_pbft_funcao import criar_blockchain
from sawtooth_cli.sawadm import main as sawtooth_keygen

# from client.main_qos_cli import main as main_client

SERVER_IP   = '0.0.0.0'
SERVER_PORT = 5555
MY_IP       = SERVER_IP
TEST_MODE   = False
HOST_NUMBER = 0
SUDO_PASS   = '214336414'
KEYS_LOCATION = '/sawtooth_keys/'

### recebe FRED como txt
#- carrega FRED from txt
#- inicia o container do blockchain genesis com os ips pares e portas de rede vindos do contrato
#- (se este for o genesis) copia as chaves publicas do FRED para /pbft-shared/validators/ no container 
#- o blockchain vai iniciar
#- Se este não for o genesis, enviar para o host origem


# FRED modelo: identificacao do fluxo, identificacao de QoS previsto, chaves_nos, genesis, ip_nos,
# (identificacao de fluxo)

# exemplo FRED:
    # {
    # "ip_ver":"4",
    # "proto":"tcp",
    # "ip_src":"192.168.0.1",
    # "ip_dst":"192.168.0.2",
    # "src_port":"9999",
    # "dst_port":"9988",
    # "mac_src":"xx",
    # "mac_dst":"xx",

    # "prioridade":"1",
    # "classe":"1",
    # "bandiwdth":"1",
    # "loss":"1",
    # "delay":"1",
    # "jitter":"1",
    # "label":"youtube-video-rt",

    # "blockchain_name":"",
    # "ASN_src":"",
    # "ASN_dst":"",
    # "AS_src_ip_range":[],
    # "AS_dst_ip_range":[],
    # "ip_genesis":"",
    # "lista_chaves":[],
    # "lista_nos":[]
    # }

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
    "proto":"",
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

def criar_par_chaves_sawadm():

    try:
        if not os.path.exists(KEYS_LOCATION): 
            os.mkdir(KEYS_LOCATION)
    except:
        print("Não foi possivel criar o folder: ", KEYS_LOCATION, " - make sure to run as root")
        exit(0)
    
    try:
        sawtooth_keygen(prog_name="fred_server", args=["keygen", "--f"]) ## salva em /etc/sawtooth/keys/validator.pub e .priv OPS, modificado para salvar em /keys/validator.pub e .priv
    except:
        print("Não foi possível criar as chaves publicas e privadas")
        exit(0)

    chave_publica = ler_arquivo(KEYS_LOCATION+"validator.pub")
    chave_privada = ler_arquivo(KEYS_LOCATION+"validator.priv")

    return chave_publica, chave_privada

def ler_arquivo(file_name):

    try:
        dados = open(file_name,'r').read().strip()
    except:
        print("ERROR: Check the file name > ", file_name)

    return dados

def key_server():
    print("Iniciando servidor de Freds (%s:%d)....\n" % (SERVER_IP, SERVER_PORT))

    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #um desses funfa
    tcp.bind((SERVER_IP, SERVER_PORT))

    tcp.listen(5)

    while True:
        conn, addr = tcp.accept()

        print(" Recebendo FRED de ", addr)

        data = conn.recv(512).decode()

        fred_json = json.loads(data)

        fred_obj = fromJsonToFred(fred_json)
        fred_json = ''

        conn.close()

        is_genesis = False
        chave_publica, chave_privada = criar_par_chaves_sawadm()
        chaves_peers:list = fred_obj.lista_chaves
        ips_peers:list = fred_obj.lista_nos

        if MY_IP == fred_obj.ip_src:
            is_genesis = True        

        if fred_obj.blockchain_name == '':
            fred_obj.blockchain_name = fred_obj.ip_src +"_"+fred_obj.ip_dst

        if consultar_blockchains(fred_obj.blockchain_name):
            print("Já existe uma blockchain para esse fluxo... skipping")
            continue

        REST_API_PORT= 8008
        NETWORK_PORT = 8800

        # criar container e blockchain
        container_id = criar_blockchain(is_genesis= is_genesis, chave_publica=chave_publica, chave_privada=chave_privada, chaves_peers=chaves_peers, nome_blockchain=fred_obj.blockchain_name,
                         REST_API_PORT=REST_API_PORT,NETWORK_PORT=NETWORK_PORT,PEERS_IP=ips_peers)

        if TEST_MODE:
            continue

        if is_genesis == False:
            
            fred_obj.lista_chaves.append(chave_publica)
            fred_obj.ip_genesis = MY_IP+':'+NETWORK_PORT
            fred_obj.lista_nos.append(MY_IP+':'+NETWORK_PORT)

            # enviar para host_genesis
            enviar_fred(fred_obj.toString(), fred_obj.ip_genesis, SERVER_PORT)            
        else:
            # criar primeira transacao, com o
            main_client('fred_server', ["reg_qos", "{}_{}:{}_{}:{}_{}".format(fred_obj.ip_ver, fred_obj.ip_src, fred_obj.src_port, fred_obj.ip_dst, fred_obj.dst_port, fred_obj.proto), "\"{}\"".format(fred_obj.toString()), "--username", "host"])


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