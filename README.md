# Project-owed
Turning employer silence into answers: feedback requests and GDPR data access requests for job seekers

The initial problem: Unemployment.

I have been applying for jobs for a bit over a month now and while ive gotten actual constructive feedback from just 2 companies there is silence on 90% on them and the only reason i got any feedback in the first place was because i asked for it specifically.

So i started thinking on building something for myself where it automatically categorises jobs ive already applied to, jobs i heard back from with positive responses, and trash job responses with automatic replies and feedback where i wasnt selected.

Another thing i thought on is the other few times ive been unemployed and struggles i personally faced and what others have been facing and job market overall.

So i went down the rabbit hole and realised that 94% of people who apply to jobs actually want real feedback from the potential employer, something that i consider a very basic thing to do and yet? No one does it at scale.

Most job seekers get ghosted and almost nobody gets feedback unless you ask for it specifically and even then there is a good chance you wont get any.

Then eventually i came across a post on linkedin from April earlier this year by Amanda Lamont:

https://www.linkedin.com/posts/ajlamont_i-submitted-a-gdpr-subject-access-request-share-7449691508812804096-An04/

The takeaway from this is the following: After 6 hours of interviews and case study with no feedback, she didnt get the job.

So what did she do? She used GDPR data access request to get her interview records from the company which then showed that the entire panel had voted to hire her and that a single directors note about her career history was what blocked it, the blocker was that she worked for a startup at one point in her career.

Another similar case that happend in germany and it went to labour court and the company had to pay them around 5000 Eur since they handled that data request poorly.

This gave me an idea to expand on it: In the EU you are legally entitled to the data a company holds on you, even if you havent worked there, including recruiter notes and scores. Amanda used exactly that: Article 15 of GDPR in the EU.

So my approach to this is the following: Wait for the deadline where the job listing expires > ask politely for feedback > request your data if you are ignored > track deadline, send reminders > escalate if needed. Where? Data protection inspectorate.

Checked the legal ground properly. Official EU guidance names interview notes explicitly and Estonian law adds a right to a written explanation when discrimination is genuinely suspected. 

My motivation with it is not to make any money, im building it for myself and other people in the same position as me because silence after an application is unfair even if i can understand that there may be a vast amount of candidates. The law however already says that we are owed an answer.

## Idea itself in short

**Problem:** Most job seekers get ghosted and almost nobody gets a feedback

**Solution:** Feedback ladder, polite request first, then data access request if ignored, with deadlines, reminders and escalation tracked for you. 

**Honest promise:** Not to "find out why" but "get everything they wrote down about you"

**First user:** Obviously myself

I have initial doc with other caveats like how long employers are actually holding onto your data if you have only applied to a company and never work there, employers can extend deadline after data request, legally they are obligated to hand over everything about you in the first 30 days since the request but they can extend it for up to 2 months. 

Companies have different retention policies when it comes to data so i intend to build a scraper that scans job listings policy about it as well, if it doesnt find anything about it there, ill find a way to get that information from companies own website and policy which is public information.

## Building the idea itself

Ive set up tools on my server so here im gonna explain each step what im building, key commands and decisions i made during and overall progress in plain english, while also having a `BUILD_LOG.md` at the root.

A week ago i created a simple tool for myself using bpnote and Atuin. Basically Atuin records every command in the scoped path where i do my work, and when i enter `bp` it will then link to claude and write a simple build log with all commands ive used so far, log them in the build log for raw format, since i got annoyed with documentation by explcitly going block for block and it started to take away too much time from me, felt like most of my work was documenting instead of implementing.

Current progress, repo done, secret scanning and push protection, `.gitignore` (mail data, secrets, terraform, evidence/), gitleaks pre-commit on both PC and server.

Tested the buildproof tool, only captures commands run inside `~/Project-owed`.

Proton bridge on the server is installed and credential store set up, logged in and mailbox now synced. Bridge service file is written but not enabled as of yet. 

My current goal is to have the server working and automating emails like clockwork.

## Proton mail bridge on the server

Proton encrypts everything so normal mail programs and scripts, bridge fixes that, runs on my server and decrypts my mail locally and makes it available like ordinary mail server but onl on the server itself as localhost so nothing is exposed to my network.

Installed it from protons official .deb package. Needed a place to store its login, so i set up `pass` with a gpg key. The key has no passphrase because bridge doesnt work with one so the server login itself is the protection.

Logged in through bridges cli and let the mailbox sync which took a while. After that i turned it into a systemd user service so it runs in the background without a terminal open. `enable` makes it start at boot, `--now` starts it right away and `linger` keeps it running even when i log out of ssh. Tested it with a reboot and it came back up on its own.

Went with native install and systemd instead of docker because there is no official docker image and bridge handles my decrypted mail, so i didnt want to trust a third party image with that.

Result: bridge runs 24/7, survives reboots and logouts and only listens on localhost, port 1143 for reading mail (IMAP) and 1025 for sending (SMTP).

Next up is the mail sorter, small python script connecting to the bridge and sorting my job mail into confirmations, rejections and actual human feedback and job listings.

## Mail sorter

