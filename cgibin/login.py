import sys, os
sys.path.append(os.getcwd())

import cgi
from services import cookiesManager

import logging
logging.basicConfig(level=logging.DEBUG)

form = cgi.FieldStorage()
mail = form.getvalue("mail", None)
password = form.getvalue("password", None)

if mail != None and password != None:
    cookiesManager.create_login_cookies(mail, password)
