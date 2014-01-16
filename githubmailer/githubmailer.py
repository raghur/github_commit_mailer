#! /usr/bin/python
# Usage - git_commit_mailer.py <recipients> smtp_user smtp_pass smtp_server port
# What: listens on port 8080. Whenever Github.com pusts with Json encoded commit details, this can send a mail out
#       to the email addresses given above. github should really do this on their own :(
# Credits
#   gmail mail script from http://kutuma.blogspot.in/2007/08/sending-emails-via-gmail-with-python.html
#

#######################
#######################
# TODO:
# Config file [DONE]
# Interactive mode - call with owner, repo,sha and recipients [DONE]
# service script
# Templates in external files [DONE]
# Class level variables for some things
# move server to separate file
# better logging

import sys
import os
import base64
from mail import SmtpMailer
from jinja2 import Template
import pkg_resources
subject_template = pkg_resources.resource_string(__name__,
                                                 "subject_template.tmpl")
message_template = pkg_resources.resource_string(__name__,
                                                 "message_template.tmpl")
mailtmpl = Template(message_template)
subjecttmpl = Template(subject_template)
# refer to https://help.github.com/articles/post-receive-hooks
# for info on GitHub's post recieve hook data

import urllib2
from urllib2 import Request
import pygments
import pygments.lexers
import pygments.formatters


class GithubDiffColorizer():
    def __init__(self, token):
        self.token = token
        self.lexer = pygments.lexers.get_lexer_for_filename("something.diff")
        self.formatter = pygments.formatters.HtmlFormatter(full=True)
        self.commit_tmpl = "https://api.github.com/repos/{owner}/{repository}/commits/{sha}"
        base64string = base64.encodestring('%s:%s' % (token, "")) \
                             .replace('\n', '')
        self.authorizationHeader = "Basic %s" % base64string

    def make_github_api_call(self, url, headers):
        print url
        req = Request(url, None, headers)
        f = urllib2.urlopen(req)
        content = f.read()
        ucontent = unicode(content, "utf-8")
        return ucontent

    def get_diff_for_commit(self, owner, repository, sha):
        headers = {
            "Accept": "application/vnd.github.diff",
            "Authorization": self.authorizationHeader
        }
        url = self.commit_tmpl.format(owner=owner,
                                      repository=repository,
                                      sha=sha)
        return self.make_github_api_call(url, headers)

    def get_commit(self, owner, repository, sha):
        """@todo: Docstring for get_commit.

        :arg1: @todo
        :returns: @todo

        """
        headers = {
            "Accept": "application/vnd.github.beta+json",
            "Authorization": self.authorizationHeader
        }
        url = self.commit_tmpl.format(owner=owner,
                                      repository=repository,
                                      sha=sha)
        return self.make_github_api_call(url, headers)

    def colorize_diffs(self, owner, repository, sha):
        ucontent = self.get_diff_for_commit(owner,
                                            repository,
                                            sha)
        hldiff = pygments.highlight(ucontent,
                                    self.lexer,
                                    self.formatter)
        return hldiff


class Mailer:
    def __init__(self,
                 server,
                 user,
                 passw,
                 recipients,
                 subjectTemplate,
                 messageTemplate):
        """@todo: Docstring for __init__.

        :recipients: @todo
        :subjectTemplate: @todo
        :messageTemplate: @todo
        :returns: @todo

        """
        self.mailer = SmtpMailer(server, user, passw, 587)
        self.recipients = recipients
        self.subjectTemplate = subjectTemplate
        self.messageTemplate = messageTemplate

    def send_mails(self, commit):
        subject = self.subjectTemplate.render(commit=commit)
        message = self.messageTemplate.render(commit=commit)
        print "sending to: ", self.recipients
        self.mailer.mail(self.recipients, subject, message)

"""
Serves files out of its current directory.
Doesn't handle POST requests.
"""
import argparse
import SocketServer
import SimpleHTTPServer
import urlparse
import json


class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        """Respond to a POST request."""
        print "handling request"
        # Extract and print the contents of the POST
        length = int(self.headers['Content-Length'])
        post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))
        obj = json.loads(post_data['payload'][0])
        for commit in obj["commits"]:
            repository = obj["repository"]["name"]
            owner = obj["repository"]["owner"]["name"]
            diff = self.server.colorizer.colorize_diffs(owner, repository, commit["id"])
            commit["diff"] = diff
            commit["repository"] = repository
            self.server.mailer.send_mails(commit)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


class MyServer(SocketServer.ThreadingTCPServer):
    def __init__(self, server_address, colorizer, mailer):
        SocketServer.ThreadingTCPServer \
            .__init__(self, server_address, CustomHandler)
        self.colorizer = colorizer
        self.mailer = mailer


def parse_args(argv):
    parser = argparse.ArgumentParser(description = """Handle github.com post-recieve-hook JSON payload and send email notifications.
    See https://help.github.com/articles/post-receive-hooks""",
                                     fromfile_prefix_chars='@')
    parser.add_argument('-s',
                        '--smtp-server',
                        dest='server',
                        default="smtp.gmail.com",
                        help="SMTP server to use for outgoing email(default: smtp.gmail.com)")
    parser.add_argument('-u',
                        '--user',
                        dest='user',
                        help="SMTP user name. Just use your gmail username if using gmail",
                        required=True)
    parser.add_argument('-p',
                        '--pass',
                        dest='passw',
                        help="SMTP password",
                        required=True)
    parser.add_argument('-P',
                        '--port',
                        type=int,
                        dest='port',
                        default="8080",
                        help="Port to listen on (default- 8080)")
    parser.add_argument('-t',
                        '--token',
                        dest='token',
                        help="OAuth Token",
                        required=True)
    parser.add_argument('-r',
                        '--repository',
                        dest='repository',
                        help="Repository in 'owner/repo' format")
    parser.add_argument('-c',
                        '--commit',
                        dest='commit',
                        help="commit SHA (usually first 5 chars are sufficient)")
    parser.add_argument('recipients',
                        nargs="+",
                        help="Recipient email address(es)")
    config = os.path.expanduser("~/.github_commit_mailer")
    if (os.path.exists(config)):
        argv = ["@" + config] + argv
    args = parser.parse_args(argv)
    #print args
    return args


def main(sysargv=sys.argv):
    args = parse_args(sysargv[1:])
    githubColorizer = GithubDiffColorizer(args.token)
    mailer = Mailer(args.server,
                    args.user,
                    args.passw,
                    args.recipients,
                    subjecttmpl,
                    mailtmpl)
    if (args.repository and args.commit):
        owner, repo = args.repository.split("/")
        commitresp = json.loads(githubColorizer.get_commit(owner,
                                                           repo,
                                                           args.commit))
        commit = commitresp["commit"]
        commit["id"] = commitresp["sha"]
        diff = githubColorizer.colorize_diffs(owner, repo, commit["id"])
        commit["diff"] = diff
        commit["repository"] = repo
        mailer.send_mails(commit)
    else:
        httpd = MyServer(('0.0.0.0', args.port), githubColorizer, mailer)
        print "serving at port", args.port
        httpd.serve_forever()

if __name__ == '__main__':
    print sys.argv
    main()
