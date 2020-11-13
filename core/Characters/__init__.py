import random, time
import json
random.seed(time.time())
from core.Errors import *
from core.Colors import bcolors as css
import base64
from functools import reduce
import socket

tips=[
    "one number is correct and well placed",
    "nothing is correct",
    'two numbers are correct but wrong placed',
    'one number is correct but wrong placed',
    'one number is correct but wrong placed'
]

sequences=[[], [], [], [], []]

numbers=[i for i in range(0,10)]

def list_splice(target, start, delete_count=None, *items):
    if delete_count == None:
        delete_count = len(target) - start

    # store removed range in a separate list and replace with *items
    total = start + delete_count
    removed = target[start:total]
    target[start:total] = items

    return removed

def shuffle(matrix):
    for i in range(0, len(matrix)-1):
        j=int(random.random()*(i+1))
        x=matrix[i]
        matrix[i]=matrix[j]
        matrix[j]=x
    return matrix

def spliceRandNumber(array=None):
    if not array:
        array=numbers
    return (list_splice(array,int(random.random()*len(array)), 1))[0]

def newCode():
    global sequences
    code=[None,None,None]
    sequences=[[], [], [], [], []]
    codeNumbers=[spliceRandNumber() for _ in range(3)]

    sequences[0] = [codeNumbers[0], spliceRandNumber(), spliceRandNumber()]
    sequences[1] = [sequences[0][1], spliceRandNumber(), spliceRandNumber()]
    sequences[2] = [codeNumbers[1], codeNumbers[2], sequences[1][1]]
    sequences[3] = [codeNumbers[0], sequences[1][2], spliceRandNumber()]
    fifthSequenceNId = int(random.random()*2)+1
    sequences[4] = [codeNumbers[fifthSequenceNId], spliceRandNumber(), spliceRandNumber()]

    for s in sequences:
        s=shuffle(s)

    places = [sequences[0].index(codeNumbers[0]),None,None]
    
    code[places[0]] = codeNumbers[0]
    
    for i in range(0,3):
        if not code[i]:
            if not codeNumbers[1] in code: # code.index(codeNumbers[1]) < 0:
                code[i] = codeNumbers[1]
                places[1]=i
            else:
                code[i] = codeNumbers[2]
                places[2]=i

    fixThirdSequence(codeNumbers, places)
    fixFourthSequence(codeNumbers, places)
    fixFifthSequence(fifthSequenceNId, codeNumbers, places)

    i=0
    for s in sequences:
        print(s, tips[i])
        i+=1
    
    return code

#fix last sequences
def fixThirdSequence(codeNumbers, places):
    global sequences
    index1=sequences[2].index(codeNumbers[1])
    index2=sequences[2].index(codeNumbers[2])
    if not index1==places[1] and not index2==places[2]: return
    sequences[2][index1] = codeNumbers[2]
    sequences[2][index2] = codeNumbers[1]

def fixFourthSequence(codeNumbers,places):
    global sequences
    index=sequences[3].index(codeNumbers[0])
    for i in range(0,3):
        if not sequences[3][i]==codeNumbers[0] and sequences[3][i] in sequences[3]:
            sequences[3][i]=random.choice(sequences[1])
    if not index==places[0]: return
    if index>1:
        change=sequences[3][index-1]
        sequences[3][index - 1] = codeNumbers[0]
        sequences[3][index] = change
    else:
        change = sequences[3][index + 1]
        sequences[3][index + 1] = codeNumbers[0]
        sequences[3][index] = change

def fixFifthSequence(nId, codeNumbers, places):
    index=sequences[4].index(codeNumbers[nId])
    seqTwoIndex = sequences[2].index(codeNumbers[nId])
    if (index==places[nId] or type(index)==type(places[nId])) or (seqTwoIndex==index or type(seqTwoIndex)==type(index)):
        newIndex= reduce(lambda acc, cur: acc+([cur if not cur==seqTwoIndex and not cur==places[nId] else 0][0]), [0,1,2], 0)
        change= sequences[4][newIndex]
        sequences[4][newIndex] = codeNumbers[nId]
        sequences[4][index]= change

class Kernel():
    def __init__(self):
        self.islocked=True
        self.is_active=True
        self.ports={'80':1, '443':1}
        self.hashes={}
        [self.hashes.update({port:base64.b64encode(''.join([chr(random.randint(97,122)) for _ in range(5)]).encode()).decode()}) for port in self.ports.keys()]

