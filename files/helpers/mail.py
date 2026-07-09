import requests
import time

from files.helpers.security import *
from files.helpers.config.const import EMAIL

from urllib.parse import quote

from flask import render_template


if SITE == 'rdrama.net':
	def send_mail(to_address, subject, html):
		url = f"https://deuxrama.net/email"
		data = {"from": EMAIL,
				"to": to_address,
				"subject": subject,
				"html": html,
				}
		requests.post(url, data=data)
else:
	import smtplib
	from email.mime.text import MIMEText
	from email.utils import formatdate, make_msgid
	import dkim

	def send_mail(to_address, subject, html):
		msg = MIMEText(html, 'html')

		msg['Subject'] = subject
		msg['From'] = EMAIL
		msg['To'] = to_address
		msg['Date'] = formatdate()
		msg['Message-ID'] = make_msgid(domain=SITE)

		headers = ["To", "From", "Subject", "Message-ID"]
		with open("/dkim_private.pem") as fh:
			dkim_private = fh.read()
		sig = dkim.sign(
						message=msg.as_string().encode("ascii"),
						selector='d'.encode("ascii"),
						domain=SITE.encode("ascii"),
						privkey=dkim_private.encode("ascii"),
						include_headers=headers
					)
		msg["DKIM-Signature"] = sig.decode("ascii").lstrip("DKIM-Signature: ")

		with smtplib.SMTP('localhost', 25) as server:
			server.sendmail(EMAIL, [to_address], msg.as_string())


def send_verification_email(user, email=None):
	if not email:
		email = user.email

	url = f"https://{SITE}/activate"
	now = int(time.time())
	token = generate_hash(f"{email}+{user.id}+{now}")
	params = f"?email={quote(email)}&id={user.id}&time={now}&token={token}"
	link = url + params
	send_mail(to_address=email,
			html=render_template("email/email_verify.html",
								action_url=link,
								v=user),
			subject=f"Verify your {SITE_NAME} account email"
			)
