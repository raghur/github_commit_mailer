from unittest import TestCase
from mock import Mock
from githubmailer import Mailer
import json

class MailerTests(TestCase):
    
    def setUp(self):
        self.subjectTemplate = Mock()
        self.messageTemplate = Mock()
        self.mailer = Mailer("a",  "b", "c", 100,self.subjectTemplate, self.messageTemplate)
        self.mailer.mailer = Mock()
    def tearDown(self):
        pass
    def test_should_create_mailer(self):
        pass
    def test_should_send_mails(self):
        commits=json.loads("""{"commits": "ddd"}""")
        self.mailer.send_mails(commits)

        self.subjectTemplate.render.called_with(json=commits,commits="ddd" )

