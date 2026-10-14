# Proton Bridge as a systemd service and a first job mail sorter

## Intent

The repo starts with an initial commit and a gitignore for "mail data, secrets and terraform state" [E001, E002]. One part of the work is running Proton Mail Bridge. My note says it "runs natively with systemd, not docker because no official image and it handles my decrypted mail" [E011]. The other part is a mail sorter prototype. It first lists folders, then exports mail to CSV, then does a dry run, and finally copies job mail into folders on Proton [E083, E089, E157, E221]. Along the way I also added a gitleaks pre-commit hook and kept a build log [E005, E009]. The events don't say what the bigger project is for beyond this.

## Build

**Repo and pre-commit hook**
`pre-commit-install` failed with exit 127 [E003]. A few seconds later `pre-commit install` worked, which looks like a fix for the typo [E004]. I committed "chore: added gitleaks pre commit hook closing #1" and ran `pre-commit install` again after a pull [E005, E006, E007]. Then I added the build log and a prototype folder, and set buildproof evidence to be ignored [E009, E013].

**Notes before the bridge work**
I wrote that the "bridge needs pass with passphrase-free gpg key so the server login is the protection" [E012]. I also wrote a test note, "checking what bp captures" [E014]. After that I removed the old log and evidence with `rm BUILD_LOG.md` and `rm -r evidence` [E019, E020].

**A messy commit and push**
A command `p` failed with exit 127 [E022]. Then `git commit -m "docs: updated build log"` failed with exit 128 [E027]. The retry ended with exit 130 [E029]. Next I ran `git config --global user.email "242280424+PelmeenidHapukoorega@users.noreply.github.com"` and `git commit --amend --reset-author --no-edit`, probably to fix the commit author [E030, E031]. After that `git push` failed with exit 1 and `git pull` failed with exit 128 [E032, E033]. I recovered with `git fetch` and `git reset --soft origin/main`, committed again, and that push worked [E034, E035, E038, E039].

**Bridge as a user service**
I looked at `~/.config/systemd/user/protonmail-bridge.service` and ran `systemctl --user daemon-reload` and `systemctl --user enable --now protonmail-bridge` [E040, E042, E043]. `systemctl --user status protonmail-bridge` ended with exit 130, probably because I quit it by hand [E044]. Then I ran `sudo loginctl enable-linger virtualhermit`, checked ports with `ss -tlnp | grep 127.0.0.1`, and rebooted [E045, E046, E047]. My note: "bridge runs as a systemd user service with linger so it survicves logout and reboots, only listens on localhost" [E048]. I committed this to the build log and the README [E051, E054].

**First script: listing folders**
`cd ~/prototype/mail-sorter` failed because that path was wrong [E059]. I typed `touch python3 -m venv .venv` by mistake, so `source .venv/bin/activate` failed [E062, E063]. I cleaned up with `rm  python3 venv .venv`, and `rm -- -m` failed with exit 1 [E064, E065]. After that, `python3 -m venv .venv` and activating it worked [E067, E068]. I wrote a `.env` and ran `pip install python-dotenv` [E069, E071]. `python list_folders.py` failed twice with exit 1 [E073, E075]. Between those runs I tried `sed -i 's/\t/    /g' list_folders.py`, probably to fix indentation [E074]. After more editing in nano it ran [E077, E078, E079]. My note: "first script connects to bridge over starttls and lists folders; cert verification off for now because its localhost only" [E081]. I committed and pushed it [E083, E085]. A later run from the repo root failed with exit 2, and it worked from the script folder [E086, E088].

**Exporting mail to CSV**
I committed a "read only export of last 60 days of mail to csv" [E089]. `python export_sample.py` failed with exit 2 from the repo root [E093]. Next, `cd ~/prototype/email-sorter` failed [E094]. From the right folder it still failed with exit 1 [E096]. I checked the keys with `cut -d= -f1 .env` [E098]. I pulled "fix: missing brackets on load_dotenv", but the run failed again with exit 1 [E101, E102]. After pulling "fix: BODY_PEEK typo in fetch" it worked, and I counted the rows with `wc -l data/mail_sample.csv` [E104, E105, E106]. A later commit made the export read all mail over 90 days with an HTML fallback for previews, and I ran it again [E116, E120, E121].

