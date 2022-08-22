import cmd, sys, queue, enum, json
from operator import truediv
from twisted.internet import reactor, threads
from twisted.internet.protocol import Protocol, connectionDone 
from twisted.internet.protocol import ReconnectingClientFactory as CltFactory
from twisted.protocols.basic import LineReceiver

class Client(LineReceiver):
    def __init__(self):
        reactor.callInThread(CallControl(self).cmdloop())

    def connectionMade(self):
        pass
    
    def dataReceived(self, data):
        data = data.decode("utf-8")
        ddata = json.loads(data)
        sys.stdout.write(ddata["response"])

    def sendData(self,message):
        self.sendLine(message.encode("utf-8"))
    
        
class ClientFactory(CltFactory):
    def __init__(self):
        self.connectedProtocol = None
        
    def buildProtocol(self, address):
        proto = Client()
        self.connectedProtocol = proto
        return proto

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.')
        CltFactory.clientConnectionFailed(self,connector,reason)
        
    def clientConnectionLost(self, connector, reason):
        print('Connection lost.')
        CltFactory.clientConnectionLost(self,connector,reason)

class CallControl(cmd.Cmd):
    def __init__(self,client):
        self.client = client
        super(CallControl,self).__init__()
        print(type(client))
    
    intro = 'This is a call center controller. Type help or ? to list commands.\n'

    def do_exit(self, arg):
        'Exit the Application'
        id = parse(arg)
        ddata = {
            "command": "exit",
            "id": id
        }
        data = json.dumps(ddata)
        reactor.callFromThread(self.client.sendData(data))

    def do_createOperator(self,arg):
        'Creates an operator with an ID'
        id = parse(arg)
        ddata = {
            "command": "createOperator",
            "id": id
        }
        data = json.dumps(ddata)
        reactor.callFromThread(self.client.sendData(data))
        

    def do_call(self, arg):
        'Makes the application receive a call with id <id>: call 7'
        id = parse(arg)
        ddata = {
            "command": "call",
            "id": id
        }
        data = json.dumps(ddata)
        reactor.callFromThread(self.client.sendData(data))

    def do_answer(self,arg):
        'Makes operator <id> answer a call being delivered to them: answer B'
        id = parse(arg)
        ddata = {
            "command": "answer",
            "id": id
        }
        data = json.dumps(ddata)
        reactor.callFromThread(self.client.sendData(data))
        
    def do_hangup(self,arg):
        'Terminates a call with id'
        id = parse(arg)
        ddata = {
            "command": "hangup",
            "id": id
        }
        data = json.dumps(ddata)
        reactor.callFromThread(self.client.sendData(data))
        
    def do_reject(self,arg):
        'Rejects a call with Operator ID'
        id = parse(arg)
        ddata = {
            "command": "reject",
            "id": id
        }
        data = json.dumps(ddata)
        reactor.callFromThread(self.client.sendData(data))
      
def parse(arg):
    'Convert input argument into a string'
    return str(arg)

if __name__ == '__main__':
    myFactory = ClientFactory()
    reactor.connectTCP('localhost', 5678, myFactory)
    reactor.run()
