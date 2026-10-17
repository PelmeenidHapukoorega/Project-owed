import os
import re

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
    "teiste kandidaatidega", "otsustasime", "filled the position",
    "position has been filled", "won't be moving forward",
    "will not be moving forward", "not be progressing", "regret to inform",
    "decided not to", "not to move forward",
    "other applicants", "decided to proceed", "proceed with other",
    "after thorough consideration", "after careful consideration",
    "not been successful", "unsuccessful", "not selected",
    "will not be proceeding", "unable to offer",
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

def matches(domain, domains):
    return any(domain == d or domain.endswith("." + d) for d in domains)


def has(text, words):
    return any(w in text for w in words)

QUOTE_MARKERS = re.compile(
    r"(on .{5,120} wrote:|-----original message-----|kirjutas .{3,120}:|from: .{3,80} sent: )",
    re.I,
)

def strip_quoted(text):
    match = QUOTE_MARKERS.search(text)
    return text[:match.start()] if match else text


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
        fresh_text = s + " " + strip_quoted(body.lower())
        if is_reply or (s.startswith("re:") and known):
            return "Job-Feedback", "reply from hiring side"
        if has(fresh_text, REJECT_WORDS):
            return "Job-Rejections", "rejection wording"
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