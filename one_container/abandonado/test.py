import docker


VALIDATOR_PORT = 4004
REST_API_PORT = 8008
NETWORK_PORT = 8800
CONTAINER_NAME = 'qostest'

# entrypoint = """echo "0318f949c3dd5e1077c604b09db452b94491b0e94d92ce929ed593d74faf8eb417" > /etc/sawtooth/keys/validator.pub &&     echo "4d2ea9b221ccc2f786d829bdc4168495247b555362a2e24be846d376276cbd41" > /etc/sawtooth/keys/validator.priv && cp /etc/sawtooth/keys/validator.pub /pbft-shared/validators/validator-0.pub && cp /etc/sawtooth/keys/validator.priv /pbft-shared/validators/validator-0.priv && sawtooth keygen my_key && sawtooth-validator -vv --endpoint tcp://0.0.0.0:8800 --bind component:tcp://0.0.0.0:4004 --bind network:tcp://0.0.0.0:8800 --bind consensus:tcp://0.0.0.0:5050 --scheduler parallel --peering static --maximum-peer-connectivity 10000"""

container_aux = docker.from_env()

container = container_aux.containers.run('qosblockchainv1', network_mode='host')

print(container.short_id)
print(container.logs())