import csv
from collections import Counter
from email.utils import parseaddr

with open("data/job_candidates.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

domains = Counter()
for r in rows:
    address = parseaddr(r["from"])[1].lower()
    domain = address.split("@")[-1] if "@" in address else "(unknown)"
    domains[domain] += 1

for domain, count in domains.most_common(40):
    print(f"{count:4}  {domain}")