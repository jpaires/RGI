# -*- coding: utf-8 -*-
import sys, os
from email.base64mime import header_encode
sys.path.append(os.getcwd())

import imaplib
import re
import email
import time
import logging
from email.header import decode_header


def extract_body(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])
  
class Email_RGI:
    """
        Represents an email. It hold the sender, the subject and the message.
        To access or modify these properties simply use '.sender', '.subject' and '.message' on the email instance.
    """
    def __init__(self, id = "", sender = "", subject = "", message = "", time = -1):
        self.__id = id
        self.__sender = sender
        self.__subject = subject
        self.__message = message
        self.__time = time
    
    def get_id(self):
        return self.__id
    
    def set_id(self, new):
        self.__id= new
    
    def get_sender(self):
        return self.__sender
    
    def set_sender(self, new):
        self.__sender = new
        
    def get_subject(self):
        return self.__subject
    
    def set_subject(self, new):
        self.__subject = new
        
    def get_message(self):
        return self.__message
    
    def set_message(self, new):
        self.__message = new
   
    def get_time(self):
        return self.__time
    
    def set_time(self, new):
        self.__time = new
   
    id = property(get_id, set_id)
    sender = property(get_sender, set_sender)       
    subject = property(get_subject, set_subject)
    message = property(get_message, set_message)
    time = property(get_time, set_time)
    
        
 