class Robot():
    def __init__(self, cols:int, rows:int, Engine, image='R'):
        self.hp=100
        self.dict_pos={'x':random.randint(0,rows-1),'y':random.randint(0,cols-1)}
        self.pos=list(self.dict_pos.values())
        self.image=image
        self.commands=json.loads(open('core/Characters/cmds.json').read())['commands']
        self.id=str(random.randint(0,100))
        self.level=1
        self.state=css.FAIL+'locked'+css.ENDC
        # ---
        self.kernel=Kernel()
        self.Engine=Engine
    
    def move(self, pos:dict): raise NotImplementedError

    def parser(self, cmd):
        _cmd=cmd.split()[0].lower()
        params=cmd.split()[1:]
        if '-h' in params:
            self.docs(_cmd)
            return
        #params=[arg.casefold() for arg in params]
        # se _cmd necessita di più parametri ritorna subito un errore
        if (_cmd in ['hack']) and len(params)<=0:
            print(css.FAIL+'[ERR]'+css.ENDC+' Some parameters are missing.'); return
        if not _cmd in self.commands and cmd in self.Engine.shop_support.tools['1']: print(css.OKCYAN+'[SHOP]'+css.ENDC+css.FAIL+'[ERR]'+css.ENDC+' Per usare questo comando devi prima comprarlo.'); return
        if not _cmd in self.commands:
            raise CommandError(cmd)
        else:
            if _cmd=='hack':
                #print(self.kernel.__dict__, params, sep='--')
                if self.kernel.ports[params[0]]==1:
                    raise HackError()
                else:
                    print(css.OKCYAN+'[..]'+css.ENDC+' Hacking on port:',params[0])
                    self.kernel.islocked=False
                    self.state=css.OKGREEN+'unlocked'+css.ENDC
                    time.sleep(0.5)
                    print(css.OKCYAN+'[*]'+css.ENDC+css.OKGREEN+' Successfully hacked.'+css.ENDC)
            elif _cmd=='help':
                print(css.HEADER+'[H]'+css.ENDC+' List of commands:'); [print('-',cmd) for cmd in self.commands]
                print(css.HEADER+'[H]'+css.ENDC+' Type "cmd -h" for info about cmd.')
            elif _cmd=='scan':
                print(css.OKCYAN+'[..]'+css.ENDC+' Scanning...')
                print('[*] Found ports:')
                for port in self.kernel.ports.keys():
                    if self.kernel.ports[port] in ['1',1]:
                        print('-',css.HEADER+port,css.ENDC+' status:'+css.FAIL,self.kernel.ports[port],css.ENDC)
                    else:
                        print('-',port,' status:'+css.OKGREEN,self.kernel.ports[port], css.ENDC)
            elif _cmd in ['destroy', 'shutdown']:
                if self.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
                print(css.FAIL+'[..]'+css.ENDC+' Self-Destruction Enabled..')
                self.kernel.is_active=False
                self.Engine.robots.remove(self)
                time.sleep(0.4)
                self.Engine.gamepoints+=1
                print(css.HEADER+'[*]'+css.ENDC+' Bot killed.')
            elif _cmd=='bshell':
                if self.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
                if self.kernel.is_active: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Disable kernel first.'); return
                print(css.OKGREEN+'[CMD]'+css.ENDC+' Entering BrainShell...')
                if self.level<=1:
                    print(css.FAIL+'[ERR][#51]'+' BShell unreacheable, this robot hasnt a BShell interface.')
                else:
                    if len(params):
                        self.BShell(' '.join(params))
                    else:
                        self.Engine.inbshell=True
            elif _cmd=='info':
                [print(k,'->',self.kernel.__dict__[k]) for k in self.kernel.__dict__ if not k.startswith('__')]
            elif _cmd=='crack':
                if '-port' in params:
                    p=params[params.index('-port')+1]
                else:
                    p=params[0]
                if self.kernel.islocked: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Unlock kernel first.'); return
                if not self.kernel.is_active: raise HackError(css.OKCYAN+'\n[INFO]'+css.ENDC+' Kernel already disabled.'); return
                # resolve pattern
                print(css.HEADER+'[PATTERN]'+css.ENDC+' Resolve:')
                code=newCode()
                print(css.OKCYAN+'[INFO]'+css.ENDC+' Code: XXX')
                rep=input(css.OKBLUE+'[SOLUTION]'+css.ENDC+' >> ')
                if rep==''.join([str(i) for i in code]):
                    self.kernel.is_active=False
                    print(css.OKGREEN+'[OK]'+css.ENDC+css.OKCYAN+' Kernel Successfully disabled!'+css.ENDC)
                else:
                    print(css.FAIL+'[ERR]'+css.ENDC+' Verification Failed.')
            elif _cmd=='hash':
                if not len(params): params.append('-port')
                if params[0]=='-port':
                    # show mode, mostra la cifratura della porta
                    try:
                        print(css.OKCYAN+'[HASH]'+css.ENDC,params[1],self.kernel.hashes[str(params[1])])
                    except Exception:
                        [print(css.OKCYAN+'[HASH]'+css.ENDC,key,self.kernel.hashes[key]) for key in self.kernel.hashes.keys()]
                elif params[0]=='-res':
                    # map commands like: {param:val}
                    mappedparams={}
                    ncmd=cmd.lower().split()[1:]
                    for p in ncmd:
                        if not p.startswith('-'): continue
                        try:
                            mappedparams.update({p:ncmd[ncmd.index(p)+1]})
                        except: break
                    if mappedparams['-res']==base64.b64decode(self.kernel.hashes[mappedparams['-port']]).decode():
                        self.kernel.ports[mappedparams['-port']]=0
                        print(css.HEADER+'[*]'+css.ENDC+' Port {p} Successfully bypassed.'.format(p=mappedparams['-port']))
                    else:
                        print(css.FAIL+'[!!] Failed.'+css.ENDC)
                else:
                    print(css.WARNING+'[WARN]'+' Unrecognized param {p}, using "-port" instead.'.format(p=params[0]))
                    try:
                        print(css.OKGREEN+'[HASH]'+css.ENDC,params[1],self.kernel.hashes[str(params[1])])
                    except Exception:
                        [print(css.OKGREEN+'[HASH]'+css.ENDC,key,self.kernel.hashes[key]) for key in self.kernel.hashes.keys()]
            elif _cmd in ['translater', 'encoder', 'decoder']:
                if _cmd=='encoder':
                    s=params[params.index('-text')+1]
                    print(css.HEADER+'[*]'+css.ENDC+' Encoded text: '+css.OKBLUE, base64.b64encode(s).decode(),css.ENDC)
                elif _cmd=='decoder':
                    s=params[params.index('-text')+1]
                    print(css.HEADER+'[*]'+css.ENDC+' Decoded text: '+css.OKBLUE, base64.b64decode(s).decode(),css.ENDC)
                elif _cmd=='translater':
                    if not '-mode' in params:
                        if 'encode' in params or 'decode' in params:
                            if 'encode' in params:
                                s=params[params.index('-text')+1]
                                print(css.HEADER+'[*]'+css.ENDC+' Encoded text: ', base64.b64encode(s).decode())
                            else:
                                s=params[params.index('-text')+1]
                                print(css.HEADER+'[*]'+css.ENDC+' Decoded text: ', base64.b64decode(s).decode())
            elif _cmd == 'exit':
                self.Engine.selected=None
    
    def docs(self, man):
        data=json.loads(open('core/Characters/cmds.json').read())
        for key in data['cheatsheet'][man]:
            print(key,'->',data['cheatsheet'][man][key])

