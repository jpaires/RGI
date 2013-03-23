# -*- coding: utf-8 -*-
from threading import Thread
import time
import socket
import cPickle as pickle
import ConfigParser

from services import cookiesManager
from services.indexer import Indexer 
from services.emailLib import GmailAccount

SECONDS_PER_WEEK = 60 * 60 * 24 * 7
SECONDS_PER_DAY = 60 * 60 * 24

def create_indexer_thread():
    indexer_thread = UpdateThread().start()
    return indexer_thread

#########################

class UpdateThread(Thread):
    
    INDEX_TIMES = "indextimes.rgi"
    LAST_UPDATE = "last_update"
    LAST_FULL = "last_full"
    INDEX_MODE = "all"
    
    def __init__(self):
        Thread.__init__(self)
        try:
            config = ConfigParser.ConfigParser()
            config.read("config.ini")
            mode = config.get("indexer", "index")
            if mode == 'UNREAD':
                self.INDEX_MODE = "unread"
            else:
                self.INDEX_MODE = "all"
        except:
            self.INDEX_MODE = "all"
        try:
            index_times = open(self.INDEX_TIMES)
            self.__indexer = Indexer([], init=False)
        except IOError:
            index_times = open(self.INDEX_TIMES, "w")
            index_times.close()
            index_times = open(self.INDEX_TIMES)
            self.__indexer = None
        
        try:
            self.__index_times = pickle.load(index_times)
        except EOFError:
            self.__index_times = {}
            self.__index_times[self.LAST_FULL] = 0.0
            self.__index_times[self.LAST_UPDATE] = 0.0
            
        index_times.close()
        print "\nIndexer: Ready in index '" + self.INDEX_MODE + "' mode"
        
    def run(self):
        while 1:
            next_full = self.__index_times[self.LAST_FULL] + SECONDS_PER_WEEK
            next_update = self.__index_times[self.LAST_UPDATE] + SECONDS_PER_DAY
            now = time.time()
            if next_full <= now:
                loginCookies = cookiesManager.get_login_cookies()
                if loginCookies != None: 
                    g=GmailAccount()
                    g.login(loginCookies.mail, loginCookies.password)
                    print "\nIndexer: Starting to index..."
                    if self.INDEX_MODE == "unread":
                        toIndex = g.get_unread()
                    else:
                        toIndex = g.get_all()
                    if self.__indexer is None:
                        self.__indexer = Indexer(toIndex)
                    else:
                        self.__indexer.full_update(toIndex)
                    self.__index_times[self.LAST_FULL] = now
                    self.__index_times[self.LAST_UPDATE] = now
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(("127.0.0.1", 58001))
                    sock.send("restart retriever")
                    print "\nIndexer: Indexing operation completed."
                    
                else:
                    print "\nIndexer: Can't index. No cookies found. (Tip: login or reload page)"
                    time.sleep(5)
            elif next_update <= now:
                last_updade = self.__index_times[self.LAST_UPDATE]
                self.__indexer.update_by_date(g.get_all_since(last_updade))
                self.__index_times[self.LAST_UPDATE] = now
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", 58001))
                sock.send("restart retriever")
            else:
                next = min(next_full, next_update)
                time.sleep(next - now)
            index_times = open(self.INDEX_TIMES , "w")
            pickle.dump(self.__index_times, index_times)
            index_times.close()


##################################################################################################