class GmailAccount:
    def __init__(self):
        self.__IMAP_SERVER='imap.gmail.com'
        self.__IMAP_PORT=993
        self.__M = None
        self.__response = None
        self.__selected = None
    
    def get_response(self):
        return self.__id
    
    response = property(get_response, None)
    
    def login(self, username, password):
        """
            Performs the login with the give username and password. 
            Returns 'OK' if successful, the error message if not.
            IT MAY RAISE AN EXCEPTION.
        """
        self.__M = imaplib.IMAP4_SSL(self.__IMAP_SERVER, self.__IMAP_PORT)
        rc, self.response = self.__M.login(username, password)
        return rc
 
    def logout(self):
        self.__M.logout()
        
    def get_mailboxes(self):
        rc, self.response = self.__M.list()
        for item in self.response:
            self.__Mailboxes.append(item.split()[-1])
        return rc
    
    def select_box(self, box='Inbox', readonly='False'):
        rc, count = self.__M.select(box, readonly)
        self.__selected = box
        return rc, count
    
    def is_selected_box(self, box):
        return self.__selected is box
    
    def get_mail_count(self, box='Inbox'):
        rc, count = self.select_box(box)
        return count[0]

    def get_unread_count(self, box='Inbox'):
        rc, message = self.__M.status(box, "(UNSEEN)")
        unreadCount = re.search("UNSEEN (\d+)", message[0]).group(1)
        return unreadCount
    
    def emails_to_dictionary(self, emails):
        """
            Receives a list of Email_RGI object and returns a dictionary of those emails. The structure
            of the dictionary is as follows:
                { contact1 : ['i1' , 'i2' ...], contact2 : ['i3' , 'i4' ...] ... }
                Where, for example, 'contact1' is a contact that sent the emails with 'i1' and 'i2' as 'mail info'
        """
        emails_dictionary = {}
        for current_email in emails:
            current_email_sender = current_email.sender
            current_email_subject = current_email.subject
            current_email_message = current_email.message
            mail_info = [current_email_subject,current_email_message]
            if current_email_sender in emails_dictionary: # checking if the sender is already on the dictionary
                emails_dictionary[current_email_sender].append(mail_info)
            else:
                emails_dictionary[current_email_sender] = [mail_info]
        return emails_dictionary
    
    def get_email_charset(self, email_msg):
        """
            Returns the value for the 'charset' field on 'email_msg'
            Not great...
        """
        try:
            r = re.compile('(.*)charset=([A-Za-z0-9-"]*)')
            m  = r.search(email_msg)
            charset = m.group(2).replace("\"", "")
        except BaseException:
            charset = None
        return charset
    
    def convert_to_utf8(self, original_str, original_encoding):
        if original_encoding is None:
            original_encoding = "iso-8859-1"
        if "utf-8" in original_encoding.lower():
            return original_str
        return original_str.decode(original_encoding).encode("utf-8")
    
    def convert_email_to_utf8(self, original_str, original_encoding):
        """
            Converts a string in an "email formatted body" in "original_encoding" to utf-8.
            This is needed because the "email formatted body" is not exactly as expected: 
                - instead of "\xC3\xA3" for "ã" we have "=C3=A3"
                - "=\r\n" means newline
        """
        pieces = re.split("(=[A-Z0-9]{2})", original_str)
        pre_converted_string =''
        for piece in pieces:
            if piece.startswith("=") and piece.isupper():
                code = piece[1] + piece[2]
                try:
                    code = chr(int(code, 16))
                except ValueError:
                    code = code
                piece = code
            pre_converted_string += piece
        pre_converted_string = pre_converted_string.replace('=\r\n', '') #taking that useless newline
        return self.convert_to_utf8(pre_converted_string, original_encoding)
    
    def get_mail_by_id(self, message_id, box='inbox', readonly=True):
        """
            Get a mail by its 'Message-id'
        """
        if not self.is_selected_box(box):
            self.select_box(box, readonly)
        typ, num = self.__M.search(None, '(HEADER MESSAGE-ID ' + message_id + ')') 
        return self.get_mail(num[0], box, readonly)
    
    def get_mail(self, num, box='inbox', readonly=True):
        """
            Get a mail by its 'num', not its 'Message-id'
        """
        print("Getting " + num)
        if not self.is_selected_box(box):
            self.select_box(box, readonly)
        try:
            this_email = Email_RGI()
            
            typ, msg_data = self.__M.fetch(num, '(BODY.PEEK[TEXT] BODY.PEEK[HEADER])')
            if(msg_data.__len__() == 1 and "Failure" in msg_data[0]):
                print "Failed to fetch " + num
                return None
            
            data = msg_data[1][1] + msg_data[0][1]
            msg = email.message_from_string(data)
            
            this_email.id = msg['message-id'];
            
            # getting the sender            
            senderDecode = decode_header(msg['from'])
            header = email.header.make_header(senderDecode)
            this_email.sender = header.__unicode__().encode("utf-8")
            
            # getting the subject
            subjectDecode = decode_header(msg['subject'].replace("\r\n", ""))
            header = email.header.make_header(subjectDecode)
            this_email.subject = header.__unicode__().encode("utf-8")
            
            this_email.time = time.mktime(email.Utils.parsedate(msg['date']))
            
            # getting the message (only the text/plain part! This lib does not support text/html parts! It's not a bug, it's a feature)
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type().find('text/plain') != -1:
                        this_email.message += self.convert_to_utf8(part.get_payload(decode=True), part.get_content_charset())
            else:
                if msg.get_content_type().find('text/plain') != -1:
                    this_email.message += self.convert_to_utf8(msg.get_payload(decode=True), msg.get_content_charset())

            return this_email
        except Exception, AttributeError:
            logging.debug("An error was occurred...");
            import traceback
            traceback.print_exc()
       
    def get_mails(self, box='inbox', criteria='ALL'):
        self.select_box(box, readonly=True)
        typ, data = self.__M.search(None, criteria)
        emails = []
        for num in data[0].split():
            mail = self.get_mail(num, box)
            if mail != None:
                emails.append(mail)
        return emails
    
    def get_unread(self):
        return self.get_mails('inbox', 'UNSEEN')
    
    def get_mails_since(self, time_seconds, box='inbox'):
        self.select_box(box, readonly=True)
        typ, data = self.__M.search(None, 'ALL')
        emails = []
        nums = data[0].split()
        len = nums.__len__()
        i = len -1
        while i >= 0:
            mail = self.get_mail(nums[i])
            i -= 1
            print mail.time
            if mail != None and mail.time <= time_seconds:
                break
            emails.append(mail)
        return emails
    
    def get_all(self):
        return self.get_mails() + self.get_mails(box='[Gmail]/Sent Mail') 
    
    def get_all_since(self, time_seconds):
        return self.get_mails_since(time_seconds) + self.get_mails_since(time_seconds, '[Gmail]/Sent Mail')
    
    """
        Attention!!!
        Needs some review (see the computation of the body part in get_mails)
    """
    def get_complete_mails(self, box='inbox', criteria='ALL'):
        """
            Complete mails mean with COMPLETE (attachments included)
        """
        self.select_box(box, readonly=True)
        typ, data = self.__M.search(None, criteria)
        emails = []
        last_mail_time = -1
        for num in data[0].split():
            try:
                FETCHTHIS = '(RFC822)'
                typ, msg_data = self.__M.fetch(num, FETCHTHIS)
                body = email.message_from_string(msg_data[0][1])
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])
                        this_email = Email_RGI()
                        senderDecode = decode_header(msg['from'])
                        this_email.sender = self.convert_to_utf8(senderDecode[0][0],senderDecode[0][1])
                        subjectDecode = decode_header(msg['subject'].replace("\r\n", ""))
                        this_email.id = msg['message-id'];
                        if(last_mail_time == -1):
                            last_mail_time = time.mktime(email.Utils.parsedate(msg['date']))
                        #logging.debug(time.mktime(email.Utils.parsedate(msg['date'])));
                        this_email.subject = self.convert_to_utf8(subjectDecode[0][0],subjectDecode[0][1])
                        msg_body = ''
                        for part in body.walk():
                            if part.get_content_type() == 'text/plain':
                                msg_body += part.get_payload()
                                this_email.message = msg_body;
                                this_email.message = self.convert_to_utf8(msg_body, self.get_email_charset(msg_data[0][1]))
                                if not msg['Content-Transfer-Encoding'] == "8bit":
                                    this_email.message = self.convert_email_to_utf8(this_email.message, self.get_email_charset(msg_data[0][1]))
                                emails.append(this_email)
            except Exception, AttributeError:
                logging.debug("An error was occurred...");
        return emails

def main():
    pass
    
if __name__=="__main__":
    main()