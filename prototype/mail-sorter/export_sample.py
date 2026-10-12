import csv
import email
import html
import imaplib
import os
import re
import ssl
from datetime import date, timedelta
from email.header import decode_header, make_header

from dotenv import load_dotenv

load_dotenv()

host = os.environ["BRIDGE_HOST"]
port = int(os.environ["BRIDGE_PORT"])
user = os.environ["BRIDGE_USER"]
password = os.environ["BRIDGE_PASS"]

FOLDERS = ['"All Mail"']
SINCE = (date.today() - timedelta(days=90)).strftime("%d-%b-%Y")
OUTPUT = "data/mail_sample.csv"


def decode(value):
    return str(make_header(decode_header(value or "")))


def body_preview(msg, length=300):
    html_text = ""
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type not in ("text/plain", "text/html"):
            continue
        payload = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        text = payload.decode(charset, errors="replace")
        if content_type == "text/plain":
            return " ".join(text.split())[:length]
        if not html_text:
            html_text = text
    if html_text:
        text = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", html_text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        return " ".join(text.split())[:length]
    return ""


context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

os.makedirs("data", exist_ok=True)

with imaplib.IMAP4(host, port) as mail, open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    mail.starttls(ssl_context=context)
    mail.login(user, password)
    writer = csv.writer(f)
    writer.writerow(["folder", "date", "from", "subject", "bulk", "preview"])

    for folder in FOLDERS:
        mail.select(folder, readonly=True)
        status, data = mail.search(None, "SINCE", SINCE)
        message_ids = data[0].split()
        print(f"{folder}: {len(message_ids)} emails to export")
        for num in message_ids:
            status, msg_data = mail.fetch(num, "(BODY.PEEK[])")
            msg = email.message_from_bytes(msg_data[0][1])
            writer.writerow([
                folder,
                msg.get("Date", ""),
                decode(msg.get("From")),
                decode(msg.get("Subject")),
                "yes" if msg.get("List-Unsubscribe") else "no",
                body_preview(msg),
            ])

print(f"Wrote {OUTPUT}")