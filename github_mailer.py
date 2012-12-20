#! /bin/python
# Usage - git_commit_mailer.py <recipients> smtp_user smtp_pass smtp_server port
# What: listens on port 8080. Whenever Github.com pusts with Json encoded commit details, this can send a mail out
#       to the email addresses given above. github should really do this on their own :(
# Credits
#   gmail mail script from http://kutuma.blogspot.in/2007/08/sending-emails-via-gmail-with-python.html
# 
import argparse
parser = argparse.ArgumentParser(description = """Handle github.com post-recieve-hook JSON payload and send email notifications.
See https://help.github.com/articles/post-receive-hooks""")
parser.add_argument('-s', '--smtp-server', dest='server', default="smtp.gmail.com", help="SMTP server to use for outgoing email(default: smtp.gmail.com)")
parser.add_argument('-u', '--user', dest= 'user', help="SMTP user name. Just use your gmail username if using gmail", required=True)
parser.add_argument('-p', '--pass', dest= 'passw', help="SMTP password", required=True)
parser.add_argument('-P', '--port', type=int, dest= 'port', default="8080", help="Port to listen on (default- 8080)")
parser.add_argument('-t', '--token', dest= 'token', help="OAuth Token", required=True)
parser.add_argument('-d', '--with-diff',  dest='with_diff', help="Include Diffs inline", default=True)
parser.add_argument('recipients',   nargs="+", help="Recipient email address(es)")
args = parser.parse_args()
#print args

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

# refer to https://help.github.com/articles/post-receive-hooks for info on GitHub's post recieve hook data

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

def mail(to, subject, text, attach = None):
   msg = MIMEMultipart()

   msg['From'] = args.user
   msg['To'] = ",".join(to)
   msg['Subject'] = subject

   msg.attach(MIMEText(text, 'html', _charset='utf-8'))

   if (attach):
       part = MIMEBase('application', 'octet-stream')
       part.set_payload(open(attach, 'rb').read())
       Encoders.encode_base64(part)
       part.add_header('Content-Disposition',
               'attachment; filename="%s"' % os.path.basename(attach))
       msg.attach(part)

   mailServer = smtplib.SMTP(args.server, 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(args.user, args.passw)
   mailServer.sendmail(args.user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()

import urllib2
from urllib2 import Request
import pygments
import pygments.lexers
import pygments.formatters
lexer = pygments.lexers.get_lexer_for_filename("something.diff")
formatter = pygments.formatters.HtmlFormatter(full=True)
def colorize_diffs(json):
    """@todo: Docstring for colorize_diffs

    :json: @todo
    :returns: @todo

    """
    headers = {
            "Accept": "application/vnd.github.diff",
            "Authorization" : "token {token}".format(token=args.token)
            }
    commit_tmpl = "https://api.github.com/repos/{owner}/{repository}/commits/{sha}"
    repository = json["repository"]["name"]
    owner = json["repository"]["owner"]["name"]
    for commit in json["commits"]:
        url = commit_tmpl.format(owner=owner, repository=repository, sha=commit["id"])
        req = Request(url, None, headers)
        f = urllib2.urlopen(req)
        content = f.read()
        ucontent = unicode (content, "utf-8")
        hldiff = pygments.highlight(ucontent, lexer, formatter)
        commit["diff"]=hldiff 

from jinja2 import Template
mailtmpl = Template(message_template)
subjecttmpl = Template(subject_template)

def send_mails(json):
    """@todo: Docstring for send_mails

    :json: @todo
    :returns: @todo

    """
    for commit in json["commits"]:
        subject = subjecttmpl.render(json=json, commit=commit)
        message= mailtmpl.render(json=json, commit=commit)

        mail(args.recipients ,subject, message )

"""
Serves files out of its current directory.
Doesn't handle POST requests.
"""
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
        colorize_diffs(obj)
        send_mails(obj)
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
httpd = SocketServer.ThreadingTCPServer(('localhost', args.port),CustomHandler)


print "serving at port", args.port
httpd.serve_forever()
