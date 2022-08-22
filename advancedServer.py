import cmd, sys, queue, enum, json
from operator import truediv
from venv import create
from twisted.internet import reactor, protocol
from twisted.internet.protocol import Protocol, connectionDone
from twisted.internet.protocol import ServerFactory as ServFactory

class Server(Protocol):   
    def connectionMade(self):
        print("New connection")

    def dataReceived(self,data):
        print("Message Received")
        data = data.decode('utf-8')
        incomingMessage = json.loads(data)
        message = executeCommand(incomingMessage)
        serverResponse = json.dumps(message)
        self.transport.write(serverResponse.encode('utf-8'))

    def connectionLost(self, reason=connectionDone):
        print("A connection was lost.")
        
class ServerFactory(ServFactory):
    def buildProtocol(self, address):
        return Server()

reactor.listenTCP(5678,ServerFactory())
reactor.run()


class OperatorState(enum.Enum):
    AVAILABLE = 1
    RINGING = 2
    BUSY = 3

class CallStatus(enum.Enum):
    RINGING = 1
    ONGOING = 2
    FINISHED = 3
    REJECTED = 4
    MISSED = 5


calls = queue.Queue(maxsize=0)
callList = []

class Call:
    def __init__(self) -> None:
        pass
    def __init__(self, id):
        self.id = id
        self.status = CallStatus.RINGING


class Operator:
    call = Call
    def __init__(self) -> None:
        pass
    def __init__(self, id):
        self.id = id
        self.state = OperatorState.AVAILABLE
        self.operator = None

        
def addCallToQueue(call, queue):
        calls.put(call)
        print('Call ' + str(call.id) + ' waiting in queue ')

def answerCall(call,operator):
    call.status = CallStatus.ONGOING
    operator.state = OperatorState.BUSY
    print('Call ' + str(call.id) + ' answered by operator ' + str(operator.id))
    updateQueue(calls)
    
def ringCall(call,operator):
    call.status = CallStatus.RINGING
    operator.state = OperatorState.RINGING
    operator.call = call
    call.operator = operator
    for key in callList:
        if key.id == call.id:
            key.operator = operator
    print('Call ' + str(call.id) + ' ringing for operator ' + str(operator.id))


def rejectCall(call, operator):
    call.status = CallStatus.REJECTED
    operator.state = OperatorState.AVAILABLE
    response = 'Call ' + str(call.id) + ' rejected by operator ' + str(operator.id)
    return response

def finishCall(call, operator):
    call.status = CallStatus.FINISHED
    operator.state = OperatorState.AVAILABLE
    id = call.id
    response = 'Call ' + str(id) + ' finished and operator ' + str(operator.id) + ' available'
    return response

def missCall(call):
    call.status = CallStatus.MISSED
    response = 'Call ' + str(call.id) + ' missed'
    return response

def createCall(id):
    call = Call(id)
    response = 'Call ' + str(call.id) + ' received'
    callList.append(call)
    associateOperatorWithCall(call)
    return response

def updateQueue(q):
    if(q.empty()):
        return
    call = q.get()
    ringing = False
    for key in operators:
        if key.state == OperatorState.AVAILABLE and ringing == False:
            ringCall(call,key)
            ringing = True
    if ringing == False:
        q.queue.insert(0,call)

def associateOperatorWithCall(call):
    ringing = False
    for key in operators:
        if key.state == OperatorState.AVAILABLE and ringing == False:
            ringCall(call,key)
            ringing = True
    if ringing == False:
        addCallToQueue(call, calls)
        updateQueue(calls)
        
def findOperatorbyID(operatorID):
    for key in operators:
        if key.id == operatorID:
            return key

def findCallAndTerminate(callID):
    for key in operators:
        if key.call.id == callID:
            if key.call.status == CallStatus.ONGOING:
                response = finishCall(key.call, key)
                updateQueue(calls)
                return response
            elif key.call.status == CallStatus.RINGING:
                response = missCall(key.call)
                key.state = OperatorState.AVAILABLE
                updateQueue(calls)
                return response
        for key in iter(calls.get, None):
            if key.id == callID:
                response = missCall(key)
                return response
    return "Call not found."

def findCallAndReject(operatorID):
    for key in operators:
        if key.id == operatorID:
            response = rejectCall(key.call, key)
            calls.queue.insert(0,key.call)
    updateQueue(calls)
    return response
    
def addOperator(operatorID):
    op = Operator(operatorID)
    operators.append(op)


def executeCommand(message):
    #if message["command"] == "exit":
    #    response = exit(message["id"])
    if message["command"] == "createOperator":
        response = addOperator(message["id"])
    elif message["command"] == "call":
        response = createCall(int(message["id"]))
    elif message["command"] == "answer":
        operator = findOperatorbyID(message["id"])
        response = answerCall(operator.call,operator)
    elif message["command"] == "hangup":
        response = findCallAndTerminate(int(message["id"]))
    elif message["command"] == "reject":
        response = findCallAndReject(message["id"])
    message = {
        "response": message
        }
    return message

#for tests
operators = []

