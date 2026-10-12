import csv
import email
import html
import imaplib
import os
import re
import ssl
from collections import Counter
from datetime import date, timedelta
from email.header import decode_header, make_header
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()

host = os.environ["BRIDGE_HOST"]
port = int(os.environ["BRIDGE_PORT"])
user = os.environ["BRIDGE_USER"]
password = os.environ["BRIDGE_PASS"]

SINCE = (date.today() - timedelta(days=90)).strftime("%d-%b-%Y")
OUTPUT = "data/dry_run.csv"

OWN_ADDRESSES = ["moosessander@gmail.com", "moosessander@pm.me"]
IGNORE_DOMAINS = ["github.com", "a16z.com", "microsoftonline.com"]
OTP_SUBJECTS = [
    "one-time passcode", "one-time-passcode", "verification code",
    "ühekordne parool",
]
NOISE_DOMAINS = [
    "ziprecruiter.ie", "flexjobs.com", "goworkabit.com", "adzuna.co.uk",
    "jobgether.com", "remotejobs.io", "niceboard.co", "upwork.com",
]
NOISE_SUBJECTS = [
    "kas neid tööpakkumisi märkasid", "lõpetamata cv",
    "vii kandideerimine kiirelt lõpuni", "cv nädalane näitamiste arv",
    "your connection with", "matched with a job", "new opportunities",
    "can we keep your information",
]
REJECT_WORDS = [
    "unfortunately", "kahjuks", "not moving forward", "other candidates",
    "not the right fit", "ideal fit", "decided to move forward",
    "teiste kandidaatidega", "otsustasime", "filled the position", "position has been filled",    "won't be moving forward", "will not be moving forward",
   "not be progressing", "regret to inform", "decided not to",
   "not to move forward"
]
INTERVIEW_WORDS = ["interview", "intervjuu", "tööintervjuu"]
PROGRESS_WORDS = [
    "next round", "next stage", "move you forward", "moving you forward",
    "järgmisse vooru", "järgmisse etappi",]
FEEDBACK_SUBJECTS = ["feedback", "tagasiside"]
CONFIRM_WORDS = [
    "thank you for applying", "thanks for applying",
    "thank you for your application", "we have received your application",
    "application received", "application confirmation",
    "thanks for your interest", "thank you for your interest",
    "kandideerimise kätte saanud", "täname kandideerimast",
    "täname, et kandideerisite", "ist bei uns eingegangen", "kätte saanud"
]
APPLICATION_WORDS = ["application", "applying", "kandideeri", "candidate", "kandidaat"]


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


def matches(domain, domains):
    return any(domain == d or domain.endswith("." + d) for d in domains)


def has(text, words):
    return any(w in text for w in words)


def body_preview(msg, length=600):
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


def classify(sender, domain, subject, body, is_reply):
    s = subject.lower()
    text = s + " " + body.lower()

    if sender in OWN_ADDRESSES or matches(domain, IGNORE_DOMAINS) or has(s, OTP_SUBJECTS):
        return None, "own mail, ignored domain or login code"

    if matches(domain, NOISE_DOMAINS) or has(s, NOISE_SUBJECTS):
        return "Job-Noise", "noise domain or subject"

    if matches(domain, ["cvkeskus.ee"]):
        if "sinu cv on saadetud" in s:
            return "Job-Confirmations", "cv keskus sent"
        return "Job-Noise", "cv keskus other"

    if matches(domain, ["cv.ee"]):
        if "kandideerimise kinnitus" in s:
            return "Job-Confirmations", "cv.ee confirmation"
        if "konkursi tagaside" in s:
            return "Job-Feedback", "cv.ee feedback"
        return "Job-Noise", "cv.ee other"

    if matches(domain, ["linkedin.com"]):
        if "your application was sent" in s or "your application was viewed" in s:
            return "Job-Confirmations", "linkedin sent or viewed"
        if "your application to" in s:
            return "Job-Rejections", "linkedin status update"
        return None, "linkedin other"

    known = matches(domain, HIRING) or matches(domain, EMPLOYERS)

    if known or has(s, APPLICATION_WORDS):
        if has(text, REJECT_WORDS):
            return "Job-Rejections", "rejection wording"
        if (is_reply or s.startswith("re:")) and known:
            return "Job-Feedback", "reply from hiring side"
        if has(s, FEEDBACK_SUBJECTS):
            return "Job-Feedback", "feedback in subject"
        if has(s, CONFIRM_WORDS):
            return "Job-Confirmations", "confirmation in subject"
        if has(text, INTERVIEW_WORDS) or has(text, PROGRESS_WORDS):
            return "Job-Progress", "interview or next round wording"
        if has(text, CONFIRM_WORDS):
            return "Job-Confirmations", "confirmation in body"
        if known:
            return "Job-Review", "hiring system, unclear"
        return "Job-Review", "unknown sender, application wording"

    return None, "not job mail"

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

counts = Counter()
os.makedirs("data", exist_ok=True)

with imaplib.IMAP4(host, port) as mail, open(OUTPUT, "w", newline="", encoding="utf-8") as f:
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

    mail.select('"All Mail"', readonly=True)
    status, data = mail.search(None, "SINCE", SINCE)
    ids = data[0].split()
    print(f"Checking {len(ids)} emails")

    writer = csv.writer(f)
    writer.writerow(["date", "from", "subject", "folder", "reason"])

    for num in ids:
        status, msg_data = mail.fetch(num, "(BODY.PEEK[])")
        msg = email.message_from_bytes(msg_data[0][1])
        sender = parseaddr(decode(msg.get("From")))[1].lower()
        domain = sender.split("@")[-1] if "@" in sender else ""
        subject = decode(msg.get("Subject"))
        in_reply_to = (msg.get("In-Reply-To") or "").strip()
        is_reply = in_reply_to in sent_ids
        folder, reason = classify(sender, domain, subject, body_preview(msg), is_reply)
        if folder:
            counts[folder] += 1
            writer.writerow([msg.get("Date", ""), sender, subject, folder, reason])

for folder, count in counts.most_common():
    print(f"{count:4}  {folder}")
print(f"Decisions written to {OUTPUT}")