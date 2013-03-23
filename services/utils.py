#!/usr/bin/python
# -*- coding: utf8 -*-
from __future__ import division
import sys, os
import logging
logging.basicConfig(level=logging.DEBUG)
sys.path.append(os.getcwd())
import math
from services import tokenizer
import time

import cPickle as pickle

class Retriever():
    
    GLOSSARY = "glossary.rgi"
    SUBJECT =  "subject.rgi"
    FROM = "from.rgi"
    BODY = "body.rgi"
    CACHE = "cache.rgi"
    TERMS_VECTORS = "termvectors.rgi"

    ALPHA = 25
    BETA = 15
    GAMMA = 2

    def __init__(self):
        #load indexes
        try:
            glossFile = open(self.GLOSSARY)
        except IOError:
            glossFile = open(self.GLOSSARY, "w")
            glossFile.close()            
            glossFile = open(self.GLOSSARY)
            
        try:
            subjFile = open(self.SUBJECT)
        except IOError:
            subjFile = open(self.SUBJECT, "w")
            subjFile.close()
            subjFile = open(self.SUBJECT)

        try:
            fromFile = open(self.FROM)
        except IOError:
            fromFile = open(self.FROM, "w")
            fromFile.close()
            fromFile = open(self.FROM)

        try:
            bodyFile = open(self.BODY)
        except IOError:
            bodyFile = open(self.BODY, "w")
            bodyFile.close()
            bodyFile = open(self.BODY)

        try:
            cacheFile = open(self.CACHE)
        except IOError:
            cacheFile = open(self.CACHE, "w")
            cacheFile.close()
            cacheFile = open(self.CACHE)
        
        try:
            termsVectorFile = open(self.TERMS_VECTORS)
        except IOError:
            termsVectorFile = open(self.TERMS_VECTORS, "w")
            termsVectorFile.close()
            termsVectorFile = open(self.TERMS_VECTORS)
        
        try:
            self.__gloss = pickle.load(glossFile)
        except EOFError:
            self.__gloss = {}
        try:
            self.__subj = pickle.load(subjFile)
        except EOFError:
            self.__subj = {}
        try:
            self.__fromp = pickle.load(fromFile)
        except EOFError:
            self.__fromp = {}
        try:
            self.__body = pickle.load(bodyFile)
        except EOFError:
            self.__body = {}
        try:
            self.__cache = pickle.load(cacheFile)
        except EOFError:
            self.__cache = {}
        try:
            self.__terms_vector = pickle.load(termsVectorFile)
        except EOFError:
            self.__terms_vector = {}
        
        glossFile.close()
        subjFile.close()
        fromFile.close()
        bodyFile.close()
        cacheFile.close()
        termsVectorFile.close()
        
    
    def addResults(self, terms, ind, results):
    
        for term in terms:
            code = 0
            
            #If terms is indexed, get code, if not, get to the next one and remove this one from the terms to not verify this in the future
            if term in self.__gloss:
                code = self.__gloss[term]
            else:
                terms.remove(term)
                continue
            
            #Get mails with the term on the subject
            if code in ind:
                for mail in ind[code]:
                    if mail not in results:
                        results.append(mail)
            
        return results
    
    def get_body_by_id(self, ids):
        result = []
        for id in ids:
            result.append(self.__cache[id][3])
        return result
    
        
    
    def retrieve(self, terms, including, excluding, time_sorted=False, on_the_fly=False,subjectWanted=True, fromWanted=True, bodyWanted=True):
        #Terms
        #For ranking reasons, search first in the subject, then the sender, then the body.
        results = []
        
        #Subject
        if subjectWanted:
            results = self.addResults(terms, self.__subj, results)
        
        #Sender
        if fromWanted:
            results = self.addResults(terms, self.__fromp, results)
        
        #Body
        if bodyWanted:
            results = self.addResults(terms, self.__body, results)
        
        
        #Include only
        if(including.__len__() > 0 ):
            inclmails = set()
            for term in including:
                code = 0
                aux = set()
                #If terms is indexed, get code, if not, get to the next one and remove this one from the terms to not verify this in the future
                if term in self.__gloss:
                    code = self.__gloss[term]
                else:
                    return []
    
                if code in self.__subj:
                    for mail in self.__subj[code]:
                        if mail not in aux:
                            aux.add(mail)
            
                if code in self.__fromp:
                    for mail in self.__fromp[code]:
                        if mail not in aux:
                            aux.add(mail)
    
                if code in self.__body:
                    for mail in self.__body[code]:
                        if mail not in aux:
                            aux.add(mail)
                
                if inclmails.__len__() > 0:
                    inclmails = inclmails.intersection(aux)
                else:
                    inclmails = inclmails.union(aux)
                
            #Join mails with every including term
            toEliminate = []
            for mail in results:
                if mail not in inclmails:
                    toEliminate.append(mail)

            for mail in toEliminate:
                results.remove(mail)
        
        #Exlude
        if(excluding.__len__() > 0 ):
            exclmails = []
            for term in excluding:
                code = 0
            
                #If terms is indexed, get code, if not, get to the next one and remove this one from the terms to not verify this in the future
                if term in self.__gloss:
                    code = self.__gloss[term]
                else:
                    excluding.remove(term)
                    continue
    
                if code in self.__subj:
                    for mail in self.__subj[code]:
                        if mail not in exclmails:
                            exclmails.append(mail)
            
                if code in self.__fromp:
                    for mail in self.__fromp[code]:
                        if mail not in exclmails:
                            exclmails.append(mail)
    
                if code in self.__body:
                    for mail in self.__body[code]:
                        if mail not in exclmails:
                            exclmails.append(mail)
            #Join mails with every including term
            toEliminate = []
            for mail in results:
                if mail in exclmails:
                    toEliminate.append(mail)
                    
            for mail in toEliminate:
                results.remove(mail)
                    
                        
        final_results = []
        
        if time_sorted:
            for id in results:
                r = [id]
                r = [id] + self.__cache[id] + [-1] #-1 means that the rank value was not calculated
                final_results.append(r)
            final_results.sort(cmp=None, key=lambda m: m[2], reverse=True)
        else:
            query_terms_vector = self.get_query_terms_vector(terms, including)
            rank_function = self.rank_part
            if on_the_fly:
                rank_function = self.OLDrank_part
            
            for id in results:            
                rank_sender = rank_function(id, "sender", query_terms_vector, terms, including)
                rank_subject = rank_function(id, "subject", query_terms_vector, terms, including)
                rank_body = rank_function(id, "body", query_terms_vector, terms, including)
                sim = self.ALPHA * rank_sender + self.BETA * rank_subject + rank_body
                
                r = [id] + self.__cache[id] + [sim]
                final_results.append(r)
            
            final_results.sort(cmp=None, key=lambda m: m[5], reverse=True)
        return final_results
    
    def get_query_terms_vector(self, normal_terms, including_terms):
        
        term_vector = []
        all_terms = normal_terms + including_terms
        number_of_parts = float(self.__cache.__len__())
        
        for term in all_terms:
            if term in including_terms:
                gamma = self.GAMMA
            else:
                gamma = 1
    
            code = self.__gloss[term]
            
            number_of_term_in_part = float(all_terms.count(term))
            number_of_terms_in_part = float(all_terms.__len__())
            
            s = frozenset()
            for di in self.__fromp, self.__subj, self.__body:
                if di.has_key(code):
                    s = s.union(di[code])
            
            number_of_parts_with_term = float(s.__len__())      
            term_vector.append(gamma * tf_idf(number_of_term_in_part, number_of_terms_in_part, number_of_parts_with_term, number_of_parts))  
        
        return term_vector
    
    
    def get_query_terms_vectors(self, normal_terms, including_terms):
        
        sender_term_vector = []
        subject_term_vector = []
        body_term_vector = []
        all_terms = normal_terms + including_terms
        number_of_parts = float(self.__cache.__len__())
        
        for term in all_terms:
            if term in including_terms:
                gamma = self.GAMMA
            else:
                gamma = 1
    
            code = self.__gloss[term]
            
            number_of_term_in_part = float(all_terms.count(term))
            number_of_terms_in_part = float(all_terms.__len__())
            
            for pair in (sender_term_vector, self.__fromp), (subject_term_vector, self.__subj), (body_term_vector,self.__body):
                
                if pair[1].has_key(code):
                    number_of_parts_with_term = float(pair[1][code].__len__())
                    pair[0].append(gamma * tf_idf(number_of_term_in_part, number_of_terms_in_part, number_of_parts_with_term, number_of_parts))
                else:
                    pair[0].append(0)
                    
        return sender_term_vector, subject_term_vector, body_term_vector
        
        
    def rank_part(self, mail_id, part, query_terms_vector, normal_terms, including_terms):
        if part is "sender":
            part_index = 0
        elif part is "subject":
            part_index = 1
            dict = self.__subj
        elif part is "body":
            part_index = 2
        else:
            logging.debug("rank: Not possible to rank part '" + part + "'")
            return 0.0
        
        dict = self.__terms_vector[mail_id][part_index]
        
        term_vector = []
        for term in normal_terms + including_terms:
            if term in including_terms:
                gamma = self.GAMMA
            else:
                gamma = 1
            
            code = self.__gloss[term]
            
            if dict.has_key(code):
                term_vector.append(gamma * dict[code])
            else:
                term_vector.append(0)
            
        return sim(term_vector, query_terms_vector)
        
    
    def OLDrank_part(self, mail_id, part, query_terms_vector, normal_terms, including_terms):
        if part is "sender":
            part_content = self.__cache[mail_id][0]
            dict = self.__fromp
        elif part is "subject":
            part_content = self.__cache[mail_id][2]
            dict = self.__subj
        elif part is "body":
            part_content = self.__cache[mail_id][3]
            dict = self.__body
        else:
            -1
            logging.debug("rank: Not possible to rank part '" + part + "'")
            return None
        
        term_vector = []
        for term in normal_terms + including_terms:
            if term in including_terms:
                gamma = self.GAMMA
            else:
                gamma = 1
    
            code = self.__gloss[term]
            
            if dict.has_key(code):
                number_of_term_in_part = float(dict[code].count(mail_id))
                number_of_terms_in_part = float(tokenizer.Tokenize(part_content).__len__())
                
                number_of_parts = float(self.__cache.__len__())
                number_of_parts_with_term = float(dict[code].__len__())
                term_vector.append(gamma * tf_idf(number_of_term_in_part, number_of_terms_in_part, number_of_parts_with_term, number_of_parts))
            else:
                term_vector.append(0)
        return sim(term_vector, query_terms_vector)
    
def tf_idf(term_count_doc, terms_count_doc, docs_with_term, total_docs):
    if term_count_doc == 0:
        return 0
    return term_count_doc / terms_count_doc  * math.log10( total_docs / docs_with_term)
        
       
def sim(a, b):
    """
    Cosine similarity of two vectors
    """
    numerator = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for i in range(0, a.__len__()):
        numerator += a[i] * b[i]
        norm_a += math.pow(a[i], 2)
        norm_b += math.pow(b[i], 2)
        
    if numerator == 0:
        return 0.0
    divisor = math.sqrt(norm_a) * math.sqrt(norm_b) 
    return numerator / divisor 
  

def main():
    pass
     
if __name__=="__main__":
    main()
