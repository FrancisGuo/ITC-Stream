#ITCast
#This program is under the license of ?

#v0 started at 170516
#v0 ended at 170523
#v1 started at 170523
#v1 ended at 170524
#v2 started at 170525
#v2 ended at 170528
#v3 started at 170529
#v3 ended at 170615
#v4 started at 171129
#last modified at 171129

import socket
import struct
import os
import time

MP3Addr = []

#USER
FileNum = 3
MP3Addr.append('/home/demo.mp3')
#MP3Addr.append('')
#USER
Host = '192.168.1.1'#IP address of the server
TCPPort = 8000#Command port
UDPPort = 15001#Data port
#USER
user = 'user'#User
password = 'password'#Password of the user
#USER
playvol = 22#Volume of session
termsel = ',1,2,3'#Term of session/Fill as ",n,m"
#termsel = ',128,129,130,131,132,133'
#USER
LogAddr = '/home'
#USER
IsTest = False
GetInfo = False
#USER

file = b''
frame = []
framenum = 0

rbsize = 20000

sessionID = b'0'

def LocalMsg(Message):
    print('Local: '+Message)
    l.write('Local: '+Message+'\n')

def SMP3P(SMP3Addr):
    global file
    global frame
    global framenum
    f = open(SMP3Addr,'rb')
    file = f.read()
    bfframenum = framenum#framenum-bfframenum is the number of frame(s) of this file.
    LocalMsg('Single MP3 loaded.Total length is '+str(len(file))+'Byte(s).')
    LastFrameAddr = -2#+2 to find frame header.So the first val is -2
    BfLastFrameAddr = -1#-1 means find nothing the last finding.Not keep the same as following.LastFrameAddr-BfLastFrameAddr is the length of this frame.
    while 1 :
        LastFrameAddr = file.find(b'\xff\xfb',LastFrameAddr+2)#Skip the \xff\xfb and find the next.
        if LastFrameAddr == -1:#Only nothing can find.
            if BfLastFrameAddr != -1:#There is(are) something finded before this finding event.
                frame.append(file[BfLastFrameAddr:len(file)])#Copy the last frame.
                framenum = framenum+1#frame number counter
            break
        if BfLastFrameAddr != -1:#New frame header is finded.
            frame.append(file[BfLastFrameAddr:LastFrameAddr])#copy
            framenum = framenum+1#counter
        BfLastFrameAddr = LastFrameAddr#refresh the previous counter.
    LocalMsg('Single MP3 prosessing done.'+str(framenum-bfframenum)+'Frame(s) detected.')
    f.close()

def MP3P():
    global framenum
    framenum = 0
    for i in range(0,FileNum):
        LocalMsg('Loading MP3 file:'+str(MP3Addr[i])+' ('+str(i+1)+'/'+str(FileNum)+')')
        SMP3P(MP3Addr[i])
    LocalMsg(str(FileNum)+' of MP3 file(s) is(are) loaded.')

def ConMsg(Message):
    print('Connection: '+Message)
    l.write('Connection: '+Message+'\n')

def TCPInit():
    s.connect((Host,TCPPort))
    ConMsg('Socket connected.')

def TCPStage0():
    s.send(b'logon 0\t'+bytes(user,'utf-8')+b'\t'+bytes(password,'utf-8'))
    if s.recv(100) == b'000 0\n':
        ConMsg('Account logoned.')
    else:
        ConMsg('Logoning error')

def TCPStage1():
    #s.send(b'service stat')
    #print(s.recv(100))
    s.send(b'term list')
    t.sleep(0.5)
    TermL = s.recv(rbsize)
    ConMsg('Term:'+str(TermL,'gbk'))
    s.send(b'group list')
    t.sleep(0.5)
    GroupL = s.recv(rbsize)
    ConMsg('Group:'+str(GroupL,'gbk'))
    
def TCPStage2():
    global sessionID
    s.send(b'session new q\t65794\t400\t1')
    sessionIDSwap = s.recv(100)
    if sessionIDSwap[:4] == b'000 ':
        ConMsg('Session created.')
    else:
        ConMsg('Session creating error')
    sessionID = sessionIDSwap[4:-1]#session ID as bytes
    ConMsg('ID:'+str(sessionID,'utf-8'))
    
def TCPStageT():
    ConMsg('Term selected:'+termsel)
    s.send(b'session add_term '+sessionID+bytes(termsel,'utf-8'))
    if s.recv(100) == b'000 \n':
        ConMsg('Term added.')
    else:
        ConMsg('Term adding error')
        
