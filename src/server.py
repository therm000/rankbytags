#!/usr/bin/python

from nmd import NMD
from SEChatBot import SEChatBot

from socket import *
myHost = '192.168.67.191'
myPort = 2005

s = socket(AF_INET, SOCK_STREAM)    # create a TCP socket
s.bind((myHost, myPort))            # bind it to the server port
s.listen(5)                         # allow 5 simultaneous
                                    # pending connections
                                    
proxy = {'192.168.254.254':80}
nmd = NMD(proxy)    
bot = SEChatBot(nmd)

while 1:
    # wait for next client to connect
    connection, address = s.accept() # connection is a new socket
    while 1:
        data = connection.recv(1024) # receive up to 1K bytes
        if data:
            connection.send(bot.input(data.strip()) + '\n')
            if data.strip() == 'bye':
                break
        else:
            break
    connection.close()              # close socket
