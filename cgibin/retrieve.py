# -*- coding: utf-8 -*-
import sys, os

sys.path.append(os.getcwd())
import cgi
import logging
import socket
logging.basicConfig(level=logging.DEBUG)

form = cgi.FieldStorage()

print "Content-type: text/html; charset=utf-8\n";

query = None
query = form["query"].value
ts_init = form["TS"].value
sorted_by = form["sortedBy"].value
sender_wanted = form["senderWanted"].value
subject_wanted = form["subjectWanted"].value
body_wanted = form["bodyWanted"].value

if query != None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 58001))
    query = sender_wanted + " " + subject_wanted + " " + body_wanted + " "+ query
    if sorted_by == "time":
        s = "queryTime " +query
        sock.send(s)
    elif sorted_by == "relevanceOTF":
        sock.send("queryOTF " +query)
    else:
        sock.send("query " +query)
    
    response = ""
    data = sock.recv(1024)
    while data:
        response += data
        data = sock.recv(1024)
    
    if(response.__len__() == 0):
        print ""
    else:
        print ts_init + " " + response
    sock.close()
else:
    print "!ERROR!"