#!/usr/bin/env python

## Consensus: Practical Byzantine Fault Tolerance
#https://gitee.com/bison-fork/sawtooth-pbft/blob/main/tests/test_liveness.yaml#

try:
    import docker
except:
    print("Install docker sdk !!")
    exit(0)

def criar_blockchain(nome_blockchain, chave_publica, chave_privada, CONSENSUS_PORT,VALIDATOR_PORT, REST_API_PORT, NETWORK_PORT, PEERS_IP:list=None, chaves_peers:list = None, is_genesis=False) -> str:
  """
  is_genesis: true if genesis, and false if not (default)
  nome_blockchain: blockchain and container name
  chave_publica: sawadm keygen .pub
  chave_privada: sawadm keygen .pub
  chaves_peers: chaves publicas sawadm keygen dos pares (importante para o nó gênesis) (3 max)
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

  print('lista_nos: ', PEERS_IP)

####################### subir container validador ######################
  print("Criar nova blockchain (containers: rest,settings,validador,consenso):")
  print('IS GENESIS: ', is_genesis)

  docker_container = docker.from_env()

  containers_list = [container.name for container in docker_container.containers.list(all=True)]

  print("Containers ativos: ", containers_list)

  if nome_blockchain in containers_list:
      print("ID existente, escolha outro !\nNenhum container foi criado")
      return -1

# as chaves devem ser criadas por fora e copiadas para dentro
  chave_publica1 = ''
  chave_publica2 = ''
  chave_publica3 = ''

  if is_genesis and len(chaves_peers) == 3 and len(PEERS_IP) == 4:
    chave_publica1 = chaves_peers[0]
    chave_publica2 = chaves_peers[1]
    chave_publica3 = chaves_peers[2]

  peers = ''
  for peer in PEERS_IP:
      peers += ',tcp://%s' % (peer)
  if peers != '':
    peers = '--peers ' + peers.replace(',','',1)

  #entrypoint
  cmd = "bash -c \"sawtooth-rest-api -vv -C tcp://0.0.0.0:%d --bind 0.0.0.0:%d \"" % (VALIDATOR_PORT, REST_API_PORT)

  main_key_config_cmd = "bash -c \"echo %s > /etc/sawtooth/keys/validator.pub && echo %s > /etc/sawtooth/keys/validator.priv && sawtooth keygen my_key\"" % (chave_publica,chave_privada)

  peer_key_config_cmd ="bash -c \"echo %s > /etc/sawtooth/keys/validator-1.pub && echo %s > /etc/sawtooth/keys/validator-2.pub && echo %s > /etc/sawtooth/keys/validator-3.pub\"" % (chave_publica1, chave_publica2, chave_publica3)

  genesis_config_cmd1 = "bash -c \"sawset genesis -k /etc/sawtooth/keys/validator.priv -o config-genesis.batch\""

  genesis_config_cmd2 = "bash -c \"sawadm genesis config-genesis.batch config.batch\""

  pbft_config_cmd = "bash -c \"sawset proposal create -k /etc/sawtooth/keys/validator.priv sawtooth.consensus.algorithm.name=pbft sawtooth.consensus.algorithm.version=1.0 sawtooth.consensus.pbft.members=\\['"'$(cat /etc/sawtooth/keys/validator.pub)'"','"'$(cat /etc/sawtooth/keys/validator-1.pub)'"','"'$(cat /etc/sawtooth/keys/validator-2.pub)'"','"'$(cat /etc/sawtooth/keys/validator-3.pub)'"'\\] sawtooth.publisher.max_batches_per_block=1200 -o config.batch\""

  # container args
  entrypoint_common = """sawtooth-validator -vv --endpoint tcp://0.0.0.0:%d --bind component:tcp://0.0.0.0:%d --bind network:tcp://0.0.0.0:%d --bind consensus:tcp://0.0.0.0:%d --scheduler parallel --peering static --maximum-peer-connectivity 4 %s" """ % (NETWORK_PORT, VALIDATOR_PORT,NETWORK_PORT, CONSENSUS_PORT, peers) # + pares

  entrypoint_genesis = "bash -c \"sawtooth-validator --endpoint tcp://0.0.0.0:%d --bind component:tcp://0.0.0.0:%d --bind network:tcp://0.0.0.0:%d --bind consensus:tcp://0.0.0.0:%d --peering static --scheduler parallel --maximum-peer-connectivity 4 %s\"" % (NETWORK_PORT, VALIDATOR_PORT, NETWORK_PORT, CONSENSUS_PORT, peers)

  container = docker_container.containers.run('qosblockchainv1', name=nome_blockchain, entrypoint=cmd, detach=True, network_mode='host')#, ports={'8008/tcp': REST_API_PORT, '8800/tcp': NETWORK_PORT, '4004/tcp': VALIDATOR_PORT, '5050/tcp':CONSENSUS_PORT})
  
  print(container.logs())

  if is_genesis:
    print('peer-key-configuration: ',container.exec_run("bash -c \"%s\" " % (peer_key_config_cmd), detach=True))
    print('genesis-configuration 1: ',container.exec_run("bash -c \"%s\" " % (genesis_config_cmd1), detach=True))
    print('genesis-configuration 2: ',container.exec_run("bash -c \"%s\" " % (genesis_config_cmd2), detach=True))
    print('pbft-configuration: ',container.exec_run("bash -c \"%s\" " % (pbft_config_cmd), detach=True))
    print('genesis-entrypoint: ',container.exec_run("bash -c \"%s\" " % (entrypoint_genesis), detach=True))
  else:
    print('peer-key-configuration: ',container.exec_run("bash -c \"%s\" " % (main_key_config_cmd), detach=True))
    print('common-entrypoint: ',container.exec_run("bash -c \"%s\" " % (entrypoint_common), detach=True))
  
  
  print('settings: ',container.exec_run("settings-tp -vv -C tcp://0.0.0.0:%d" % (VALIDATOR_PORT), detach=True))

  print('pbft-engine: ',container.exec_run("pbft-engine -vv --connect tcp://0.0.0.0:%d" % (CONSENSUS_PORT), detach=True))
  
  print('transaction-processor: ',container.exec_run("python3 main.py -C tcp://0.0.0.0:%d" % (VALIDATOR_PORT), detach=True))

  print("Sucesso !")
  print("Container Name:", nome_blockchain)
  print("Container ID:", container.short_id)

  return container.short_id



