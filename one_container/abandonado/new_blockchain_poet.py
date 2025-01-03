#!/usr/bin/env python

## Consensus: Proof of Enlapsed time

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

print(len(sys.argv))
if (len(sys.argv) != 13 and len(sys.argv) != 15):
  print("Invalid args-> python new_blockchain1.py -host 0 -name <id-new-blockchain> -validator_port 4004 -rest_port 8008 -consensus_port 5050 -network_port 8800")
  print("or -> python new_blockchain1.py -host 1 (2 ou 3 ou 4) -name <id-new-blockchain> -validator_port 4004 -rest_port 8008 -consensus_port 5050 -network_port 8800 -seed <ip-validator0:port>")
  exit(0)

HOST_NUMBER = sys.argv[2]
nome_blockchain = sys.argv[4]

# container ports
VALIDADOR_PORT = sys.argv[6] #4004
REST_API_PORT  = sys.argv[8] #8008
CONSENSUS_PORT = sys.argv[10] #5050
NETWORK_PORT   = sys.argv[12] #8800
SEEDS           = '--seeds tcp://' + sys.argv[14] if len(sys.argv) == 15 else ''


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



main_validator_poet = "sawset genesis --key $HOME/.sawtooth/keys/my_key.priv -o config-genesis.batch && " 

if VALIDADOR_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

entrypoint = "bash -c \"\
  sawtooth keygen my_key && \
  sudo sawadm keygen && \
  {} \
  sawset proposal create --key $HOME/.sawtooth/keys/my_key.priv \
  -o config-consensus.batch \
  sawtooth.consensus.algorithm.name=PoET \
  sawtooth.consensus.algorithm.version=0.1 \
  sawtooth.poet.report_public_key_pem=\"$(cat /etc/sawtooth/simulator_rk_pub.pem)\" \
  sawtooth.poet.valid_enclave_measurements=$(poet enclave measurement) \
  sawtooth.poet.valid_enclave_basenames=$(poet enclave basename) && \
  poet registration create --key /etc/sawtooth/keys/validator.priv -o poet.batch &&\
  sawset proposal create --key $HOME/.sawtooth/keys/my_key.priv \
  -o poet-settings.batch \
  sawtooth.poet.target_wait_time=5 \
  sawtooth.poet.initial_wait_time=25 \
  sawtooth.publisher.max_batches_per_block=100 && \
  sudo -u sawtooth sawadm genesis \
  config-genesis.batch config-consensus.batch poet.batch poet-settings.batch &&\
  sawtooth-validator -vv \
      --minimum-peer-connectivity 1 \
      --bind network:tcp://{}:{} \
      --bind component:tcp://{}:{} \
      --bind consensus:tcp://{}:{} \
      --peering dynamic \
      --endpoint tcp://{}:{} \
      {} \
      --scheduler parallel \
      --network-auth trust \
  \"".format(main_validator_poet if HOST_NUMBER == '0' else '', NETWORK_IP, NETWORK_PORT, VALIDADOR_IP, VALIDADOR_PORT, CONSENSUS_IP, CONSENSUS_PORT, NETWORK_IP, NETWORK_PORT, SEEDS)#, 'python main.py')
# --network-auth trust \

print("entrypoint code: ", entrypoint)

CONTAINER_NAME = "qos" + nome_blockchain

if CONTAINER_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

## subindo um container apenas -- bloqueia o fluxo do codigo !
# sawtooth_validator.containers.run(image="qosblockchainv1", name=CONTAINER_NAME, ports={'4004/tcp':VALIDADOR_PORT, '8008/tcp':REST_API_PORT,'8800/tcp':NETWORK_PORT}, entrypoint=entrypoint)

#alternativo
# container_id = sawtooth_validator.api.create_container(
#     image='qosblockchainv1', name=CONTAINER_NAME, command='ls', ports=[(4004, 'tcp'),(5050,'tcp'), (8008,'tcp'), (8800,'tcp')], entrypoint=entrypoint,
#     host_config=sawtooth_validator.api.create_host_config(port_bindings={
#         '4004/tcp': VALIDADOR_PORT,
#         '8008/tcp': REST_API_PORT,
#         '8800/tcp': NETWORK_PORT,
#         '5050/tcp':None
#     })
# )

container_id = sawtooth_validator.api.create_container(
    image='qosblockchainv1', name=CONTAINER_NAME, command='ls')
sawtooth_validator.api.start(container_id)

CONTAINER_ID = sawtooth_validator.containers.get(CONTAINER_NAME)

print("Sucesso !")
print("Container Name:", CONTAINER_NAME)
print("Container ID:", CONTAINER_ID)

# ATIVOS
exec_settings_tp = sawtooth_validator.api.exec_create(container=container_id, cmd="settings-tp -vv -C tcp://{}:{}".format(VALIDADOR_IP,VALIDADOR_PORT))
exec_rest_api = sawtooth_validator.api.exec_create(container=container_id, cmd="sawtooth-rest-api -vv -C tcp://{}:{} --bind {}:{}".format(VALIDADOR_IP,VALIDADOR_PORT, REST_API_IP, REST_API_PORT))
exec_consensus = sawtooth_validator.api.exec_create(container=container_id, cmd="poet-engine -vv --connect tcp://{}:{}".format(CONSENSUS_IP,CONSENSUS_PORT))


sawtooth_validator.api.exec_start(exec_settings_tp, detach=True)
sawtooth_validator.api.exec_start(exec_rest_api, detach=True)
sawtooth_validator.api.exec_start(exec_consensus, detach=True)


signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()