
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

class SmtpMailer:
    def __init__(self, server, user, password, port):
        """@todo: Docstring for __init__.
        :returns: @todo

        """
        self.server = server
        self.user = user
        self.password = password
        self.port = port

    def mail(to, subject, text, attach = None):
       msg = MIMEMultipart()

       msg['From'] = self.user
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

       mailServer = smtplib.SMTP(self.server, 587)
       mailServer.ehlo()
       mailServer.starttls()
       mailServer.ehlo()
       mailServer.login(self.user, self.passw)
       mailServer.sendmail(self.user, to, msg.as_string())
       # Should be mailServer.quit(), but that crashes...
       mailServer.close()

