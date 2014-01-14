#! /usr/bin/python
# Usage - git_commit_mailer.py <recipients> smtp_user smtp_pass smtp_server port
# What: listens on port 8080. Whenever Github.com pusts with Json encoded commit details, this can send a mail out
#       to the email addresses given above. github should really do this on their own :(
# Credits
#   gmail mail script from http://kutuma.blogspot.in/2007/08/sending-emails-via-gmail-with-python.html
# 

from jinja2 import Template
subject_template = "[{{json.repository.name}}]<{{commit.author.name}}> {{commit.message}} SHA:{{commit.id}}"
message_template = u"""

url: {{commit.url}}<br/>
Timestamp: {{ commit.timestamp }} <br/>
message : {{commit.message}} <br/>
author: {{commit.author.name}} <br/>
<br/>
Stats: <br/>
        {% for path in commit.modified %}
        Modified: {{ path }} <br/>
        {% endfor %}
        {% for path in commit.added %}
        Added: {{ path }} <br/>
        {% endfor %}
        {% for path in commit.removed %}
        Removed: {{ path }} <br/>
        {% endfor %}
<br/>
Diff: <br/>
        {{commit.diff}}
"""
mailtmpl = Template(message_template)
subjecttmpl = Template(subject_template)
# refer to https://help.github.com/articles/post-receive-hooks for info on GitHub's post recieve hook data

import urllib2
from urllib2 import Request
import pygments
import pygments.lexers
import pygments.formatters

class GithubDiffColorizer():
    def __init__(self, , token):
        self.token = token
        self.lexer = pygments.lexers.get_lexer_for_filename("something.diff")
        self.formatter = pygments.formatters.HtmlFormatter(full=True)

    def get_diff_for_commit(repository, owner, sha):
        commit_tmpl = "https://api.github.com/repos/{owner}/{repository}/commits/{sha}"
        headers = {
                "Accept": "application/vnd.github.diff",
                "Authorization" : "token {token}".format(token=self.token)
                }
        url = commit_tmpl.format(owner=owner, repository=repository, sha=sha)
        req = Request(url, None, headers)
        f = urllib2.urlopen(req)
        content = f.read()
        ucontent = unicode (content, "utf-8")
        return ucontent

    def colorize_diffs(json):
        repository = json["repository"]["name"]
        owner = json["repository"]["owner"]["name"]
        for commit in json["commits"]:
            ucontent = get_diff_for_commit(repository, owner, commit["id"])
            hldiff = pygments.highlight(ucontent, lexer, formatter)
            commit["diff"]=hldiff


class Mailer:
    def __init__(self, server, user, passw, recipients, subjectTemplate, messageTemplate):
        """@todo: Docstring for __init__.

        :recipients: @todo
        :subjectTemplate: @todo
        :messageTemplate: @todo
        :returns: @todo

        """
        self.server = server
        self.user = user
        self.password = password
        self.recipients = recipients
        self.subjectTemplate = subjectTemplate
        self.messageTemplate = messageTemplate

    def send_mails(json):
        for commit in json["commits"]:
            subject = self.subjectTemplate.render(json=json, commit=commit)
            message= self.messageTemplate.render(json=json, commit=commit)
            mail(self.recipients ,subject, message )

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
    def do_POST(s):
        """Respond to a POST request."""

        # Extract and print the contents of the POST
        length = int(s.headers['Content-Length'])
        post_data = urlparse.parse_qs(s.rfile.read(length).decode('utf-8'))
        obj = json.loads(post_data['payload'][0])
        #print obj
        self.server.colorizer.colorize_diffs(obj, self.server.token)
        self.server.mailer.send_mails(obj)
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

class MyServer(SocketServer.ThreadingTCPServer):
    def __init__(self, server_address, colorizer, mailer, token):
        SocketServer.ThreadingTCPServer.__init__(self, server_address, CustomHandler)
        self.colorizer = colorizer
        self.mailer = mailer
        self.token = token

def parse_args(argv):
    parser = argparse.ArgumentParser(description = """Handle github.com post-recieve-hook JSON payload and send email notifications.
    See https://help.github.com/articles/post-receive-hooks""")
    parser.add_argument('-s', '--smtp-server', dest='server', default="smtp.gmail.com", help="SMTP server to use for outgoing email(default: smtp.gmail.com)")
    parser.add_argument('-u', '--user', dest= 'user', help="SMTP user name. Just use your gmail username if using gmail", required=True)
    parser.add_argument('-p', '--pass', dest= 'passw', help="SMTP password", required=True)
    parser.add_argument('-P', '--port', type=int, dest= 'port', default="8080", help="Port to listen on (default- 8080)")
    parser.add_argument('-t', '--token', dest= 'token', help="OAuth Token", required=True)
    parser.add_argument('-d', '--with-diff',  dest='with_diff', help="Include Diffs inline", default=True)
    parser.add_argument('recipients',   nargs="+", help="Recipient email address(es)")
    args = parser.parse_args(argv)
    #print args
    return args

def main(sysargv=sys.argv):
    args = parse_args(sysargv)
    githubColorizer = GithubDiffColorizer(args.token)
    mailer = Mailer(args.server, args.user, args.passw, args.recipients, subjecttmpl, mailtmpl)
    httpd = MyServer(('0.0.0.0', args.port), githubColorizer, mailer, args.token)
    print "serving at port", args.port
    httpd.serve_forever()

if __name__ == '__main__':
    # print sys.argv
    main()