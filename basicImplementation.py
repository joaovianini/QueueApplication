import cmd, sys, queue, enum
from operator import truediv
from venv import create

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
    print('Call ' + str(call.id) + ' rejected by operator ' + str(operator.id))

def finishCall(call, operator):
    call.status = CallStatus.FINISHED
    operator.state = OperatorState.AVAILABLE
    id = call.id
    print('Call ' + str(id) + ' finished and operator ' + str(operator.id) + ' available')

def missCall(call):
    call.status = CallStatus.MISSED
    print('Call ' + str(call.id) + ' missed')

def createCall(id):
    call = Call(id)
    print('Call ' + str(call.id) + ' received')
    callList.append(call)
    return call

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

#for tests
operators = []


class CallControl(cmd.Cmd):
    intro = 'This is a call center controller. Tupe help or ? to list commands.\n'
    prompt = '(queueApplication)'

    def do_exit(self, arg):
        'Exit the Application'
        exit(int(*parse(arg)))

    def do_createOperator(self,arg):
        'Creates an operator with an ID'
        op = Operator(*parse(arg))
        operators.append(op)

    def do_call(self, arg):
        'Makes the application receive a call with id <id>: call 7'
        try:	
            id = int(parse(arg))
        except:
            print("Only integers are allowed as call IDs")
            updateQueue(calls)
            return
        call = createCall(id)
        ringing = False
        for key in operators:
            if key.state == OperatorState.AVAILABLE and ringing == False:
                ringCall(call,key)
                ringing = True
        if ringing == False:
            addCallToQueue(call, calls)
        updateQueue(calls)

    def do_answer(self,arg):
        'Makes operator <id> answer a call being delivered to them: answer B'
        operatorID = parse(arg)
        for key in operators:
            if key.id == operatorID:
                answerCall(key.call,key)
        updateQueue(calls)

    def do_hangup(self,arg):
        'Terminates a call with id'
        try:	
            callID = int(parse(arg))
        except:
            print("Only integers are allowed as call IDs")
            updateQueue(calls)
            return
        for key in operators:
            if key.call.id == callID:
                if key.call.status == CallStatus.ONGOING:
                    finishCall(key.call, key)
                    updateQueue(calls)
                    return
                elif key.call.status == CallStatus.RINGING:
                    missCall(key.call)
                    key.state = OperatorState.AVAILABLE
                    updateQueue(calls)
                    return
        for key in iter(calls.get, None):
            if key.id == callID:
                missCall(key)
                return

    def do_reject(self,arg):
        'Rejects a call with ID'
        operatorID = parse(arg)
        for key in operators:
            if key.id == operatorID:
                rejectCall(key.call, key)
                calls.queue.insert(0,key.call)
        updateQueue(calls)
                
def parse(arg):
    'Convert input argument into a string'
    return str(arg)

if __name__ == '__main__':
    CallControl().cmdloop()
