#!/usr/bin/env python
try:
    import docker
except:
    print("Install docker sdk !!")
    exit(0)

print("Listando containers (parados e executando):")

####################### subir container validador ######################
sawtooth_validator = docker.from_env()

containers_list = [("nome:{}, id:{}, status:{}".format(container.name, container.short_id, container.status)) for container in sawtooth_validator.containers.list(all=True)]
print(containers_list)

import signal
import sys

def signal_handler(sig, frame):
    # fechar os conatiners e remover todos ?


    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()