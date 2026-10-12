import imaplib
import os
import ssl

from dotenv import load_dotenv

load_dotenv()

host = os.environ["BRIDGE_HOST"]
port = int(os.environ["BRIDGE_PORT"])
user = os.environ["BRIDGE_USER"]
password = os.environ["BRIDGE_PASS"]

# Bridge uses self signed cert on localhost
# Verification is off for now, trusting bridges own cert is later improvement
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

with imaplib.IMAP4(host, port) as mail:
    mail.starttls(ssl_context=context)
    mail.login(user, password)
    status, folders = mail.list()
    for folder in folders:
        print(folder.decode())
