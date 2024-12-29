#!/usr/bin/env python

## Consensus: Practical Byzantine Fault Tolerance

try:
    import docker
except:
    print("Install docker sdk !!")
    exit(0)
import sys
import signal

def criar_blockchain(nome_blockchain, VALIDADOR_IP, VALIDADOR_PORT, REST_API_IP, REST_API_PORT, CONSENSUS_IP, CONSENSUS_PORT, NETWORK_IP, NETWORK_PORT, PEERS_IP=None, is_genesis=False) -> str:
  """
  is_genesis: true if genesis, and false if not (default)
  nome_blockchain: blockchain and container name
  VALIDADOR_IP: validator module ip address
  VALIDADOR_PORT: validator module port
  REST_API_IP: rest_api module ip address
  REST_API_PORT: rest_api module port
  CONSENSUS_IP: consensus module ip address
  CONSENSUS_PORT: consensus module port
  NETWORK_IP: network ip address 
  NETWORK_PORT: network ip address
  PEERS_IP: pbft must be fully peered, if it is the genesis node == None
  Returns: container-id
  """

  ####################### subir container validador ######################
  print("Criar nova blockchain (containers: rest,settings,validador,consenso):")

  sawtooth_validator = docker.from_env()

  containers_list = [container.name for container in sawtooth_validator.containers.list(all=True)]

  print("Containers ativos: ", containers_list)

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


  if nome_blockchain in containers_list:
      print("ID existente, escolha outro !\nNenhum container foi criado")
      exit(0)

  # as chaves devem ser criadas por fora e copiadas para dentro
  # sawadm keygen &&\ (estaca antes de mkdir -p)

  entrypoint = "bash -c \"\
    mkdir -p /pbft-shared/validators || true && \
    while [[ ! -f /etc/sawtooth/keys/validator.pub ]]; \
    do sleep 2; done &&; \
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
    \"".format(main_validator if is_genesis else '', NETWORK_IP, NETWORK_PORT, VALIDADOR_IP, VALIDADOR_PORT, NETWORK_IP, NETWORK_PORT, CONSENSUS_IP, CONSENSUS_PORT, PEERS_IP)#, 'python main.py')
  # --network-auth trust \

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

  return CONTAINER_ID