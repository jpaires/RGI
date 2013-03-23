# -*- coding: utf-8 -*-

import sys, os
import Cookie
sys.path.append(os.getcwd())

from services.cookiesManager import LoginCookies
from services.indexer import Indexer
import cgi
import cgitb
import sys
import os
import logging

from services.emailLib import GmailAccount
from services import htmlGenerator, cookiesManager

# log to stderr
logging.basicConfig(level=logging.DEBUG)


print "Content-Type: text/html\n"

print """<!DOCTYPE html>
<html lang="en">
"""
htmlGenerator.print_header()


loginCookies = cookiesManager.get_login_cookies()
if loginCookies != None:
    g = GmailAccount()
    try:
        resp = g.login(loginCookies.mail,loginCookies.password) 
        htmlGenerator.print_main_page()
        
    except Exception, e:
        #nothing so far
        print "Wrong username and/or password."
        htmlGenerator.print_page("login.html")
else:
    htmlGenerator.print_page("login.html")


print "</html>"
