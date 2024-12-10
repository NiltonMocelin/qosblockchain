#!/usr/bin/env python
try:
    import docker
except:
    print("Install docker sdk !!")
    exit(0)

VALIDADOR_PORT = 4004
REST_API_PORT = 8008
CONSENSUS_PORT = 5050
NETWORK_PORT = 8800

# armazenar isso tudo dentro de uma lista

####################### subir container validador ######################
sawtooth_validator = docker.from_env()


print("Criar nova blockchain:: \n1 cria um container + setup blockchain: rest,settings,validador,consenso...")

  # for container in sawtooth_validator.containers.list(all=True):
  #     print("Nome:{} id:{}".format(container.name,container.short_id))

container_id = input()

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
    --endpoint tcp://validator:{} \
    --bind component:tcp://eth0:{} \
    --bind network:tcp://eth0:{} \
    --bind consensus:tcp://eth0:5050 \
  \" && \
  settings-tp -vv -C tcp://validator:{} & && \
  sawtooth-rest-api -vv -C tcp://validator:{} --bind rest-api:{} & && \
  devmode-engine-rust -C tcp://validator:5050 & && \
  ".format(VALIDADOR_PORT, NETWORK_PORT, VALIDADOR_PORT, VALIDADOR_PORT, NETWORK_PORT)

# sawtooth_validator.api.exec_create(container=container_id, cmd=cmd) # isso aqui seria caso tentar colocar vários blockchain no mesmo container(já existente)

exit(0)  
  

containers_list = [container.name for container in sawtooth_validator.containers.list(all=True)]

nome_blockchain = input("Digite o id da nova blockchain: ")

CONTAINER_NAME = "qos" + nome_blockchain

if CONTAINER_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

## subindo um container apenas
sawtooth_validator.containers.run(image="qosblockchainv1", name=CONTAINER_NAME, ports={'4004/tcp':VALIDADOR_PORT, '8008/tcp':REST_API_PORT,'8800/tcp':NETWORK_PORT}, entrypoint=entrypoint)

import signal
import sys

def signal_handler(sig, frame):
    # fechar os conatiners e remover todos ? ainda não
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()