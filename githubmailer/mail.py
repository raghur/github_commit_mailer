
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

