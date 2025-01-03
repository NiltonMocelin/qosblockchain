
import json

class EndPairQoS: ## IDEIA: apenas registrar QoS quando perceber mudança significativa de classe ou qos de um fluxo
    def __init__(self, endpair_name:str, ip_src:str):
        # interpretando o XO game (jogo da velha)
        # Isso representa o estado atual do fluxo, ou seja, o resultado das ações informadas nos blocos ( lá cada transação era um movimento e aqui se montava o tabuleiro, o estado do jogo e os jogadores)
        self.endpair_name:str = endpair_name
        self.ip_src:str = ip_src
        self.ip_dst:str = ''
        self.ip_ver:str = ''

        self.flows: list[Flow] = [] # lista de fluxos de um par

    def addFlow(self, flow):
        self.flows.append(flow)
        return True
    
    def remFlow(self, name):
        for f in self.flows:
            if f.name == name:
                self.flows.remove(f)
                return True
        return False
    
    def toString(self):

        #####        
        flows_json_str = ""
        for flow in self.flows:
            flows_json_str+= ',' + flow.toString()
        flows_json_str = flows_json_str.replace(',','',1)# tem outros jeitos, depois mudar
        #####

        json_result = "{\"endpair_name\":\"%s\",\
            \"ip_ver\":\"%s\",\
            \"ip_src\":\"%s\",\
            \"ip_dst\":\"%s\",\
            \"flows\":[%s]\
        }" % (self.endpair_name, self.ip_ver, self.ip_src, self.ip_dst, flows_json_str)

        return json_result
    
    def fromJSON(self, endpair_qos_json):
        return
        

class Flow:
    # dissecar o FRED aqui
    def __init__(self, src_port:str):
        self.name:str = ''
        self.src_port:str = src_port
        self.dst_port:str = ''
        self.proto:str=''
        self.as_duration:list[:str] = ['AS1001:50s'] # duração que cada AS participou do fluxo
        self.as_list:list[:str] = ['AS1001', 'AS1002'] #text/public key ...
        self.duration:list[:str] = ['50s']
        self.qoss: list[QoS] = [] # class QoS # lista de registros de qos para um fluxo
        self.state:str = 'Going' #Going, Stoped
        self.freds:list[Fred] = [] #caso existam freds diferentes, serão armazenados aqui

    def toString(self):

        ####
        freds_json_str = ""
        for fred in self.freds:
            freds_json_str+= ',' + fred.toString()
        freds_json_str= freds_json_str.replace(',','',1)# tem outros jeitos, depois mudar
        ####

        ####
        qos_json_str = ""
        for qos in self.qoss:
            qos_json_str+= ',' + qos.toString()
        qos_json_str = qos_json_str.replace(',','',1)# tem outros jeitos, depois mudar
        ####

        flow_json = "{\"name\":\"%s\",\
            \"state\":\"%s\",\
            \"src_port\":\"%s\",\
            \"dst_port\":\"%s\",\
            \"proto\":\"%s\",\
            \"qos\":[%s],\
            \"freds\":[%s]}" % (self.name, self.state, self.src_port, self.dst_port, self.proto, qos_json_str, freds_json_str)
        
        return flow_json

# organizar isso depois, pois o fred já possui muitas das informacoes do Flow (menos a parte das métricas de QoS)
class Fred:
    def __init__(self, nao_sei:str):
        self.nao_sei:str = nao_sei
    
    def toString(self):
        fred_json = "{\
        \"nao_sei\":\"%s\"}" % (self.nao_sei)

        return fred_json

class QoS:
    #medida de QoS
    def __init__(self, bandwidth:str):
        self.node:str = 'a' #nó que calculou
        self.bandwidth:str = bandwidth

    def toString(self):
        qos_json = "{\
        \"bandwidth\":\"%s\"\
        }" % (self.bandwidth)

        return qos_json

class QoSState:

    TIMEOUT = 3

    def _deserialize(self, data):
        """Take bytes stored in state and deserialize them into Python
        Game objects.

        Args:
            data (bytes): The UTF-8 encoded string stored in state.

        Returns:
            (dict): game name (str) keys, Game values.
        """

        endpair_qos_hist = None
        try:
            for endpair_qos in data.decode(): # precisa ver primeiro como vai ficar isso em json ... deixar para depois
                name, board, state, player1, player2 = endpair_qos.split(",")

                endpair_qos_hist[name] = EndPairQoS(name, board, state, player1, player2)
        except:
            print("Failed to deserialize game data")

        return endpair_qos_hist

    def _serialize(self, endpair_qos_hist):
        """Takes a dict of game objects and serializes them into bytes.

        Args:
            games (dict): game name (str) keys, Game values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        # duvida: usar json ou usar pickle?
        # a principio, json

        endpair_qos_hist_json = json.dumps(endpair_qos_hist.__dict__)
        print(endpair_qos_hist_json)
        
        return endpair_qos_hist_json.encode()


pairqos1 = EndPairQoS('0.0.0.0_1.1.1.1', '0.0.0.0')

flow1 = Flow(src_port='5500')
flow1.qoss.append(QoS('5Mbps'))
flow1.freds.append(Fred('teste'))
pairqos1.flows.append(flow1)

print(pairqos1.toString())

pairqos1_json =json.loads(pairqos1.toString()) 
# print( pairqos1_json )
print("------------------")
print(pairqos1_json['endpair_name'])