**Exploring and building a domain list**
I ran `python filter_jobs.py` and `python top_senders.py` [E123, E124]. `ython build_domain_list.py` failed with exit 127, and the corrected `python build_domain_list.py` worked [E125, E126]. My note: "built hiring system domain list from full mail history, headers only, store platform domains not company subdomains" [E127]. The `touch` on a misspelled `protoype` path failed, and the retry worked [E129, E130]. `cut -d, -f1,2 data/hiring_domain_candidates.csv` failed from the repo root and worked from the script folder [E131, E133]. I committed the exploration scripts and the domain list [E138].

**Dry-run sorter**
I ran `python sort_dry_run.py` over and over [E141, E142, E143, E144, E146, E147, E148, E149, E151]. One run ended with exit 130 [E145]. I looked at the noise rules with `grep -n -A10 "NOISE_SUBJECTS = \[" sort_dry_run.py` [E150]. My note: "sorter dry run matches real mail, added job-progress for next rounds, missing comma glued 2 noise rules together, silent bug" [E154]. `cd Project-owed` failed, and `cd ~/Project-owed` worked [E152, E153]. I committed the dry-run sorter "with domain lists, reply detection and progress folder on proton" [E157].

**First real run**
`python sort_dry_run.py --aply --limit 1` failed with exit 2 because of a typo, and `python sort_dry_run.py --apply --limit 1` worked [E172, E173]. Three grep attempts failed: a bare `grep` (exit 2), one with no file (exit 130), and `grep -i -E "however|decided|regret|other (candidates|applicants)" data/dry_run.csv | grep Job-Confirmations` (exit 1) [E175, E176, E177]. After those I used small Python one-liners on `data/dry_run.csv` to count folders and reasons and to read the previews [E178, E179]. I ran `python sort_dry_run.py --apply --limit 5` and checked `data/moves_log.csv` [E182, E183, E185]. Then I ran `python sort_dry_run.py --apply` [E186]. My note: "limit 1 caught rejection filed as confirmation because subject was friendly, now reads bodies and not only subjects" [E213]. Another note says the full run "still caught feedback emails and sent a few of them under rejections. Thinking on how to tackle that, duplication perhaps?" [E187].

**Replies to rejections and the second run**
`python sort_dry` failed with exit 2, and the full name worked [E189, E190]. My note: "reply to a rejection quotes the rejection so conversation check now runs before rejection wording and quoted text is stripped, 2nd run planned 0 moves" [E191, E215]. The sorter "skips anything already in a job folder by message id" [E214]. For screenshots, I checked the bridge again [E193]. `systemctl --user status protonmail-bridge` ended with exit 130 again, and `ss -tlnp | grep 127.0.0.1` worked [E194, E195]. I counted the logged moves and ran `python folder_counts.py` [E197, E198]. My notes on design: "copy instead of move since imported mail only lives in all mail so nothings ever deleted" and "targets are folders only" [E211, E212].

**Committing**
`get diff --stat` failed with exit 127, and `git diff --stat` worked [E201, E202]. `git add prototype/email-sorter/folder_counts.py` failed with exit 128, and the `mail-sorter` path worked [E205, E206]. I committed and pushed the folder count script [E207, E209]. `cat ~/home/virtualhermit/Project-owed/BUILD_LOG.md` and `cat ~ BUILD_LOG.md` both failed with exit 1, and there's no successful retry of that cat in these events [E216, E217]. I committed "sorter can copy job mail into folders, tested with --limit" and pushed [E221, E223]. Last, I grepped `evidence/events.md` for passwords, tokens and IPs, probably to check it before publishing [E224].

## Takeaway

- Proton Bridge runs as a systemd user service with linger and listens on localhost only [E043, E045, E048].
- The sorter can copy job mail into Proton folders, and it was tested with `--limit 1` and `--limit 5` before the full run [E173, E182, E186, E221].
- After the reply fix, the second run planned 0 moves [E191].
- Feedback emails landing under rejections was an open question in my note [E187]. These events don't show whether I tried the duplication idea.
- Cert verification was off "for now" [E081]. There's no event where I turn it back on.
- Reading `BUILD_LOG.md` with cat failed twice, with no successful retry in these events [E216, E217].
