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
# -----------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class QoSPayload:

    def __init__(self, payload):
        try:
            # The payload is csv utf-8 encoded string
            
            # pensar nas informacoes a serem armazenadas
            #goal_classe, goal_app, goal_service, goal_bandwidth, goal_latency, 
            #
            action, flow_str = payload.decode().split(',')

        except ValueError as e:
            raise InvalidTransaction("Invalid payload serialization") from e

        if not action:
            raise InvalidTransaction('Action is required')

        if (action == 'reg_qos' or action == 'del_qos') and not flow_str:
            raise InvalidTransaction('Flow is required')

        if action == '':

            try:
                print('a')
            except ValueError:
                raise InvalidTransaction('Error') from ValueError

        self._action = action
        self._flow_str = flow_str
        
    @staticmethod
    def from_bytes(payload):
        return QoSPayload(payload=payload)

    @property
    def action(self):
        return self._action
    @property
    def flow_str(self):
        return self._flow_str