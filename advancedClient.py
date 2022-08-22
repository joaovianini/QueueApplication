import cmd, sys, enum, json
from operator import truediv
from twisted.internet import reactor, threads
from twisted.protocols.basic import LineReceiver
from twisted.internet.stdio import StandardIO
from twisted.internet.protocol import Protocol, connectionDone 
from twisted.internet.protocol import ClientFactory as CltFactory
from twisted.internet.endpoints import TCP4ClientEndpoint


class Client(Protocol):
    def __init__(self):
        StandardIO(LineProcessor(self))
        self.message = ''

    def dataReceived(self, data):
        data = data.decode("utf-8")
        ddata = json.loads(data)
        print(ddata["response"])

    def sendData(self):
        newmessage = self.message.encode('utf-8')
        self.transport.write(newmessage)
      
class ClientFactory(CltFactory):
    def __init__(self):
        super(ClientFactory,self).__init__()
        self.clientInstance = None
        
    def buildProtocol(self, address):
        proto = Client()
        self.clientInstance = proto
        return proto

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.')
        CltFactory.clientConnectionFailed(self,connector,reason)
        
    def clientConnectionLost(self, connector, reason):
        print('Connection lost.')
        CltFactory.clientConnectionLost(self,connector,reason)

class LineProcessor(LineReceiver,object):
    from os import linesep as delimiter
    
    def __init__(self,client):
        self.client = client
        self.processor = CallControl(client)
        self.setRawMode()

    def connectionMade(self):
        self.transport.write(''.encode('utf-8'))
        
    def dataReceived(self, data):
        self.processor.onecmd(data.decode('utf-8'))
        self.transport.write(''.encode('utf-8'))
        

class CallControl(cmd.Cmd):
    def __init__(self,client):
        super().__init__()
        self.client = client

    intro = 'This is a call center controller. Type help or ? to list commands.\n'

    def do_exit(self, arg):
        'Exit the Application'
        id = parse(arg)
        ddata = {
            "command": "exit",
            "id": id
        }
        data = json.dumps(ddata)
        self.client.message = data
        self.client.sendData()

    def do_createOperator(self,arg):
        'Creates an operator with an ID'
        id = parse(arg)
        ddata = {
            "command": "createOperator",
            "id": id
        }
        data = json.dumps(ddata)
        self.client.message = data
        self.client.sendData(data)

    def do_call(self, arg):
        'Makes the application receive a call with id <id>: call 7'
        id = parse(arg)
        ddata = {
            "command": "call",
            "id": id
        }
        data = json.dumps(ddata)
        self.client.message = data
        self.client.sendData()

    def do_answer(self,arg):
        'Makes operator <id> answer a call being delivered to them: answer B'
        id = parse(arg)
        ddata = {
            "command": "answer",
            "id": id
        }
        data = json.dumps(ddata)
        self.client.message = data
        self.client.sendData()

    def do_hangup(self,arg):
        'Terminates a call with id'
        id = parse(arg)
        ddata = {
            "command": "hangup",
            "id": id
        }
        data = json.dumps(ddata)
        self.client.message = data
        self.client.sendData()

    def do_reject(self,arg):
        'Rejects a call with Operator ID'
        id = parse(arg)
        ddata = {
            "command": "reject",
            "id": id
        }
        data = json.dumps(ddata)
        self.client.message = data
        self.client.sendData()

def parse(arg):
    'Convert input argument into a string'
    return str(arg)

if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 5678)
    endpoint.connect(ClientFactory())
    reactor.run()
