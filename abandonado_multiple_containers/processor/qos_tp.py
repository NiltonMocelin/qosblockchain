## reff: https://sawtooth.splinter.dev/docs/1.2/app_developers_guide/python_sdk.html
## PBFT consensus requires a network with at least four nodes. A network with fewer than four nodes will fail.
## https://www.youtube.com/watch?v=4VUaZkwJdCc&ab_channel=DanAnderson


### boa ref: https://blog.logrocket.com/hyperledger-sawtooth-introduction/
### https://github.com/rosdec/single/blob/master/processor/handler.js

### ref das melhores: https://sawtooth.splinter.dev/docs/1.2/sysadmin_guide/setting_up_sawtooth_network.html

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
'''
Transaction family class for qosblockchain.
'''

import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = "qosblockchain"

def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()

# Prefix for simplewallet is the first six hex digits of SHA-512(TF name).
sw_namespace = _hash(FAMILY_NAME.encode('utf-8'))[0:6]

class QoSRegTransactionHandler(TransactionHandler):
    '''                                                       
    Transaction Processor class for the qosreg transaction family.       
                                                              
    This with the validator using the accept/get/set functions.
    It implements functions to flowstart, fred, registerqos, retriveqos, and checkqos, flowend.
    '''

    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for this transaction handler.
                                                              
           This function does most of the work for this class.
        '''                                                
        
        # Get the payload and extract simplewallet-specific information.
        header = transaction.header
        payload_list = transaction.payload.decode().split(",")
        operation = payload_list[0]
        amount = payload_list[1] #json ?

        # Get the public key sent from the client.
        from_key = header.signer_public_key

        # Perform the operation.
        LOGGER.info("Operation = "+ operation)


        ### inserir o volume de dados trocados durante o subfluxo pode vir a ser útil tbm


        if operation == "flowstart":
            self._make_deposit(context, amount, from_key)
        elif operation == "regfred":
            self._make_withdraw(context, amount, from_key)
        elif operation == "registerqos":
            if len(payload_list) == 3:
                to_key = payload_list[2]
            self._make_transfer(context, amount, to_key, from_key)
        elif operation == "checkqos":
            if len(payload_list) == 3:
                to_key = payload_list[2]
            self._make_transfer(context, amount, to_key, from_key)
        elif operation == "flowend":
            if len(payload_list) == 3:
                to_key = payload_list[2]
            self._make_transfer(context, amount, to_key, from_key)
        else:
            LOGGER.info("Unhandled action. " +
                "Operation should be deposit, withdraw or transfer")

    def _flow_start(self, context, fred, ipv6_origem, ipv6_destino, as_requisitante):
        """Registrar o inicio de um fluxo, usando o FRED e o id de uma entidade"""

        host_address = self._get_hostreg_address(ipv6_origem)
        LOGGER.info('Got the key {} and the wallet address {} '.format(
            ipv6_origem, host_address))
        
        current_entry = context.get_state([host_address])

        if current_entry == []:
            LOGGER.info('No previous reg, creating new deposit {} '
                .format(ipv6_origem))

        state_data = str(fred).encode('utf-8')
        addresses = context.set_state({host_address: state_data})

        if len(addresses) < 1:
            raise InternalError("State Error")

        return 

    def _reg_fred(self, context, fred):
        """Registrar o FRED calculado por uma entidade por um fluxo"""
        return
    
    def _reg_qos(self, context, qos):
        """Registrar o QoS calculado por uma entidade para um fluxo"""
        return
    
    def _check_qos(self, context):
        """Obtém os últimos registros de QOS enviados pelas entidades"""
        return
    
    def _flow_end(self, context, fred):
        """Uma entidade define que um fluxo encerrou"""
        return

    def _flow_resume(self, context, fred):
        """Uma entidade define que um fluxo vai continua com o mesmo QoS"""
        return
    
    def _get_hostreg_address(self, from_key):
        return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:64]


    def _make_deposit(self, context, amount, from_key):
        wallet_address = self._get_wallet_address(from_key)
        LOGGER.info('Got the key {} and the wallet address {} '.format(
            from_key, wallet_address))
        current_entry = context.get_state([wallet_address])
        new_balance = 0

        if current_entry == []:
            LOGGER.info('No previous deposits, creating new deposit {} '
                .format(from_key))
            new_balance = int(amount)
        else:
            balance = int(current_entry[0].data)
            new_balance = int(amount) + int(balance)

        state_data = str(new_balance).encode('utf-8')
        addresses = context.set_state({wallet_address: state_data})

        if len(addresses) < 1:
            raise InternalError("State Error")

    def _make_withdraw(self, context, amount, from_key):
        wallet_address = self._get_wallet_address(from_key)
        LOGGER.info('Got the key {} and the wallet address {} '.format(
            from_key, wallet_address))
        current_entry = context.get_state([wallet_address])
        new_balance = 0

        if current_entry == []:
            LOGGER.info('No user with the key {} '.format(from_key))
        else:
            balance = int(current_entry[0].data)
            if balance < int(amount):
                raise InvalidTransaction('Not enough money. The amount ' +
                    'should be lesser or equal to {} '.format(balance))
            else:
                new_balance = balance - int(amount)

        LOGGER.info('Withdrawing {} '.format(amount))
        state_data = str(new_balance).encode('utf-8')
        addresses = context.set_state(
            {self._get_wallet_address(from_key): state_data})

        if len(addresses) < 1:
            raise InternalError("State Error")

    def _make_transfer(self, context, transfer_amount, to_key, from_key):
        transfer_amount = int(transfer_amount)
        if transfer_amount <= 0:
            raise InvalidTransaction("The amount cannot be <= 0")

        wallet_address = self._get_wallet_address(from_key)
        wallet_to_address = self._get_wallet_address(to_key)
        LOGGER.info('Got the from key {} and the from wallet address {} '.format(
            from_key, wallet_address))
        LOGGER.info('Got the to key {} and the to wallet address {} '.format(
            to_key, wallet_to_address))
        current_entry = context.get_state([wallet_address])
        current_entry_to = context.get_state([wallet_to_address])
        new_balance = 0

        if current_entry == []:
            LOGGER.info('No user (debtor) with the key {} '.format(from_key))
        if current_entry_to == []:
            LOGGER.info('No user (creditor) with the key {} '.format(to_key))

        balance = int(current_entry[0].data)
        balance_to = int(current_entry_to[0].data)
        if balance < transfer_amount:
            raise InvalidTransaction('Not enough money. ' +
                'The amount should be less or equal to {} '.format(balance))
        else:
            LOGGER.info("Debiting balance with {}".format(transfer_amount))
            update_debtor_balance = balance - int(transfer_amount)
            state_data = str(update_debtor_balance).encode('utf-8')
            context.set_state({wallet_address: state_data})
            update_beneficiary_balance = balance_to + int(transfer_amount)
            state_data = str(update_beneficiary_balance).encode('utf-8')
            context.set_state({wallet_to_address: state_data})

    def _get_wallet_address(self, from_key):
        return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:64]

def setup_loggers():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

def main():
    '''Entry-point function for the simplewallet transaction processor.'''
    setup_loggers()
    try:
        # Register the transaction handler and start it.
        processor = TransactionProcessor(url='tcp://validator:4004')

        handler = SimpleWalletTransactionHandler(sw_namespace)

        processor.add_handler(handler)

        processor.start()

    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

