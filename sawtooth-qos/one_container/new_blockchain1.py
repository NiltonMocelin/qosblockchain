#!/usr/bin/env python
try:
    import docker
except:
    print("Install docker sdk !!")
    exit(0)
import sys


if (sys.argv < 5):
  print("Invalid args-> python new_blockchain1.py -id <id-new-blockchain> -npairs 3 -ippairs x.x.x.x:port,y.y.y.y:port")
  exit(0)

nome_blockchain = sys.argv[2]
qtd_pares =       sys.argv[4]
ip_pares =        sys.argv[6].split(',')

# armazenar isso tudo dentro de uma lista

####################### subir container validador ######################
print("Criar nova blockchain (containers: rest,settings,validador,consenso):")

sawtooth_validator = docker.from_env()

containers_list = [container.short_id for container in sawtooth_validator.containers.list(all=True)]

print("Containers ativos: ", containers_list)

# container name
VALIDADOR_NAME = "val"  + nome_blockchain
REST_API_NAME =  "rest" + nome_blockchain
SETTINGS_NAME=   "set"  + nome_blockchain
CONSENSUS_NAME=  "cons" + nome_blockchain

# container ports
VALIDADOR_PORT = 4004
REST_API_PORT =  8008
CONSENSUS_PORT = 5050
NETWORK_PORT =   8800

# container ips
VALIDADOR_PORT = 'localhost'
REST_API_PORT =  'localhost'
CONSENSUS_PORT = 'localhost'
NETWORK_PORT =   'localhost'


if VALIDADOR_NAME in containers_list:
    print("ID existente, escolha outro !\nNenhum container foi criado")
    exit(0)

# print(sawtooth_validator.api.images(name="hyperledger/sawtooth-validator", quiet=False, all=False, filters=None))
    
# exit(0)
# if not sawtooth_validator.api.get().get("hyperledger/sawtooth-validator"):
sawtooth_validator.api.pull("hyperledger/sawtooth-validator:chime", stream=True, decode=True)#", tag="chime")

sawtooth_validator.containers.run(image="hyperledger/sawtooth-validator:chime", name=VALIDADOR_NAME, ports={'8008/tcp':REST_API_PORT, '5050/tcp':NETWORK_PORT}, entrypoint="bash -c \"\
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
          --bind consensus:tcp://eth0:{} \
        \"".format(NETWORK_PORT, VALIDADOR_PORT, NETWORK_PORT, CONSENSUS_PORT))


####################### subir container settings-tp ######################
sawtooth_settings = docker.from_env()
sawtooth_settings.api.pull("hyperledger/sawtooth-settings-tp:chime")

sawtooth_settings.containers.run(image="hyperledger/sawtooth-settings-tp:chime",name=SETTINGS_NAME, entrypoint="settings-tp -vv -C tcp://validator:{}".format(VALIDADOR_PORT))

####################### subir container rest-api ######################
sawtooth_rest = docker.from_env()
sawtooth_rest.api.pull("hyperledger/sawtooth-rest-api:chime")

sawtooth_rest.containers.run(image="hyperledger/sawtooth-rest-api:chime",name=REST_API_NAME,ports={'8008/tcp':REST_API_PORT}, entrypoint="sawtooth-rest-api -vv -C tcp://validator:{} --bind rest-api:{}".format(VALIDADOR_PORT, REST_API_PORT))

####################### subir container consenso ######################
sawtooth_consenso = docker.from_env()
sawtooth_consenso.api.pull("hyperledger/sawtooth-devmode-engine-rust:chime")

sawtooth_consenso.containers.run(image="hyperledger/sawtooth-devmode-engine-rust:chime",name=CONSENSUS_NAME,ports={'5050/tcp':CONSENSUS_PORT}, entrypoint="devmode-engine-rust -C tcp://validator:{}".format(CONSENSUS_PORT))

import signal
import sys

def signal_handler(sig, frame):
    # fechar os conatiners e remover todos ?


    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()