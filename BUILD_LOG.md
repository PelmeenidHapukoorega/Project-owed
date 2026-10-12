# Setting up Project-owed with a gitleaks hook and Proton Mail Bridge as a user service

## Intent

I set up the Project-owed repo so it ignores mail data, secrets and terraform state [E002]. I added a gitleaks pre-commit hook, which closed issue #1 [E005]. The main piece was running Proton Mail Bridge on the server. In my words: "bridge runs natively with systemd, not docker because no official image and it handles my decrypted mail" [E011]. Also: "bridge needs pass with passphrase-free gpg key so the server login is the protection" [E012]. Along the way I kept a build log and README in the repo [E009, E021, E037, E051, E054].

## Build

**Starting the repo and the pre-commit hook**
I made the initial commit and then a commit to ignore mail data, secrets and terraform state [E001, E002]. My first try, `pre-commit-install`, failed with exit 127 [E003]. I retried a few seconds later with `pre-commit install`, and it worked [E004]. Then I committed the gitleaks pre-commit hook [E005]. After a `git pull` I ran `pre-commit install` again [E006, E007].

**Docs and prototype folder**
I committed a build log and a prototype folder [E009]. Later I committed the prototype folder again and set the repo to ignore buildproof evidence [E013].

**Testing the capture tool**
I left a note: "test: checking what bp captures" [E014]. After that I read the build log and removed it and the evidence folder with `rm BUILD_LOG.md` and `rm -r evidence` [E018, E019, E020]. This was probably cleanup after the test [E014, E020].

**Committing the build log, with failures**
I committed a README intro and project story [E021]. Right after, a command `p` failed with exit 127 [E022]. It was probably a typo, and there was no retry in these events [E022]. I pulled, staged the log with `git add BUILD_LOG.md`, and ran `git commit -m "docs: updated build log"`, which failed with exit 128 [E024, E026, E027]. I ran the same commit again and it ended with exit 130 [E029]. Next I set `git config --global user.email "242280424+PelmeenidHapukoorega@users.noreply.github.com"` and ran `git commit --amend --reset-author --no-edit` [E030, E031]. That probably fixed the author identity on the commit [E030, E031].

**Getting the push through**
`git push` failed with exit 1 [E032]. Then `git pull` failed with exit 128 [E033]. I ran `git fetch` and `git reset --soft origin/main`, checked `git status`, and committed again with `git commit -m "docs: updated build log"` [E034, E035, E036, E038]. That made commit 8f5273d [E037]. Then `git push` succeeded [E039].

**Running the bridge as a systemd user service**
I looked at the unit file with `cat ~/.config/systemd/user/protonmail-bridge.service` [E040]. I ran `systemctl --user daemon-reload` and then `systemctl --user enable --now protonmail-bridge` [E042, E043]. `systemctl --user status protonmail-bridge` ended with exit 130 [E044]. I probably quit it with Ctrl+C, but the events don't show that [E044]. I ran `sudo loginctl enable-linger virtualhermit` and checked listening ports with `ss -tlnp | grep 127.0.0.1` [E045, E046]. Then I ran `sudo reboot` [E047]. My note after that: "bridge runs as a systemd user service with linger so it survicves logout and reboots, only listens on localhost" [E048].

**Recording it**
I committed and pushed the build log with the message "docs: build log, bridge running as service" [E049, E050, E051, E052]. After a `git pull`, commit 08aec51 updated the README with a Proton Bridge section [E053, E054].

## Takeaway

- The gitleaks pre-commit hook is committed and installed [E005, E007].
- Proton Mail Bridge is enabled as a systemd user service, and linger is on [E043, E045]. My note says it survives logout and reboots and only listens on localhost [E048].
- The events don't record any status check after the reboot [E047, E048].
- The build log commit had a rough path. It failed with exit 128 and exit 130, the push failed with exit 1, and the pull failed with exit 128 [E027, E029, E032, E033]. A fetch, a soft reset and a new commit got it pushed [E034, E035, E038, E039].
- The `p` failure (exit 127) has no retry in these events [E022].
- Docs and the README are pushed up to the bridge service section [E052, E054].
