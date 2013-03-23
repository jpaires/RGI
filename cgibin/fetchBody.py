# -*- coding: utf-8 -*-
import sys, os

sys.path.append(os.getcwd())
import cgi
import logging
import socket
logging.basicConfig(level=logging.DEBUG)

form = cgi.FieldStorage()

print "Content-type: text/html; charset=utf-8\n";

idsToFetch = None
idsToFetch = form["idsToFetch"].value

if idsToFetch != None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 58001))
    sock.send("fetchBody" + idsToFetch)
    
    response = ""
    data = sock.recv(1024)
    while data:
        response += data
        data = sock.recv(1024)
    
    if(response.__len__() == 0):
        print ""
    else:
        print response
    sock.close()
else:
    print "!ERROR!"

