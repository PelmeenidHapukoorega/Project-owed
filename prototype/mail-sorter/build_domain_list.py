import csv
import email
import imaplib
import os
import ssl
from collections import Counter, defaultdict
from email.header import decode_header, make_header
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()

host = os.environ["BRIDGE_HOST"]
port = int(os.environ["BRIDGE_PORT"])
user = os.environ["BRIDGE_USER"]
password = os.environ["BRIDGE_PASS"]

OUTPUT = "data/hiring_domain_candidates.csv"
BATCH = 500

DOMAIN_HINTS = [
    "recruit", "career", "talent", "jobs", "hire", "hiring",
    "teamtailor", "personio", "smartrecruiters", "teamdash", "lever",
    "ashby", "greenhouse", "workable", "workday", "bamboohr",
    "jobvite", "icims", "talendipank",
]
SUBJECT_WORDS = [
    "application", "applying", "kandideeri", "candidate", "kandidaat",
    "interview", "intervjuu", "position", "ametikoh",
]


def decode(value):
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

counts = Counter()
examples = defaultdict(list)

with imaplib.IMAP4(host, port) as mail:
    mail.starttls(ssl_context=context)
    mail.login(user, password)
    mail.select('"All Mail"', readonly=True)
    status, data = mail.search(None, "ALL")
    ids = data[0].split()
    print(f"Scanning {len(ids)} emails (headers only)")

    for i in range(0, len(ids), BATCH):
        batch = ",".join(x.decode() for x in ids[i:i + BATCH])
        status, msg_data = mail.fetch(batch, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
        for item in msg_data:
            if not isinstance(item, tuple):
                continue
            msg = email.message_from_bytes(item[1])
            sender = parseaddr(decode(msg.get("From")))[1].lower()
            domain = sender.split("@")[-1] if "@" in sender else ""
            subject = decode(msg.get("Subject"))
            domain_hit = any(h in domain for h in DOMAIN_HINTS)
            subject_hit = any(w in subject.lower() for w in SUBJECT_WORDS)
            if domain and (domain_hit or subject_hit):
                counts[domain] += 1
                if len(examples[domain]) < 2:
                    examples[domain].append(subject[:80])
        print(f"{min(i + BATCH, len(ids))}/{len(ids)}")

os.makedirs("data", exist_ok=True)
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["domain", "count", "example_1", "example_2"])
    for domain, count in counts.most_common():
        ex = examples[domain] + ["", ""]
        writer.writerow([domain, count, ex[0], ex[1]])

print(f"{len(counts)} candidate domains written to {OUTPUT}")