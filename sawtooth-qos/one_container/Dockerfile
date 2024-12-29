# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
# new image
# usar comando: sudo docker build --debug --tag 'qosblockchainv1' .

FROM hyperledger/sawtooth-rest-api:chime

# ADD file:4974bb5483c392fb54a35f3799802d623d14632747493dce5feb4d435634b4ac in /

RUN set -xe   && echo '#!/bin/sh' > /usr/sbin/policy-rc.d  && echo 'exit 101' >> /usr/sbin/policy-rc.d  && chmod +x /usr/sbin/policy-rc.d   && dpkg-divert --local --rename --add /sbin/initctl  && cp -a /usr/sbin/policy-rc.d /sbin/initctl  && sed -i 's/^exit.*/exit 0/' /sbin/initctl   && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup   && echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/docker-clean  && echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/docker-clean  && echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/docker-clean   && echo 'Acquire::Languages "none";' > /etc/apt/apt.conf.d/docker-no-languages   && echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/docker-gzip-indexes   && echo 'Apt::AutoRemove::SuggestsImportant "false";' > /etc/apt/apt.conf.d/docker-autoremove-suggests

RUN mkdir -p /run/systemd && echo 'docker' > /run/systemd/container

RUN apt-get update  && apt-get install gnupg -y

LABEL install-type=repo

RUN echo "deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe" >> /etc/apt/sources.list  && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD  || apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 8AA7AF1F1091A5FD)  && apt-get update
    
# instalar os pacotes importantes
RUN apt-get install -y -q sawtooth python3-sawtooth-sdk python3-sawtooth-rest-api python3-sawtooth-validator sawtooth-settings-tp sawtooth-pbft-engine sawtooth-devmode-engine-rust python3-sawtooth-poet-engine python3-sawtooth-poet-cli python3-sawtooth-poet-families && apt-get clean  && rm -rf /var/lib/apt/lists/*
# precisa installar esse tbm ? sawtooth SIM -> o validador utiliza varias ferramentas desse pacote (ex: sawtooth keygen)

EXPOSE 4004/tcp
EXPOSE 8008

# copiar TransactionProcess
COPY processor/ /processor/

WORKDIR /processor
# CMD ["sawtooth-rest-api"]

# para rodar o validador
# CMD ["sawtooth-validator" "-vv"]

# CMD ["settings-tp" "-vv"] # para rodar o settings

# CMD ["pbft-engine" "-C" "tcp://validator:5050"] # para rodar pbft consensus