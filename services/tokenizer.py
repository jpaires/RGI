#!/usr/bin/python
# -*- coding: utf8 -*-

import re
import sys, os
sys.path.append(os.getcwd())
from services.django.utils.encoding import smart_unicode, smart_str

re_word = re.compile(r'[a-zA-Z0-9\-\xc0-\xff]+',re.UNICODE)
re_secondary = re.compile(r'[\w]+', re.UNICODE)


STOPWORDS_EN=['a', 'about', 'above', 'according', 'across', 'actually',
           'adj', 'after', 'afterwards', 'again', 'against', 'all',
           'almost', 'alone', 'along', 'already', 'also', 'although',
           'always', 'among', 'amongst', 'an', 'and', 'another', 'any',
           'anyhow', 'anyone', 'anything', 'anywhere', 'are', "aren't",
           'around', 'as', 'at', 'b', 'be', 'became', 'because', 'become',
           'becomes', 'becoming', 'been', 'before', 'beforehand', 'begin',
           'beginning', 'behind', 'being', 'below', 'beside', 'besides',
           'between', 'beyond', 'billion', 'both', 'but', 'by', 'c', 'can',
           "can't", 'cannot', 'caption', 'co', 'co.', 'could', "couldn't",
           'd', 'did', "didn't", 'do', 'does', "doesn't", "don't", 'down',
           'during', 'e', 'each', 'eg', 'eight', 'eighty', 'either', 'else',
           'elsewhere', 'end', 'ending', 'enough', 'etc', 'even', 'ever',
           'every', 'everyone', 'everything', 'everywhere', 'except', 'f',
           'few', 'fifty', 'first', 'five', 'for', 'former', 'formerly',
           'forty', 'found', '', 'four', 'from', 'further', 'g', 'h', 'had',
           'has', "hasn't", 'have', "haven't", 'he', "he'd", "he'll", "he's",
           'hence', 'her', 'here', "here's", 'hereafter', 'hereby', 'herein',
           'hereupon', 'hers', 'herself', 'him', 'himself', 'his', 'how',
           'however', 'hundred', 'i', "i'd", "i'll", "i'm", "i've", 'ie',
           'if', 'in', 'inc.', 'indeed', 'instead', 'into', 'is', "isn't",
           'it', "it's", 'its', 'itself', 'j', 'k', 'l', 'last', 'later',
           'latter', 'latterly', 'least', 'less', 'let', "let's", 'like',
           'likely', 'ltd', 'm', 'made', 'make', 'makes', 'many', 'maybe',
           'me', 'meantime', 'meanwhile', 'might', 'million', 'miss', 'more',
           'moreover', 'most', 'mostly', 'mr', 'mrs', 'much', 'must', 'my',
           'myself', 'n', 'namely', 'neither', 'never', 'nevertheless', 'next',
           'nine', 'ninety', 'no', 'nobody', 'none', 'nonetheless', 'noone',
           'nor', 'not', 'nothing', 'now', 'nowhere', 'o', 'of', 'off', 'often',
           'on', 'once', 'one', "one's", 'only', 'onto', 'or', 'other', 'others',
           'otherwise', 'our', 'ours', 'ourselves', 'out', 'over', 'overall',
           'own', 'p', 'per', 'perhaps', 'q', 'r', 'rather', 'recent', 'recently',
           's', 'same', 'seem', 'seemed', 'seeming', 'seems', 'seven', 'seventy',
           'several', 'she', "she'd", "she'll", "she's", 'should', "shouldn't",
           'since', 'six', 'sixty', 'so', 'some', 'somehow', 'someone',
           'something', 'sometime', 'sometimes', 'somewhere', 'still', 'stop',
           'such', 't', 'taking', 'ten', 'than', 'that', "that'll", "that's",
           "that've", 'the', 'their', 'them', 'themselves', 'then', 'thence',
           'there', "there'd", "there'll", "there're", "there's", "there've",
           'thereafter', 'thereby', 'therefore', 'therein', 'thereupon',
           'these', 'they', "they'd", "they'll", "they're", "they've",
           'thirty', 'this', 'those', 'though', 'thousand', 'three', 'through',
           'throughout', 'thru', 'thus', 'to', 'together', 'too', 'toward',
           'towards', 'trillion', 'twenty', 'two', 'u', 'under', 'unless',
           'unlike', 'unlikely', 'until', 'up', 'upon', 'us', 'used', 'using',
           'v', 'very', 'via', 'w', 'was', "wasn't", 'we', "we'd", "we'll",
           "we're", "we've", 'well', 'were', "weren't", 'what', "what'll",
           "what's", "what've", 'whatever', 'when', 'whence', 'whenever',
           'where', "where's", 'whereafter', 'whereas', 'whereby', 'wherein',
           'whereupon', 'wherever', 'whether', 'which', 'while', 'whither',
           'who', "who'd", "who'll", "who's", 'whoever', 'whole', 'whom',
           'whomever', 'whose', 'why', 'will', 'with', 'within', 'without',
           "won't", 'would', "wouldn't", 'x', 'y', 'yes', 'yet', 'you',
           "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself',
           'yourselves', 'z', 'www']