# cmdline do docker-compose que funciona
# sawadm keygen validator-1 && sawadm keygen validator-2 && sawadm keygen validator-3 && sawadm keygen && sawset genesis -k /etc/sawtooth/keys/validator.priv -o config-genesis.batch && sawset proposal create -k /etc/sawtooth/keys/validator.priv sawtooth.consensus.algorithm.name=pbft sawtooth.consensus.algorithm.version=1.0 sawtooth.consensus.pbft.members=\['"'$(cat /etc/sawtooth/keys/validator.pub)'"','"'$(cat /etc/sawtooth/keys/validator-1.pub)'"','"'$(cat /etc/sawtooth/keys/validator-2.pub)'"','"'$(cat /etc/sawtooth/keys/validator-3.pub)'"'\] -o config.batch && sawadm genesis config-genesis.batch config.batch && mv /etc/sawtooth/keys/validator-* /shared_keys && echo $(cat /etc/sawtooth/keys/validator.pub); sawtooth-validator --endpoint tcp://validator-0:8800 --bind component:tcp://eth0:4004 --bind network:tcp://eth0:8800 --bind consensus:tcp://eth0:5050 --peering static --scheduler parallel --maximum-peer-connectivity 3


# argumentos pbft

# (python string) \\\\\\[ \\''"'\\'$\\(cat /etc/sawtooth/keys/validator.pub\\)\\''"'\\' \\\\\\] == (bash ) sawtooth.consensus.pbft.members=\\\[ \''"'\'$\(cat /etc/sawtooth/keys/validator.pub\)\''"'\' \\\] == (argumento pbft) \['"'$(cat /etc/sawtooth/keys/validator.pub)'"'\]


# bash -c "echo sawtooth.consensus.pbft.members=\\\[ \''\"'\'$\(cat /etc/sawtooth/keys/validator.pub\)\''\"'\',\''\"'\'$\(cat /etc/sawtooth/keys/validator-1.pub\)\''\"'\',\''\"'\'$\(cat /etc/sawtooth/keys/validator-2.pub\)\''\"'\',\''\"'\'$\(cat /etc/sawtooth/keys/validator-3.pub\)\''\"'\' \\\] " == (argumento pbft) \['"'$(cat /etc/sawtooth/keys/validator.pub)'"'\]

# /usr/lib/python3/dist-packages/sawtooth_cli/sawset.py 328