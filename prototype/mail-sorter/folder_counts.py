import imaplib
import os
import ssl

from dotenv import load_dotenv

load_dotenv()

host = os.environ["BRIDGE_HOST"]
port = int(os.environ["BRIDGE_PORT"])
user = os.environ["BRIDGE_USER"]
password = os.environ["BRIDGE_PASS"]

FOLDERS = ["Job-Confirmations", "Job-Rejections", "Job-Feedback",
           "Job-Progress", "Job-Review", "Job-Noise"]

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

with imaplib.IMAP4(host, port) as mail:
    mail.starttls(ssl_context=context)
    mail.login(user, password)
    for name in FOLDERS:
        status, data = mail.select(f'"Folders/{name}"', readonly=True)
        print(f"{int(data[0]):5}  {name}")