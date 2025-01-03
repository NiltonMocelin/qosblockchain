#!/usr/bin/env python

## Consensus: Practical Byzantine Fault Tolerance

try:
    import docker
except:
    print("Install docker sdk !!")
    exit(0)
import sys
import signal

def signal_handler(sig, frame):
    print('You pressed Ctrl+C! \n Stopping and removing the containers...')
    sawtooth_validator = docker.from_env()

    # fechar os conatiners e remover
    # sawtooth_validator.api.stop(container=CONTAINER_ID)
    # sawtooth_validator.api.remove_container(container=CONTAINER_ID)
    sawtooth_validator.api.stop(container=CONTAINER_NAME)
    sawtooth_validator.api.remove_container(container=CONTAINER_NAME)

    print("Container PARADO e REMOVIDO -> Nome:{} ID:{}".format(CONTAINER_NAME, CONTAINER_ID))
    sys.exit(0)

PEERS=[]
print(len(sys.argv))
if (len(sys.argv) != 13 and len(sys.argv) != 17):
  print("Invalid args-> python new_blockchain1.py -host 0 -name <name-new-blockchain> -validator_port 4004 -rest_port 8008 -consensus_port 5050 -network_port 8800")
  print("or -> python new_blockchain1.py -host 1 (2 ou 3 ou 4) -name <name-new-blockchain> -validator_port 4004 -rest_port 8008 -consensus_port 5050 -network_port 8800 -npeers 2 -peers <ip-validator0:networkport,ip-validator1:networkport>")
  exit(0)

if (len(sys.argv) == 17 ):
  PEERS = sys.argv[16].split(',')

  if len(PEERS) != int(sys.argv[14]):
     print("Peer numbers informed and ips are different: ", len(PEERS), ' - ', int(sys.argv[14]))
     exit(0)

PEERS_IP = ''

for peer_ip in PEERS:
   PEERS_IP+= '--peers tcp://'+peer_ip+' '

print('AAA')

HOST_NUMBER = sys.argv[2]
nome_blockchain = sys.argv[4]

# container ports
VALIDADOR_PORT = sys.argv[6] #4004
REST_API_PORT  = sys.argv[8] #8008
CONSENSUS_PORT = sys.argv[10] #5050
NETWORK_PORT   = sys.argv[12] #8800

print('BBBB')

# ip_pares = []

# peers = ''

# if int(qtd_pares) > 0:
#   ip_pares =        sys.argv[14].split(',') # adicionar isso no entrypoint depois, nos pares

#   if len(ip_pares) != qtd_pares:
#      print("Invalid pairs: expected ", qtd_pares)
#      exit(0)
#   peers += '--peers'
#   for peer in ip_pares:
#      peers+= ' tcp://'+peer


####################### subir container validador ######################
print("Criar nova blockchain (containers: rest,settings,validador,consenso):")

sawtooth_validator = docker.from_env()

containers_list = [container.name for container in sawtooth_validator.containers.list(all=True)]

print("Containers ativos: ", containers_list)

# container name
VALIDADOR_NAME = "val"  + nome_blockchain
REST_API_NAME  = "rest" + nome_blockchain
SETTINGS_NAME  = "set"  + nome_blockchain
CONSENSUS_NAME = "cons" + nome_blockchain

# container ips
VALIDADOR_IP = '0.0.0.0'#'eth0'
REST_API_IP  = '0.0.0.0'#'eth0'
CONSENSUS_IP = '0.0.0.0'#'eth0'
NETWORK_IP   = '0.0.0.0'#'eth0'

# nem tudo do sugerido é necessário pois não vai haver configuracao anterior. Algumas coisas foram cortadas
main_validator = "while [[ ! -f /pbft-shared/validators/validator-0.pub || \
                 ! -f /pbft-shared/validators/validator-1.pub || \
                 ! -f /pbft-shared/validators/validator-2.pub || \
                 ! -f /pbft-shared/validators/validator-3.pub ]]; \
          do sleep 1; done &&\
          echo sawtooth.consensus.pbft.members=\\['\"'$$(cat /pbft-shared/validators/validator-0.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-1.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-2.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-3.pub)'\"'\\] && \
          sawset proposal create \
            -k /etc/sawtooth/keys/validator.priv \
            sawtooth.consensus.algorithm.name=pbft \
            sawtooth.consensus.algorithm.version=1.0 \
            sawtooth.consensus.pbft.members=\\['\"'$$(cat /pbft-shared/validators/validator-0.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-1.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-2.pub)'\"','\"'$$(cat /pbft-shared/validators/validator-3.pub)'\"'\\] \
            sawtooth.publisher.max_batches_per_block=1200 \
            -o config.batch &&\
          sawadm genesis config-genesis.batch config.batch &&"


if VALIDADOR_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

# as chaves devem ser criadas por fora e copiadas para dentro
# sawadm keygen &&\ (estaca antes de mkdir -p)

