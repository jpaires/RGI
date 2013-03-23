# -*- coding: utf-8 -*-

import CGIHTTPServer
import BaseHTTPServer
import SocketServer
from services import automaticIndexer
from services.utils import Retriever
import services
import time
from threading import Thread

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
    cgi_directories = ["/cgibin"]

##################################################################################################

class RGIServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): pass

##################################################################################################

class RetrievalThread(Thread):
    
    def run(self):
        time.sleep(1)
        rs = RetrievalServer(('',58001), RetrievalRequestHandler)
        rs.start_indexing_thread()
        rs.serve_forever()

def create_retrieval_thread():
    RetrievalThread().start()


class RetrievalRequestHandler(SocketServer.BaseRequestHandler):
    
    def handleQuery(self, query, time_sorted = False, on_the_fly = False):
        if query != None:
            splitted = query.split(" ", 3)
            query = splitted[3]
            sender_wanted = splitted[0] == "true"
            subject_wanted = splitted[1] == "true"
            body_wanted = splitted[2] == "true"
            
            basicTerms, includingTerms, excludingTerms = services.tokenizer.TokenizeInput(query)
            
            
            
            results = self.server.retriever.retrieve(basicTerms, includingTerms, excludingTerms, time_sorted = time_sorted, on_the_fly = on_the_fly, subjectWanted = subject_wanted, fromWanted = sender_wanted, bodyWanted = body_wanted)
            
            if results.__len__() == 0:
                response = ""
            else:
                result_string = ""
                bodies_to_send = 20
                for mail in results:
                    result_string += " '" + mail[0].replace("\r\n", "") + "'"
                    result_string += " '" + mail[1].replace("\r\n", "") + "'"
                    result_string += " '" + str(time.asctime(time.localtime(mail[2]))) + "'"
                    result_string += " '" + mail[3].replace("\r\n", "<br/>") + "'"
                    if bodies_to_send >= 0:
                        result_string += " '" + mail[4].replace("\r\n", "<br/>") + "'"
                        bodies_to_send -=1
                    else:
                        result_string += " ''"
                    result_string += " '" + str(mail[5]) + "'"
                response = result_string
        else:
            response = "!ERROR!"
        
        return response
    
    def handleFetchBody(self, ids):
        
        results = self.server.retriever.get_body_by_id(ids.split(" "))
        
        response = ""
        if results.__len__() > 0:
            for body in results:
                response += " '" + body.replace("\r\n", "<br/>") + "'"
        
        return response
    
    def handleTimeLine(self, ids):
        results = self.server.retriever.get_time_line(ids.split(" "))
        return results
        
    def restart(self, args):
        self.server.retriever = Retriever()
        return "None"
    
    def handleCommand(self, type, args):
        if type == "query":
            return self.handleQuery(args)
        elif type == "queryOTF":
            return self.handleQuery(args, on_the_fly=True)
        elif type == "queryTime":
            return self.handleQuery(args, time_sorted=True)
        elif type == "fetchBody":
            return self.handleFetchBody(args)
        elif type == "idsToTimeLine":
            return self.handleTimeLine(args)
        elif type == "restart":
            return self.restart(args)
    
    def handle(self):
        
        command = self.request.recv(4096)
        type = command.split(" ", 1)[0];
        args = command.split(" ", 1)[1];
        
        response = self.handleCommand(type, args)
        
        self.request.send(response)
        
class RetrievalServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    retriever = Retriever()
    indTh = None
    
    def start_indexing_thread(self):
        self.indTh = automaticIndexer.create_indexer_thread()
        

##################################################################################################


create_retrieval_thread()
port = 58000
max_attempts = 100
while max_attempts > 0 :
    try:
        print "\nServer: serving at port " + str(port)
        print "\tType one of the following in your web browser:"
        print "\t\t- http://127.0.0.1:" + str(port) +"/\t\t(faster on Firefox)"
        print "\t\t- http://localhost:" + str(port) +"/"
        RGIServer(('',port), Handler).serve_forever()
    except Exception:
        print "Server: error at port",port
        port += 1
        max_attempts -=1
print "Server: too many attempts. No ports available"
