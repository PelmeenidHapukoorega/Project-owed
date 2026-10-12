# Owed build log: Proton Bridge, a mail sorter prototype and dry runs

## Intent

The commits and notes show I'm building a mail sorter on top of Proton Mail Bridge. It reads my mail and sorts job and hiring mail into folders [E083, E089, E157]. The bridge runs natively with systemd, not docker, "because no official image and it handles my decrypted mail" [E011]. The sorter uses a list of hiring system domains built from my full mail history, headers only [E127, E137]. The last sorter commit is a dry-run sorter "with domain lists, reply detection and progress folder on proton" [E157]. The events don't show more than that about the bigger goal [E021, E108].

## Build

**Setting up the repo and the gitleaks hook**
I started the repo and ignored mail data, secrets and terraform state [E001, E002]. `pre-commit-install` failed with exit 127 [E003]. Right after, `pre-commit install` worked, which looks like the fix for a typo [E004]. Then I committed a gitleaks pre-commit hook, "closing #1" [E005]. I ran `pre-commit install` again after a pull [E006, E007].

**Docs and build log housekeeping**
I added a build log and a prototype folder, and set buildproof evidence to be ignored [E009, E013]. I left a test note to check what bp captures, then ran `rm BUILD_LOG.md` and `rm -r evidence` [E014, E019, E020]. I wrote the README intro and project story [E021]. A stray `p` failed with exit 127, with no retry in these events [E022].

**Fixing the commit author and getting the push through**
`git commit -m "docs: updated build log"` failed with exit 128 [E027]. A second try exited with 130 [E029]. Next I ran `git config --global user.email "242280424+PelmeenidHapukoorega@users.noreply.github.com"` and `git commit --amend --reset-author --no-edit` [E030, E031]. Then `git push` failed with exit 1 and `git pull` failed with exit 128 [E032, E033]. I ran `git fetch` and `git reset --soft origin/main`, then committed again [E034, E035, E037, E038]. That push succeeded [E039].

**Running the bridge as a service**
I looked at `cat ~/.config/systemd/user/protonmail-bridge.service` [E040]. Then I ran `systemctl --user daemon-reload` and `systemctl --user enable --now protonmail-bridge` [E042, E043]. `systemctl --user status protonmail-bridge` exited with 130, probably because I quit the status view, but that's a guess [E044]. I ran `sudo loginctl enable-linger virtualhermit` and checked listeners with `ss -tlnp | grep 127.0.0.1`, then rebooted [E045, E046, E047]. My note: "bridge runs as a systemd user service with linger so it survicves logout and reboots, only listens on localhost" [E048]. I also noted the bridge needs pass with a passphrase-free gpg key, "so the server login is the protection" [E012]. I committed the build log and a README section on the bridge [E051, E054, E056].

**Python venv for the mail sorter**
`cd ~/prototype/mail-sorter` failed with exit 1, and the next commands ran in `~/Project-owed/prototype/mail-sorter` [E059, E061]. I ran `touch python3 -m venv .venv` by mistake, and `source .venv/bin/activate` then failed with exit 1 [E062, E063]. I cleaned up with `rm  python3 venv .venv`, but `rm -- -m` failed with exit 1 and there's no retry in these events [E064, E065]. Then `python3 -m venv .venv` and `source .venv/bin/activate` both worked [E067, E068]. I edited `.env` and ran `pip install python-dotenv` [E069, E071].

**First script: listing folders**
I wrote `list_folders.py`, and `python list_folders.py` failed with exit 1 [E072, E073]. I swapped tabs for spaces with `sed -i 's/\t/    /g' list_folders.py`, but the next run failed with exit 1 again [E074, E075]. After checking the tail and editing the file twice more, the script ran fine [E076, E077, E078, E079]. My note: "first script connects to bridge over starttls and lists folders; cert verification off for now because its localhost only" [E081]. I committed and pushed it [E083, E085]. A later run from the repo root failed with exit 2, and the same command worked from the mail-sorter folder [E086, E088].

**Exporting mail to CSV**
A commit added a "read only export of last 60 days of mail to csv" [E089]. `python export_sample.py` failed with exit 2 from the repo root [E093]. `cd ~/prototype/email-sorter` failed with exit 1, and `cd prototype/mail-sorter` worked [E094, E095]. From there the export failed with exit 1 [E096]. I checked the `.env` keys with `cut -d= -f1 .env` and confirmed `list_folders.py` still ran [E098, E099]. A fix commit "missing brackets on load_dotenv" came in by `git pull`, but the export still failed with exit 1 [E100, E101, E102]. A second fix, "BODY_PEEK typo in fetch", came in, and after that the export ran [E103, E104, E105]. I checked the output with `wc -l data/mail_sample.csv` [E106]. I read through it with `python -c "import csv; [print(r['from'][:40].ljust(42), r['subject'][:70]) for r in csv.DictReader(open('data/mail_sample.csv', encoding='utf-8'))]" | less` [E107]. Later a commit changed the export to read all mail over a 90 days period, with an html fallback for previews [E116]. I ran it again and checked the line count [E120, E121]. The old manual build log was removed in a commit [E118].

**Exploration scripts and the hiring domain list**
I ran `python filter_jobs.py` and `python top_senders.py` [E123, E124]. `ython build_domain_list.py` failed with exit 127 because of the typo, and `python build_domain_list.py` worked right after [E125, E126]. My note: "built hiring system domain list from full mail history, headers only, store platform domains not company subdomains" [E127]. `touch protoype/mail-sorter/hiring_systems.txt` failed with exit 1 (typo in the path), and the corrected `touch prototype/mail-sorter/hiring_systems.txt` worked [E129, E130]. `cut -d, -f1,2 data/hiring_domain_candidates.csv` failed with exit 1 from the repo root and worked from the mail-sorter folder [E131, E132, E133]. I committed and pushed the scripts and domain list [E137, E138, E139].

**Dry-run sorter**
I ran `python sort_dry_run.py` many times in a row [E141, E142, E143, E144, E146, E147, E148, E149, E151]. One run exited with 130, and the next run succeeded [E145, E146]. I checked the noise rules with `grep -n -A10 "NOISE_SUBJECTS = \[" sort_dry_run.py` [E150]. My note: "sorter dry run matches real mail, added job-progress for next rounds, missing comma glued 2 noise rules together, silent bug" [E154]. `cd Project-owed` failed with exit 1, and `cd ~/Project-owed` worked [E152, E153]. I committed and pushed the dry-run sorter [E157, E158, E159]. After that I updated the build log, and a README commit added a section on dry run tests [E161, E163, E165].

## Takeaway

- The Proton Bridge runs as a systemd user service with linger and listens only on localhost [E043, E045, E048].
- The mail sorter prototype connects to the bridge, exports mail to CSV, builds a hiring domain list and runs a dry-run sort. All of it is committed and pushed [E083, E105, E138, E157, E159].
- The sorter is still a dry run in these events. No event shows it moving real mail [E157].
- Cert verification is off "for now" per my note [E081].
- A missing comma had silently glued two noise rules together. My note names this bug [E154].
- Most failures had a visible retry or fix: the commit and push mess [E039], the venv [E068], `list_folders.py` [E079], the export [E105] and several typos [E004, E126, E130].
- The failures with no retry in these events are `p` [E022], `rm -- -m` [E065] and the `systemctl --user status protonmail-bridge` exit 130 [E044].
