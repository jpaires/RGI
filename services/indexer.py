#!/usr/bin/python
# -*- coding: utf8 -*-
import sys, os
from services import utils
sys.path.append(os.getcwd())

import cPickle as pickle
import tokenizer

class Indexer:
    GLOSSARY = "glossary.rgi"
    SUBJECT = "subject.rgi"
    FROM = "from.rgi"
    BODY = "body.rgi"
    SEEN = "seen.rgi"
    CACHE = "cache.rgi"
    TERMS_VECTORS = "termvectors.rgi"

    GENCODE = 0
    GENCODELBL = "<gencode>"
    
    def load(self):
        glossshlv = open(self.GLOSSARY)
        subjshlv = open(self.SUBJECT)
        fromshlv = open(self.FROM)
        bodyshlv = open(self.BODY)
        seenshlv = open(self.SEEN)
        cacheshlv = open(self.CACHE)
        vectorshlv = open(self.TERMS_VECTORS)
        
        try:
            self.__glossshlv = pickle.load(glossshlv)
        except EOFError:
            self.__glossshlv = {}
        
        try:
            self.__subjshlv = pickle.load(subjshlv)
        except EOFError:
            self.__subjshlv = {}
        try:
            self.__fromshlv = pickle.load(fromshlv)
        except EOFError:
            self.__fromshlv = {}
        try:
            self.__bodyshlv = pickle.load(bodyshlv)
        except EOFError:
            self.__bodyshlv = {}
        try:
            self.__seenshlv = pickle.load(seenshlv)
        except EOFError:
            self.__seenshlv = []
        try:
            self.__cacheshlv = pickle.load(cacheshlv)
        except EOFError:
            self.__cacheshlv = {}
        try:
            self.__vectorshlv = pickle.load(vectorshlv)
        except EOFError:
            self.__vectorshlv = {}    
        
        glossshlv.close()
        subjshlv.close()
        fromshlv.close()
        bodyshlv.close()
        seenshlv.close()
        cacheshlv.close()
        vectorshlv.close()
        
    def sync(self):
        glossshlv = open(self.GLOSSARY, "w")
        subjshlv = open(self.SUBJECT, "w")
        fromshlv = open(self.FROM, "w")
        bodyshlv = open(self.BODY, "w")
        seenshlv = open(self.SEEN, "w")
        cacheshlv = open(self.CACHE, "w")
        vectorshlv = open(self.TERMS_VECTORS , "w")
        
        pickle.dump(self.__glossshlv, glossshlv)
        pickle.dump(self.__subjshlv, subjshlv)
        pickle.dump(self.__fromshlv, fromshlv)
        pickle.dump(self.__bodyshlv, bodyshlv)
        pickle.dump(self.__seenshlv, seenshlv)
        pickle.dump(self.__cacheshlv, cacheshlv)
        pickle.dump(self.__vectorshlv, vectorshlv)
        
        glossshlv.close()
        subjshlv.close()
        fromshlv.close()
        bodyshlv.close()
        seenshlv.close()
        cacheshlv.close()
        vectorshlv.close()
            
    def __init__(self, toIndex, init=True):
        if init:
            #create files
            glossshlv = open(self.GLOSSARY, "w")
            subjshlv = open(self.SUBJECT, "w")
            fromshlv = open(self.FROM, "w")
            bodyshlv = open(self.BODY, "w")
            seenshlv = open(self.SEEN, "w")
            cacheshlv = open(self.CACHE, "w")
            vectorshlv = open(self.TERMS_VECTORS, "w")
            
            glossshlv.close()
            subjshlv.close()
            fromshlv.close()
            bodyshlv.close()
            seenshlv.close()
            cacheshlv.close()
            vectorshlv.close()
        #init the dictionaries
        self.load()

        #index mails
        self.__seenshlv = []
        helper = {}
        for mail in toIndex:
            print("Indexing " + mail.id)
            helper[mail.id] = [-1, -1 , -1]
            
            self.__cacheshlv[mail.id] = [mail.sender, mail.time,mail.subject, mail.message]
            
            self.__seenshlv.append(mail.id)
            #index sender
            tmp = tokenizer.Tokenize(mail.sender)
            helper[mail.id][0]=tmp.__len__()
            code = 0
            for token in tmp:
                if not token in self.__glossshlv:
                    code = self.generateCode()
                    self.__glossshlv[token] = code
                    self.__fromshlv[code] = [mail.id]
                else:
                    code = self.__glossshlv[token]
                    if not code in self.__fromshlv:
                        self.__fromshlv[code] = [mail.id]
                    else:
                        self.__fromshlv[code].append(mail.id)                   
            #index subject
            tmp = tokenizer.Tokenize(mail.subject)
            helper[mail.id][1]=tmp.__len__()
            code = 0
            for token in tmp:
                if not token in self.__glossshlv:
                    code = self.generateCode()
                    self.__glossshlv[token] = code
                    self.__subjshlv[code] = [mail.id]
                else:
                    code = self.__glossshlv[token]
                    if not code in self.__subjshlv:
                        self.__subjshlv[code] = [mail.id]
                    else:
                        self.__subjshlv[code].append(mail.id)
            #index message
            tmp = tokenizer.Tokenize(mail.message)
            helper[mail.id][2]=tmp.__len__()
            code = 0
            for token in tmp:
                if not token in self.__glossshlv:
                    code = self.generateCode()
                    self.__glossshlv[token] = code
                    self.__bodyshlv[code] = [mail.id]
                else:
                    code = self.__glossshlv[token]
                    if not code in self.__bodyshlv:
                        self.__bodyshlv[code] = [mail.id]
                    else:
                        self.__bodyshlv[code].append(mail.id)
        
        
        for mail in toIndex:
            print("calculating " + mail.id)
            vect = [{}, {}, {}]
            for term in self.__glossshlv:
                code = self.__glossshlv[term]
                for tuple in [(vect[0], self.__fromshlv, 0, 0), (vect[1], self.__subjshlv, 2, 1), (vect[2], self.__bodyshlv, 3, 2)]:
                    dict = tuple[1]
                    part_content = self.__cacheshlv[mail.id][tuple[2]]
                    if dict.has_key(code):
                        number_of_term_in_part = float(dict[code].count(mail.id))
                        
                        number_of_terms_in_part = float(helper[mail.id][tuple[3]])
                
                        number_of_parts = float(self.__cacheshlv.__len__())
                        number_of_parts_with_term = float(dict[code].__len__())
                        
                        tf_idf_value = utils.tf_idf(number_of_term_in_part, number_of_terms_in_part, number_of_parts_with_term, number_of_parts)
                        
                        if tf_idf_value != 0:
                            tuple[0][code] = tf_idf_value
                        
                    else:
                        #nothing to do here
                        pass
                    
                    
            
            self.__vectorshlv[mail.id] = vect
        self.__glossshlv[self.GENCODELBL] = self.GENCODE
        
        #close the dictionaries
        self.sync()

    def update_by_date(self, toIndex):
        self.__init__(toIndex, init=False)
    
    def full_update(self, toIndex):
        self.__init__(toIndex)

    def generateCode(self):
        self.GENCODE = self.GENCODE + 1
        return self.GENCODE
        
def main():
    pass
    
if __name__=="__main__":
    main()
