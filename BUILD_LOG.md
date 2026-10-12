# Setting up Project-owed with a gitleaks hook and a Proton Mail bridge service

## Intent

I started the repo and set it to ignore mail data, secrets and terraform state [E001, E002]. I added a gitleaks pre-commit hook, which closed issue #1 [E005]. I wanted Proton Mail Bridge to run natively with systemd, not Docker, "because no official image and it handles my decrypted mail" [E011]. The bridge needs pass with a passphrase-free gpg key, "so the server login is the protection" [E012]. The goal was for it to run "as a systemd user service with linger so it survicves logout and reboots, only listens on localhost" [E048]. I also kept a build log and a prototype folder in the repo [E009, E013, E021].

## Build

**Setting up the repo and the pre-commit hook**
I made the initial commit and then a commit that ignores mail data, secrets and terraform state [E001, E002]. My first try, `pre-commit-install`, failed with exit 127 [E003]. I retried a few seconds later with `pre-commit install`, and that worked [E004]. Next I committed the gitleaks hook with `chore: added gitleaks pre commit hook closing #1` [E005]. I pulled and ran `pre-commit install` again after that [E006, E007].

**Docs and the prototype folder**
I committed the build log and the prototype folder [E009]. A later commit added the prototype folder again and set buildproof evidence to be ignored [E013]. I left a note saying I was "checking what bp captures" [E014]. Then I read the build log and removed it with `rm BUILD_LOG.md` and `rm -r evidence`, probably to clear out test output [E018, E019, E020]. After that I committed the README intro and the project story [E021]. Right after that commit, a command `p` failed with exit 127, probably a typo, and there is no retry in these events [E022].

**Committing the updated build log**
I staged the build log with `git add BUILD_LOG.md` [E026]. The first `git commit -m "docs: updated build log"` failed with exit 128 [E027]. A second try exited with 130 [E029]. I then ran `git config --global user.email "242280424+PelmeenidHapukoorega@users.noreply.github.com"` and `git commit --amend --reset-author --no-edit`, so the commit failure was probably about author identity [E030, E031]. `git push` failed with exit 1 [E032]. `git pull` failed with exit 128 [E033]. I fixed this with `git fetch` and `git reset --soft origin/main`, then committed again as `docs: updated build log` [E034, E035, E037, E038]. This time `git push` worked [E039].

**Running the bridge as a systemd user service**
I looked at the unit file with `cat ~/.config/systemd/user/protonmail-bridge.service` [E040]. I ran `systemctl --user daemon-reload` and `systemctl --user enable --now protonmail-bridge`, and both worked [E042, E043]. `systemctl --user status protonmail-bridge` exited with 130 [E044]. I turned on linger with `sudo loginctl enable-linger virtualhermit` [E045]. I probably checked the localhost listeners with `ss -tlnp | grep 127.0.0.1` [E046]. Then I ran `sudo reboot` [E047]. My closing note says the bridge runs with linger and only listens on localhost [E048].

## Takeaway

- The repo has ignore rules for mail data, secrets and terraform state, plus a gitleaks pre-commit hook [E002, E005].
- The `pre-commit-install` failure was fixed by running `pre-commit install` [E003, E004].
- The build log commit failed at first, and so did the push. Both were fixed by setting the email, resetting onto `origin/main` and committing again, and the push went through [E027, E030, E035, E038, E039].
- The bridge user service is enabled and linger is on [E043, E045].
- These events don't show a check after the reboot [E047].
- `systemctl --user status protonmail-bridge` exited with 130, with no retry in these events [E044].
- `p` failed with exit 127, with no retry in these events [E022].