def TCPStage3():
    s.send(b'session set '+sessionID+b'\tSTAT=1')
    if s.recv(100) == b'000 \n':
        ConMsg('Setted session state to 1.')
    else:
        ConMsg('Setting session state to 1 error')
    s.send(b'session get '+sessionID+b'\tSTAT')
    GetStateSwap = s.recv(100)
    if GetStateSwap == b'000 STAT=1\n':
        ConMsg('The state of session is at 1.')
    else:
        if GetStateSwap == b'000 STAT=0\n':
            ConMsg('The state of session is at 0.')
            ConMsg('Failed to set session state to 1')
        else:
            ConMsg('Getting state error')
            ConMsg('Failed to set session state to 1')

def TCPStageV():
    ConMsg('Set play volume:'+str(playvol))
    s.send(b'session playvol '+sessionID+b','+bytes(str(playvol),'utf-8')+b',')
    if s.recv(100) == b'000 \n':
        ConMsg('Play volume setted.')
    else:
        ConMsg('Play volume setting error')

def TCPStage4():
    s.send(b'session set '+sessionID+b'\tSTAT=0')
    if s.recv(100) == b'000 \n':
        ConMsg('Setted session state to 0.')
    else:
        ConMsg('Setting session state to 0 error')
    s.send(b'session get '+sessionID+b'\tSTAT')
    GetStateSwap = s.recv(100)
    if GetStateSwap == b'000 STAT=0\n':
        ConMsg('The state of session is at 0.')
    else:
        if GetStateSwap == b'000 STAT=1\n':
            ConMsg('The state of session is at 1.')
            ConMsg('Failed to set session state to 0')
        else:
            ConMsg('Getting state error')
            ConMsg('Failed to set session state to 0')
    s.send(b'session rm '+sessionID)
    if s.recv(100) == b'000 \n':
        ConMsg('Session removed.')
    else:
        ConMsg('Removing session error')

def TCPStage5():
    s.send(b'quit')
    if s.recv(100) == b'quit':
        ConMsg('Account quited.')
    else:
        ConMsg('Quitting account error')

def TCPStage6():
    s.close()
    ConMsg('Socket closed.')

def UDPStage():
    UsessionID = int(str(sessionID,'utf-8'))
    IDHeader = struct.pack('>i',UsessionID)
    ConMsg('UDP data transmitting start.')
    for UFrameID in range(0,framenum):
        IDFrame = struct.pack('>i',UFrameID)
        u.sendto(IDHeader+IDFrame+frame[UFrameID],(Host,UDPPort))
        t.sleep(0.02567)
    u.close()
    ConMsg('UDP data transmitting done.')

def RmAllSession():
    rangeL = 10000
    rangeH = 11010#number of ID is rangeH-rangeL+1
    TCPInit()
    TCPStage0()
    for RmID in range(rangeL,rangeH+1):
        s.send(b'session get '+bytes(str(RmID),'utf-8')+b'\tSTAT') 
        if s.recv(100) == b'000 STAT=1\n':
            ConMsg('The state of session is at 1.')
            ConMsg('Removing session:'+str(RmID))
            s.send(b'session rm '+bytes(str(RmID),'utf-8'))
            if s.recv(100) == b'000 \n':
                ConMsg('Session removed.')
            else:
                ConMsg('Removing session '+str(RmID)+' error')
                break
        if RmID == rangeH:
            ConMsg('Removing all session in range done.')
    TCPStage5()
    TCPStage6()

def Play(TestFlag,GetInfoFlag):
    try:
        MP3P()
    except:
        LocalMsg('Error:MP3 processing')
    else:
        try:
            TCPInit()
        except:
            ConMsg('Error:Network connection')
        else:
            try:
                TCPStage0()
                if GetInfoFlag == True:
                    TCPStage1()
            except:
                ConMsg('Error:Controling before creating session')
            else:
                try:
                    TCPStage2()
                except:
                    ConMsg('Error:Plying')
                else:
                    try:
                        TCPStageT()
                        TCPStage3()
                        TCPStageV()
                    except:
                        ConMsg('Error:Controling after creating session')
                    else:
                        if TestFlag == False:
                            try:
                                UDPStage()
                            except:
                                ConMsg('Error:Plying')
                            #else:
                            #finally:
                    #finally:
                finally:
                    TCPStage4()
            finally:
                TCPStage5()
        finally:
            TCPStage6()
    #finally:

if __name__ == '__main__':
    try:
        l = open(LogAddr,'a')
    except:
        print('Unable to access log files')
    else:
        try:
            t = time
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            u = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            LocalMsg('Start----------------')
            LocalMsg('GMT:'+t.strftime('%Y-%m-%d %X',t.gmtime(t.time())))
            if IsTest == True :
                LocalMsg('Test Mode')
            if GetInfo == True :
                LocalMsg('Get Term and Group info')
            #RmAllSession()
            Play(IsTest,GetInfo)
        except:
            LocalMsg('Error unknow')
        finally:
            LocalMsg('End------------------')
    finally:
        l.close()
