import sys, os
sys.path.append(os.getcwd())

from services import cookiesManager
import logging
logging.basicConfig(level=logging.DEBUG)

cookiesManager.delete_login_cookies()
