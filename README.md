github_commit_mailer
====================
Python script to send commit emails with colorized diffs when commits are pushed to Github.com

![image](https://raw.github.com/raghur/github_commit_mailer/master/assets/snapshot.png)

## Why
So Github.com offers commit emails in the service hook section but does not include diffs. Git itself allows you to have hook scripts - but this only works if you host your own repository.

I like commit emails with diffs and since none of the existing solutions worked, I wrote this.

## Summary

```
usage: github_mailer [-h] [-s SERVER] -u USER -p PASSW [-P PORT] -t TOKEN
                     [-r REPOSITORY] [-c COMMIT] [-v VERBOSITY]
                     recipients [recipients ...]

positional arguments:
  recipients            Recipient email address(es)

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --smtp-server SERVER
                        SMTP server to use for outgoing email(default:
                        smtp.gmail.com)
  -u USER, --user USER  SMTP user name. Just use your gmail username if using
                        gmail
  -p PASSW, --pass PASSW
                        SMTP password
  -P PORT, --port PORT  Port to listen on (default- 8080)
  -t TOKEN, --token TOKEN
                        OAuth Token
  -r REPOSITORY, --repository REPOSITORY
                        Repository in 'owner/repo' format
  -c COMMIT, --commit COMMIT
                        commit SHA (usually first 5 chars are sufficient)
  -v VERBOSITY, --verbose VERBOSITY
                        Log level: INFO,DEBUG,CRITICAL,WARNING
```

## Github API token

To use this on a repository, you'll need to do two things:

1. Generate an API token to your github account so that the script can retrieve the diff
2. On each repository, configure the post-receive service url (whereever you're running `github_commit_mailer` as a server)

## Installation

I'll be putting this in PyPI soon - till that time install from zip:
```
pip install https://github.com/raghur/github_commit_mailer/archive/master.zip
```

## Give it a spin
If you specify the repo `-r` and commit `-c`, the script runs in interactive mode and sends a commit email and exits. 

## Keeping secrets
If you'd rather not specifiy secrets (smtp password, token) as command line args, you can stick them in a config file -  `~/.github_commit_mailer`. Any arg specified explicitly on the command line overrides a config setting read from the file. Format of the file is one argument per line:

```
-u
abcd@gmail.com
-p
mysecretpass
-t
asfljasdfljasdfljasdf
```

## TODOs

1. ~~Config file~~ [DONE]
1. ~~Interactive mode - call with owner, repo,sha and recipients~~ [DONE]
1. service script
1. ~~Templates in external files~~ [DONE]
1. move server to separate file
1. ~~logging~~ [DONE]

## Credits

1. gmail mail script from http://kutuma.blogspot.in/2007/08/sending-emails-via-gmail-with-python.html