class Player(Robot):
    def __init__(self, cols:int, rows:int, Engine, image='P'):
        color=Engine.pickColor()[0]
        super().__init__(cols, rows, Engine, color+image+css.ENDC)
        self.x=int(self.pos[0])
        self.y=int(self.pos[1])
    
    def connect(self, address):
        ip=address.split(':')[0]
        port=int(address.split(':')[1])
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,port))
        self.s=s
    
    def loop(self):
        self.s.send('ciao'.encode())
        print(self.s.recv(1024).decode())
        # aggiorna la mappa ed esegui i comandi ricevuti se ce ne sono

    def parser(self, x):
        cmd=x.split()[0].lower()
        params=x.split()[1:]
        commands=['move']
        if not cmd in commands:
            print('[ERR] Unknown command.'); return
        print(cmd)

class Level2Robot(Robot):
    def __init__(self, cols:int, rows:int, Engine, image='M'):
        super().__init__(cols, rows, Engine, image)
        self.level=2
    
    def parser(self, x):
        super().parser(x)
    
    def BShell(self, x=None):
        comms=json.loads(open('core/Characters/cmds.json').read())['bscommands']
        cmd=x.split()[0].lower()
        params=x.split()[1:]
        if not cmd in comms:
            if cmd=='bshell' or not cmd:
                # start a serial communication
                self.Engine.inbshell=True
                if params[0] in comms:
                    cmd=params[0]
                    params.remove(params[0])
                else: return
            else:
                print(css.FAIL+'[ERR]'+css.ENDC+' Unrecognized command:', cmd)
                return
        # exec live commands
        if cmd=='move':
            if '-pos' in params:
                self.move(params[params.index('-pos')+1])
            else:
                self.move(params[0])
        if cmd in ['bye', 'exit']:
            self.Engine.inbshell=False
    
    def move(self, pos):
        newx=int(pos.split(',')[0]); x=self.pos[0]
        newy=int(pos.split(',')[1]); y=self.pos[1]
        skip=None
        if x in [0,5]:
            if newx>x:
                if x==4:
                    skip='x'
            else:
                if x==0:
                    skip='x'
        if y in [0,4]:
            if newy>y:
                if y==3:
                    skip='y'
            else:
                if y==0:
                    skip='y'
        if not skip:
            self.pos=[newx, newy]
        else:
            if skip=='y':
                self.pos=[newx, y]
            else:
                self.pos=[x, newy]        
