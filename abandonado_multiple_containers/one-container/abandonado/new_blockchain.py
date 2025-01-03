#!/usr/bin/env python
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

if (len(sys.argv) < 13):
  print("Invalid args-> python new_blockchain1.py -name <id-new-blockchain> -validator_port <port> -rest_port <port> -consensus_port <port> -network_port <port> -npairs 3 -ippairs x.x.x.x:port,y.y.y.y:port")
  exit(0)

nome_blockchain = sys.argv[2]

# container ports
VALIDADOR_PORT = sys.argv[4] #4004
REST_API_PORT  = sys.argv[6] #8008
CONSENSUS_PORT = sys.argv[8] #5050
NETWORK_PORT   = sys.argv[10] #8800

qtd_pares =       sys.argv[12]
ip_pares = []


if int(qtd_pares) > 0:
  ip_pares =        sys.argv[6].split(',') # adicionar isso no entrypoint depois, nos pares

  if len(ip_pares) != qtd_pares:
     print("Invalid pairs: expected ", qtd_pares)
     exit(0)


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


if VALIDADOR_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

entrypoint = "bash -c \"\
  sawadm keygen && \
  sawtooth keygen my_key && \
  sawset genesis -k /root/.sawtooth/keys/my_key.priv && \
  sawset proposal create \
    -k /root/.sawtooth/keys/my_key.priv \
    sawtooth.consensus.algorithm.name=Devmode \
    sawtooth.consensus.algorithm.version=0.1 \
    -o config.batch && \
  sawadm genesis config-genesis.batch config.batch  && \
  sawtooth-validator -vv \
    --endpoint tcp://{}:{} \
    --bind component:tcp://{}:{} \
    --bind network:tcp://{}:{} \
    --bind consensus:tcp://{}:{} \
    --scheduler parallel \
    --peering static \
    --maximum-peer-connectivity 10000 \
    --peers tcp://{}:{}\
  \"".format(VALIDADOR_IP, NETWORK_PORT, REST_API_IP, VALIDADOR_PORT, NETWORK_IP, NETWORK_PORT, CONSENSUS_IP, CONSENSUS_PORT, VALIDADOR_IP, VALIDADOR_PORT)#,VALIDADOR_IP, VALIDADOR_PORT,VALIDADOR_IP, VALIDADOR_PORT,REST_API_IP, REST_API_PORT, CONSENSUS_IP, CONSENSUS_PORT)
# essas portas e ips ein... mas é o que traduzi do single-node example
# # sawtooth_validator.api.exec_create(container=container_id, cmd=cmd) # isso aqui seria caso tentar colocar vários blockchain no mesmo container(já existente)
# """settings-tp -vv -C tcp://{}:{} &
#   sawtooth-rest-api -vv -C tcp://{}:{} --bind {}:{} &
#   devmode-engine-rust -C tcp://{}:{} & echo DONE!"""

CONTAINER_NAME = "qos" + nome_blockchain

if CONTAINER_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

## subindo um container apenas -- bloqueia o fluxo do codigo !
# sawtooth_validator.containers.run(image="qosblockchainv1", name=CONTAINER_NAME, ports={'4004/tcp':VALIDADOR_PORT, '8008/tcp':REST_API_PORT,'8800/tcp':NETWORK_PORT}, entrypoint=entrypoint)

#alternativo
container_id = sawtooth_validator.api.create_container(
    image='qosblockchainv1', name=CONTAINER_NAME, command='ls', ports=[(4004, 'tcp'),(5050,'tcp'), (8008,'tcp'), (8800,'tcp')], entrypoint=entrypoint,
    host_config=sawtooth_validator.api.create_host_config(port_bindings={
        '4004/tcp': VALIDADOR_PORT,
        '8008/tcp': REST_API_PORT,
        '8800/tcp': NETWORK_PORT,
        '5050/tcp':None
    })
)
sawtooth_validator.api.start(container_id)

CONTAINER_ID = sawtooth_validator.containers.get(CONTAINER_NAME)

print("Sucesso !")
print("Container Name:", CONTAINER_NAME)
print("Container ID:", CONTAINER_ID)

exec_settings_tp = sawtooth_validator.api.exec_create(container=container_id, cmd="settings-tp -vv -C tcp://{}:{}".format(VALIDADOR_IP,VALIDADOR_PORT))
exec_rest_api = sawtooth_validator.api.exec_create(container=container_id, cmd="sawtooth-rest-api -vv -C tcp://{}:{} --bind {}:{}".format(VALIDADOR_IP,VALIDADOR_PORT, REST_API_IP, REST_API_PORT))
exec_consensus = sawtooth_validator.api.exec_create(container=container_id, cmd="devmode-engine-rust -C tcp://{}:{}".format(VALIDADOR_IP,CONSENSUS_PORT))
# exec_processor = sawtooth_validator.api.exec_create(container=container_id, cmd="python processor/main.py -C tcp://{}:{}".format(VALIDADOR_IP,VALIDADOR_PORT))

sawtooth_validator.api.exec_start(exec_settings_tp, detach=True)
sawtooth_validator.api.exec_start(exec_rest_api, detach=True)
sawtooth_validator.api.exec_start(exec_consensus, detach=True)
# sawtooth_validator.api.exec_start(exec_processor, detach=True)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()