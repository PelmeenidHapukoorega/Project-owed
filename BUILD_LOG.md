# Proton bridge as a service and a dry-run mail sorter

## Intent

I set up a repo that ignores mail data, secrets and terraform state, and adds a gitleaks pre-commit hook [E002, E005]. I wanted Proton Mail Bridge running natively with systemd, not docker, "because no official image and it handles my decrypted mail" [E011]. The bridge needs pass with a passphrase-free gpg key, so the server login is the protection [E012]. On top of the bridge I built a mail sorter prototype. It connects to the bridge, exports mail to csv, builds a list of hiring system domains, and does a dry-run sort with a progress folder on proton [E083, E089, E138, E157]. The events don't show a bigger goal than that [E001, E021].

## Build

**Setting up the repo and hooks**
I started with an initial commit and a commit to ignore mail data, secrets and terraform state [E001, E002]. `pre-commit-install` failed with exit 127 [E003]. I retried a few seconds later as `pre-commit install` and it worked [E004]. Then I committed the gitleaks pre-commit hook, "closing #1", and ran `pre-commit install` again after a `git pull` [E005, E006, E007].

**Docs and the prototype folder**
I committed a build log and a prototype folder, then a commit to ignore buildproof evidence [E009, E013]. I left a test note to check what bp captures, then ran `rm BUILD_LOG.md` and `rm -r evidence` [E014, E019, E020]. I committed a README intro [E021]. A stray `p` failed with exit 127 [E022].

**Getting the build log commit through**
After `git add BUILD_LOG.md`, `git commit -m "docs: updated build log"` failed with exit 128 [E026, E027]. A second try exited with 130, probably interrupted [E029]. I then set `git config --global user.email "242280424+PelmeenidHapukoorega@users.noreply.github.com"` and ran `git commit --amend --reset-author --no-edit` [E030, E031]. `git push` failed with exit 1, and `git pull` failed with exit 128 [E032, E033]. I fixed it with `git fetch` and `git reset --soft origin/main`, committed again and pushed successfully [E034, E035, E037, E039].

**Running the bridge as a user service**
I looked at `cat ~/.config/systemd/user/protonmail-bridge.service`, then ran `systemctl --user daemon-reload` and `systemctl --user enable --now protonmail-bridge` [E040, E042, E043]. `systemctl --user status protonmail-bridge` exited with 130, probably because I quit the status view [E044]. I ran `sudo loginctl enable-linger virtualhermit`, checked listeners with `ss -tlnp | grep 127.0.0.1`, and rebooted [E045, E046, E047]. My note: "bridge runs as a systemd user service with linger so it survicves logout and reboots, only listens on localhost" [E048]. I committed and pushed that, then updated the readme with a proton bridge section [E051, E052, E054, E056, E058].

**Python venv for the mail sorter**
`cd ~/prototype/mail-sorter` failed with exit 1, but the next commands ran from `~/Project-owed/prototype/mail-sorter` [E059, E061]. I ran `touch python3 -m venv .venv` by mistake, so `source .venv/bin/activate` failed with exit 1 [E062, E063]. I cleaned up with `rm  python3 venv .venv`, but `rm -- -m` failed with exit 1 [E064, E065]. Then `python3 -m venv .venv` and `source .venv/bin/activate` worked [E067, E068]. I wrote a `.env` and ran `pip install python-dotenv` [E069, E071].

**First script: listing folders**
I wrote `list_folders.py`, and `python list_folders.py` failed with exit 1 [E072, E073]. I swapped tabs for spaces with `sed -i 's/\t/    /g' list_folders.py`, but it still failed with exit 1 [E074, E075]. After checking the tail and editing it twice more, the script ran fine [E076, E077, E078, E079]. My note: "first script connects to bridge over starttls and lists folders; cert verification off for now because its localhost only" [E081]. I committed and pushed it [E083, E085]. Running it later from the repo root failed with exit 2, and it worked from the mail-sorter folder [E086, E088].

**Exporting mail to csv**
A commit added a read-only export of the last 60 days of mail to csv, then I merged main and pulled [E089, E090, E092]. `python export_sample.py` failed from the repo root with exit 2, and `cd ~/prototype/email-sorter` failed with exit 1 [E093, E094]. From the right folder it failed with exit 1 [E096]. I checked the `.env` keys with `cut -d= -f1 .env`, and `list_folders.py` still ran [E098, E099]. After pulling a fix for missing brackets on `load_dotenv`, it still failed with exit 1 [E101, E102]. After pulling a fix for a `BODY_PEEK` typo, the export ran [E104, E105]. Both fixes came in through `git pull`, so I probably made them somewhere else [E100, E103]. I checked the output with `wc -l data/mail_sample.csv` and paged through senders and subjects [E106, E107]. A later commit made the export read all mail over 90 days with an html fallback for previews, and that version ran too [E116, E120, E121]. Along the way I updated the readme and build log, then removed the old manual build log [E108, E113, E118].

**Exploration scripts and the hiring domain list**
I ran `python filter_jobs.py` and `python top_senders.py` [E123, E124]. `ython build_domain_list.py` failed with exit 127 from the typo, and `python build_domain_list.py` worked on the retry [E125, E126]. My note: "built hiring system domain list from full mail history, headers only, store platform domains not company subdomains" [E127]. `touch protoype/mail-sorter/hiring_systems.txt` failed with exit 1 from the typo, and the corrected path worked [E129, E130]. `cut -d, -f1,2 data/hiring_domain_candidates.csv` failed with exit 1 from the repo root and worked from the mail-sorter folder [E131, E133]. I committed and pushed the exploration scripts and the domain list [E138, E139].

**Dry-run sorter**
I ran `python sort_dry_run.py` many times in a row, probably tuning it between runs [E141, E142, E143, E144, E146, E147, E148, E149, E151]. One run exited with 130, probably interrupted, and the next run worked [E145, E146]. I checked the noise rules with `grep -n -A10 "NOISE_SUBJECTS = \[" sort_dry_run.py` before the last run [E150, E151]. My note: "sorter dry run matches real mail, added job-progress for next rounds, missing comma glued 2 noise rules together, silent bug" [E154]. `cd Project-owed` failed with exit 1, then `cd ~/Project-owed` worked [E152, E153]. I committed and pushed the dry-run sorter with domain lists, reply detection and the progress folder on proton [E157, E159].

## Takeaway

- The bridge runs as a systemd user service with linger, listening only on localhost [E043, E045, E048].
- The mail sorter connects to the bridge, exports mail to csv, and has a hiring system domain list [E079, E120, E126, E138].
- The sorter is still a dry run, and my note says it matches real mail [E154, E157].
- A missing comma had silently glued two noise rules together [E154].
- The build log commit failed on author and push problems until I amended the author and did a soft reset to `origin/main` [E027, E031, E032, E035, E039].
- The export needed two fixes, one for `load_dotenv` brackets and one for a `BODY_PEEK` typo, before it ran [E101, E104, E105].
- Most of the other failures were typos or running a command from the wrong folder, and each had a working retry right after [E003, E004, E125, E126, E129, E130, E131, E133].
- Cert verification is off for now because the bridge is localhost only [E081].
- Nothing in these events moves real mail yet, only the dry run [E157].