STOPWORDS_PT=u"""a
ÃƒÂ 
acordo
agora
ainda
alÃƒÂ©m
algumas
alguns
altura
ano
anos
antes
ao
aos
apenas
apesar
apoio
apÃƒÂ³s
aqui
ÃƒÂ¡rea
as
ÃƒÂ s
assim
atÃƒÂ©
atravÃƒÂ©s
bem
cada
casa
caso
causa
cento
centro
cerca
cinco
com
como
conselho
conta
contos
contra
cultura
da
dar
das
de
depois
desde
desta
deste
dia
dias
disse
diz
dizer
do
dois
dos
duas
durante
e
ÃƒÂ©
ele
eleiÃƒÂ§ÃƒÂµes
eles
em
embora
enquanto
entanto
entÃƒÂ£o
entre
equipa
era
essa
esse
esta
estÃƒÂ¡
estado
estados
estÃƒÂ£o
estar
estava
este
estes
eu
exemplo
facto
falta
faz
fazer
fez
fim
final
foi
fora
foram
forma
frente
geral
grande
grandes
grupo
hÃƒÂ¡
histÃƒÂ³ria
hoje
isso
isto
jogo
lÃƒÂ¡
lado
lei
lhe
local
lugar
maior
maioria
mais
manuel
mas
me
meio
melhor
menos
mercado
mÃƒÂªs
meses
mesma
mesmo
mil
milhÃƒÂµes
ministÃƒÂ©rio
ministro
momento
muito
muitos
mundo
mÃƒÂºsica
na
nada
nÃƒÂ£o
nas
nem
neste
no
noite
nome
nos
nova
novo
num
numa
nÃƒÂºmero
nunca
o
obras
onde
ontem
os
ou
outra
outras
outro
outros
p.
paÃƒÂ­s
paÃƒÂ­ses
para
parece
parte
partido
partir
passado
pela
pelas
pelo
pelos
pessoas
pode
poder
poderÃƒÂ¡
polÃƒÂ­cia
polÃƒÂ­tica
pontos
por
porque
possÃƒÂ­vel
pouco
primeira
primeiro
prÃƒÂ³prio
prÃƒÂ³ximo
ps
psd
pÃƒÂºblico
quais
qual
qualquer
quando
quanto
quase
quatro
que
quem
quer
questÃƒÂ£o
r.
regiÃƒÂ£o
relaÃƒÂ§ÃƒÂ£o
repÃƒÂºblica
sÃƒÂ£o
se
segunda
segundo
seguranÃƒÂ§a
seis
seja
sem
semana
sempre
sentido
ser
serÃƒÂ¡
seu
seus
sido
silva
situaÃƒÂ§ÃƒÂ£o
sÃƒÂ³
sobre
sua
suas
tal
tambÃƒÂ©m
tÃƒÂ£o
tarde
tem
tÃƒÂªm
tempo
ter
terÃƒÂ¡
teve
tinha
toda
todas
todo
todos
trÃƒÂªs
tudo
ÃƒÂºltimo
ÃƒÂºltimos
um
uma
vai
vÃƒÂ£o
ver
vez
vezes""".splitlines()

STOPWORDS={}

for s in STOPWORDS_EN:
    STOPWORDS[s]=None

for s in STOPWORDS_PT:
    STOPWORDS[s]=None

def Tokenize(text, minsize = 3, use_stopwords = True, stem = True):
    tokens = []
    text = smart_unicode(text) 
    for cur_token in re_word.findall(text):
        if len(cur_token) >= minsize:
            lt = cur_token.lower()
            if ((use_stopwords and not (lt in STOPWORDS)) or (not use_stopwords)):
                tokens.append(smart_str(lt))
                for t in re_secondary.findall(lt):
                    if (not smart_str(t) in tokens) and ((use_stopwords and not (t in STOPWORDS)) or (not use_stopwords)):
                        tokens.append(smart_str(t))
    return tokens

re_input = re.compile(r'\+[a-zA-Z0-9\-\xc0-\xff]+|[a-zA-Z0-9\-\xc0-\xff]+', re.UNICODE)

def TokenizeInput(text, minsize = 3, use_stopwords = True, stem = True):
    terms = []
    including = []
    excluding = []
    text = smart_unicode(text) 
    for cur_token in re_input.findall(text):
        if len(cur_token) >= minsize:
            lt = cur_token.lower()
            if lt[0] == '+':
                lt = lt.lstrip('+')
                if ((use_stopwords and not (lt in STOPWORDS)) or (not use_stopwords)):
                    including.append(smart_str(lt))
            elif lt[0] == '-':
                lt = lt.lstrip('-')
                if ((use_stopwords and not (lt in STOPWORDS)) or (not use_stopwords)):
                    excluding.append(smart_str(lt))
            else:
                if ((use_stopwords and not (lt in STOPWORDS)) or (not use_stopwords)):
                    terms.append(smart_str(lt))
                    for t in re_secondary.findall(lt):
                        if (smart_str(t) not in terms) and ((use_stopwords and not (t in STOPWORDS)) or (not use_stopwords)):
                            terms.append(smart_str(t))
                continue
    return terms, including, excluding


def main():
    pass
    
if __name__=='__main__':
    main()
