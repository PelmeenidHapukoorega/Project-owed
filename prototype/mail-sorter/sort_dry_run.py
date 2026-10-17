import csv
import email
import html
import imaplib
import os
import re
import ssl
import argparse
from collections import Counter
from datetime import date, datetime, timedelta
from email.header import decode_header, make_header
from email.utils import parseaddr

from dotenv import load_dotenv
from classifier import classify, OWN_ADDRESSES

load_dotenv()

host = os.environ["BRIDGE_HOST"]
port = int(os.environ["BRIDGE_PORT"])
user = os.environ["BRIDGE_USER"]
password = os.environ["BRIDGE_PASS"]

SINCE = (date.today() - timedelta(days=90)).strftime("%d-%b-%Y")
OUTPUT = "data/dry_run.csv"
LOG = "data/moves_log.csv"

def load_list(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]


HIRING = load_list("hiring_systems.txt")
EMPLOYERS = load_list("data/employer_domains.txt")


def decode(value):
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""

def body_preview(msg, length=1500):
    html_text = ""
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type not in ("text/plain", "text/html"):
            continue
        payload = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")
        if content_type == "text/plain":
            return " ".join(text.split())[:length]
        if not html_text:
            html_text = text
    if html_text:
        text = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", html_text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        return " ".join(html.unescape(text).split())[:length]
    return ""


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="really copy mail into folders (default: dry run)")
parser.add_argument("--limit", type=int, default=0, help="stop after N emails (0 = no limit)")
args = parser.parse_args()

DESTINATIONS = {
    "Job-Confirmations": "Folders/Job-Confirmations",
    "Job-Rejections": "Folders/Job-Rejections",
    "Job-Feedback": "Folders/Job-Feedback",
    "Job-Progress": "Folders/Job-Progress",
    "Job-Review": "Folders/Job-Review",
    "Job-Noise": "Folders/Job-Noise",
}

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

os.makedirs("data", exist_ok=True)
log_is_new = not os.path.exists(LOG)
counts = Counter()


def collect_message_ids(mail, folder):
    ids = set()
    status, _ = mail.select(f'"{folder}"', readonly=True)
    if status != "OK":
        raise SystemExit(f"Folder missing or unreadable: {folder}")
    status, data = mail.search(None, "ALL")
    nums = data[0].split()
    for i in range(0, len(nums), 500):
        batch = ",".join(x.decode() for x in nums[i:i + 500])
        status, head_data = mail.fetch(batch, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
        for item in head_data:
            if isinstance(item, tuple):
                header = email.message_from_bytes(item[1])
                message_id = (header.get("Message-ID") or "").strip()
                if message_id:
                    ids.add(message_id)
    return ids


with imaplib.IMAP4(host, port) as mail, \
        open(OUTPUT, "w", newline="", encoding="utf-8") as f, \
        open(LOG, "a", newline="", encoding="utf-8") as log_file:
    mail.starttls(ssl_context=context)
    mail.login(user, password)

    sent_ids = set()

    mail.select('"Sent"', readonly=True)
    status, data = mail.search(None, "SINCE", SINCE)
    boxes = [('"Sent"', data[0].split())]

    mail.select('"All Mail"', readonly=True)
    status, data = mail.search(None, "SINCE", SINCE)
    boxes.append(('"All Mail"', data[0].split()))

    for box, nums in boxes:
        mail.select(box, readonly=True)
        print(f"Scanning {len(nums)} headers in {box}")
        for i in range(0, len(nums), 500):
            batch = ",".join(x.decode() for x in nums[i:i + 500])
            status, head_data = mail.fetch(batch, "(BODY.PEEK[HEADER.FIELDS (FROM MESSAGE-ID)])")
            for item in head_data:
                if isinstance(item, tuple):
                    header = email.message_from_bytes(item[1])
                    sender = parseaddr(decode(header.get("From")))[1].lower()
                    message_id = (header.get("Message-ID") or "").strip()
                    if message_id and (box == '"Sent"' or sender in OWN_ADDRESSES):
                        sent_ids.add(message_id)
    print(f"Found {len(sent_ids)} sent emails to match replies against")

    already_filed = set()
    for destination in DESTINATIONS.values():
        already_filed |= collect_message_ids(mail, destination)
    print(f"{len(already_filed)} emails already sit in the job folders")

    mail.select('"All Mail"', readonly=not args.apply)
    status, data = mail.uid("SEARCH", None, "SINCE", SINCE)
    uids = data[0].split()
    mode = "APPLY" if args.apply else "dry run"
    print(f"Checking {len(uids)} emails ({mode})")

    writer = csv.writer(f)
    writer.writerow(["date", "from", "subject", "folder", "reason", "preview"])
    log = csv.writer(log_file)
    if log_is_new:
        log.writerow(["time", "message_id", "from", "subject", "destination", "reason"])

    handled = 0
    skipped = 0
    for uid in uids:
        status, msg_data = mail.uid("FETCH", uid, "(BODY.PEEK[])")
        msg = email.message_from_bytes(msg_data[0][1])
        sender = parseaddr(decode(msg.get("From")))[1].lower()
        domain = sender.split("@")[-1] if "@" in sender else ""
        subject = decode(msg.get("Subject"))
        in_reply_to = (msg.get("In-Reply-To") or "").strip()
        is_reply = in_reply_to in sent_ids
        preview = body_preview(msg)
        folder, reason = classify(sender, domain, subject, preview, is_reply)
        if not folder:
            continue

        message_id = (msg.get("Message-ID") or "").strip()
        if not message_id or message_id in already_filed:
            skipped += 1
            continue
        if args.limit and handled >= args.limit:
            break

        destination = DESTINATIONS[folder]
        writer.writerow([msg.get("Date", ""), sender, subject, folder, reason, preview[:250]])

        if args.apply:
            status, _ = mail.uid("COPY", uid, f'"{destination}"')
            if status != "OK":
                print(f"COPY FAILED for uid {uid.decode()} to {destination}, stopping")
                break
            already_filed.add(message_id)
            log.writerow([datetime.now().isoformat(timespec="seconds"), message_id, sender, subject, destination, reason])
            log_file.flush()

        counts[folder] += 1
        handled += 1

for folder, count in counts.most_common():
    print(f"{count:4}  {folder}")
print(f"{skipped} skipped (already filed or no message-id)")
print("Copied into folders." if args.apply else "Dry run: nothing was changed.")