# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)
import re

def inject_on_div(div_id, original, content_to_inject):
    """
    Injects 'content_to_inject' on a div with id equal to 'div_id' present on 'original'
    Example:
    div_id = 'test'
    
    original = '<html>
                <div id="test" class="myDiv">
                
                </div>
                </html>'
    
    content_to_inject = 'Welcome'
    
    Would return 
    '<html>
        <div id="test" class="myDiv">
        Welcome        
        </div>
    </html>'
    """
    m = re.match(".*(<div.*id=\""+ div_id +"\".*>)(.*)(</div>).*", original, re.DOTALL)
    return re.sub(m.group(1) + m.group(2) + m.group(3), m.group(1) + content_to_inject + m.group(3) , original)

def get_file_content(filepath):
    header_filehandler = open(filepath, 'r')
    content = header_filehandler.read()
    header_filehandler.close()
    return content
    
def print_from_file(filepath):
    """
    Prints the content of a given filename
    """
    
    
    header_filehandler = open(filepath, 'r')
    print header_filehandler.read()
    header_filehandler.close()

def print_header():
    """
    Prints the header of the html file
    """
    
    print_from_file("html/header.html")

def print_page(page):
    print_from_file("html/" + page)
    
def print_main_page():
    #original = get_file_content("html/main.html")
    #inject_on_div("mails", original, emails)
    
    print_from_file("html/main.html")
    return
    print """<body>
    Welcome!
    <form method="post" action="logout.py">
    <input type="submit" value="Logout" />
    </form>
    <div id="mails"></div>
    <body>
    <!-- 
    <div class="form-container">
        <form method="post" class="retrieve-form">
        Retrieve: <input type="text" name="terms" /> <br/>
        <input type="submit" value="Retrieve" />
        </form> 
    </div>
     -->
    Apresenta\xe7\xe3o <br/>
    Apresenta\xc3\xa7\xc3\xa3o  <br/>
    Apresentação
    Retrieve: <input type="text" name="query" id="query"/> <button type="button" class="retrieve-button">Retrieve</button> <br/>
    
    <div class="results">
        
    </div>
</body>"""
    """
    print \"""
        <html>
            <head>
            
            </head>
            
            <body>
                Apresentaçãos
                Apresenta\xc3\xa7\xc3\xa3os
            </body>
        </html>
    
    \"""
    """