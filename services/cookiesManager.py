import os
import Cookie
from datetime import date, timedelta 

import logging

mail_cookie = 'mail'
password_cookie = 'password'

def create_login_cookies(mail, password):
    C = Cookie.SimpleCookie()
    C[mail_cookie] = mail
    C[password_cookie] = password
    print C.output()
    
def delete_login_cookies():
    C = Cookie.SimpleCookie()
    C[mail_cookie] = "void"
    C[password_cookie] = "void"
    new = date.today() + timedelta(days = -10) 
    C[mail_cookie]["expires"] = new.strftime("%a, %d-%b-%Y 23:59:59 GMT") 
    C[password_cookie]["expires"] = new.strftime("%a, %d-%b-%Y 23:59:59 GMT")
    print C.output()

def get_login_cookies():
    c = LoginCookies()
    if c.is_not_empty():
        return LoginCookies()
    else:
        return None

class LoginCookies:
    
    __mail = None
    __password = None
    
    def __init__(self):
        
        try:
            if 'HTTP_COOKIE' in os.environ:
                cookies = os.environ['HTTP_COOKIE']
                cookies = cookies.split('; ')
                handler = {}

                for cookie in cookies:
                    cookie = cookie.split('=')
                    handler[cookie[0]] = cookie[1]
            
            
                self.__mail = handler[mail_cookie]
                self.__password = handler[password_cookie]
        except BaseException:
            pass
    
    @property
    def mail(self):
        return self.__mail
    
    @property
    def password(self):
        return self.__password
    
    def is_not_empty(self):
        return self.__mail != None and self.__password != None