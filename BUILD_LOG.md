# Setting up the Project-owed repo with a gitleaks hook and bridge notes

## Intent

- I set up a new repo called Project-owed and ignored mail data, secrets and terraform state from the start [E001, E002].
- I added a gitleaks pre-commit hook, and the commit says it closes #1 [E005].
- My notes say the bridge runs natively with systemd, not docker, "because no official image and it handles my decrypted mail" [E011].
- My notes also say the bridge "needs pass with passphrase-free gpg key so the server login is the protection" [E012].
- The events don't show what the project as a whole is for. The commits only say there is a README intro and a "project story overall" [E021].

## Build

**Setting up the repo**
I made the initial commit [E001]. Then I committed a change to ignore mail data, secrets and terraform state [E002].

**Adding the pre-commit hook**
My first try was `pre-commit-install`, and it failed with exit 127 [E003]. A few seconds later I ran `pre-commit install` with a space, and that worked, so it looks like a typo fix [E004]. I committed the gitleaks pre-commit hook [E005]. After that I ran `git pull` and `pre-commit install` again [E006, E007].

**Docs and prototype folder**
I pulled again and committed a build log and a prototype folder [E008, E009]. I wrote down two notes about the bridge: it runs natively with systemd, and it needs pass with a passphrase-free gpg key [E011, E012]. Then I committed the prototype folder and ignored the buildproof evidence [E013].

**Testing what buildproof captures**
I left a note: "test: checking what bp captures" [E014]. I checked `git status` and read the build log with `cat BUILD_LOG.md` [E016, E018]. Then I deleted it with `rm BUILD_LOG.md` and removed the evidence folder with `rm -r evidence` [E019, E020].

**README and wrap-up**
I committed the README intro and the overall project story [E021]. Right after that I ran `p`, which failed with exit 127. There is no retry in these events [E022]. I read `BUILD_LOG.md` again, so the file was back by then [E023]. I finished with a `git pull` [E024].

## Takeaway

- The repo exists. Mail data, secrets and terraform state are ignored, and a gitleaks pre-commit hook is committed [E002, E005].
- The `pre-commit-install` failure was fixed by running `pre-commit install` [E003, E004].
- The `p` command failed with exit 127, and there is no retry in these events [E022].
- The bridge setup decisions (systemd, pass with a passphrase-free gpg key) are only in my notes. These events don't show any commands that actually set up the bridge [E011, E012].
- README and docs are committed [E009, E021].