# entrypoint = "bash -c \"\
#   if [ -e /pbft-shared/validators/validator-0.priv ]; then \
#     cp /pbft-shared/validators/validator-0.pub /etc/sawtooth/keys/validator.pub \
#     cp /pbft-shared/validators/validator-0.priv /etc/sawtooth/keys/validator.priv \
#   fi && \
#   if [ ! -e /etc/sawtooth/keys/validator.priv ]; then \
#     sawadm keygen \
#     mkdir -p /pbft-shared/validators || true \
#     cp /etc/sawtooth/keys/validator.pub /pbft-shared/validators/validator-0.pub \
#     cp /etc/sawtooth/keys/validator.priv /pbft-shared/validators/validator-0.priv \
#   fi &&  \
#   {} \
#   sawtooth keygen my_key && \
#   sawtooth-validator -vv \
#     --endpoint tcp://{}:{} \
#     --bind component:tcp://{}:{} \
#     --bind network:tcp://{}:{} \
#     --bind consensus:tcp://{}:{} \
#     --scheduler parallel \
#     --peering static \
#     --maximum-peer-connectivity 10000 \
#     {} \
#   \"".format(HOST_NUMBER, HOST_NUMBER, main_validator if HOST_NUMBER == '0' else '', NETWORK_IP, NETWORK_PORT, VALIDADOR_IP, VALIDADOR_PORT, NETWORK_IP, NETWORK_PORT, CONSENSUS_IP, CONSENSUS_PORT, PEERS_IP)#, 'python main.py')
# # --network-auth trust \


entrypoint = "bash -c \"\
    sawadm keygen && \
    cp /etc/sawtooth/keys/validator.pub /pbft-shared/validators/validator-0.pub && \
    cp /etc/sawtooth/keys/validator.priv /pbft-shared/validators/validator-0.priv && \
    {} \
    sawtooth keygen my_key && \
    sawtooth-validator -vv \
      --endpoint tcp://{}:{} \
      --bind component:tcp://{}:{} \
      --bind network:tcp://{}:{} \
      --bind consensus:tcp://{}:{} \
      --scheduler parallel \
      --peering static \
      --maximum-peer-connectivity 10000 \
      {} \
    \"".format(main_validator if HOST_NUMBER == '0' else '', NETWORK_IP, NETWORK_PORT, VALIDADOR_IP, VALIDADOR_PORT, NETWORK_IP, NETWORK_PORT, CONSENSUS_IP, CONSENSUS_PORT, PEERS_IP)#, 'python main.py')


print("entrypoint code: ", entrypoint)

CONTAINER_NAME = "qos" + nome_blockchain

if CONTAINER_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

## subindo um container apenas -- bloqueia o fluxo do codigo !
# sawtooth_validator.containers.run(image="qosblockchainv1", name=CONTAINER_NAME, ports={'4004/tcp':VALIDADOR_PORT, '8008/tcp':REST_API_PORT,'8800/tcp':NETWORK_PORT}, entrypoint=entrypoint)

#alternativo --> aparentemnete só precisa exportar as portas REST-API para os clients acessarem e a porta de REDE para comunicação inter-validators
container_id = sawtooth_validator.api.create_container(
    image='qosblockchainv1', name=CONTAINER_NAME, command='ls', ports=[(4004, 'tcp'),(5050,'tcp'), (8008,'tcp'), (8800,'tcp')], entrypoint=entrypoint,
    host_config=sawtooth_validator.api.create_host_config(port_bindings={
        '4004/tcp': VALIDADOR_PORT,
        '8008/tcp': REST_API_PORT,
        '8800/tcp': NETWORK_PORT,
        '5050/tcp':None
    })
)

CONTAINER_ID = sawtooth_validator.containers.get(CONTAINER_NAME)

print("Sucesso !")
print("Container Name:", CONTAINER_NAME)
print("Container ID:", CONTAINER_ID)

# ATIVOS
exec_settings_tp = sawtooth_validator.api.exec_create(container=container_id, cmd="settings-tp -vv -C tcp://{}:{}".format(VALIDADOR_IP,VALIDADOR_PORT))
exec_rest_api = sawtooth_validator.api.exec_create(container=container_id, cmd="sawtooth-rest-api -vv -C tcp://{}:{} --bind {}:{}".format(VALIDADOR_IP,VALIDADOR_PORT, REST_API_IP, REST_API_PORT))
exec_consensus = sawtooth_validator.api.exec_create(container=container_id, cmd="pbft-engine -vv --connect tcp://{}:{}".format(CONSENSUS_IP,CONSENSUS_PORT))


sawtooth_validator.api.exec_start(exec_settings_tp, detach=True)
sawtooth_validator.api.exec_start(exec_rest_api, detach=True)
sawtooth_validator.api.exec_start(exec_consensus, detach=True)


signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()