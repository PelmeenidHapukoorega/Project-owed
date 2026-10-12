import csv

WORDS = [
    "cvkeskus", "cv.ee", "linkedin", "teamdash", "greenhouse", "lever",
    "workable", "recruitee", "smartrecruiters", "personio",
    "application", "applying", "kandideeri", "interview", "intervjuu",
    "unfortunately", "kahjuks", "candidate", "kandidaat", "position",
    "ametikoh", "vacancy", "töökoht", "automated reply", "we value", "consideration"
]

with open("data/mail_sample.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

hits = [
    r for r in rows
    if any(w in (r["from"] + r["subject"] + r["preview"]).lower() for w in WORDS)
]

with open("data/job_candidates.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(hits)

print(f"{len(hits)} possible job emails out of {len(rows)}")