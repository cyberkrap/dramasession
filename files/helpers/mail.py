import os
import time

import requests

from files.helpers.security import *
from files.helpers.config.const import EMAIL

from urllib.parse import quote
from flask import render_template


class EmailDeliveryError(RuntimeError):
	pass


EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "").strip().lower()
EMAIL_FROM = os.environ.get("EMAIL_FROM", EMAIL).strip()
EMAIL_REPLY_TO = os.environ.get("EMAIL_REPLY_TO", "").strip()
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()


def _send_with_resend(to_address, subject, html):
	if not RESEND_API_KEY:
		raise EmailDeliveryError("resend_not_configured")

	payload = {
		"from": EMAIL_FROM,
		"to": [to_address],
		"subject": subject,
		"html": html,
	}
	if EMAIL_REPLY_TO:
		payload["reply_to"] = [EMAIL_REPLY_TO]

	try:
		response = requests.post(
			"https://api.resend.com/emails",
			headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
			json=payload,
			timeout=10,
		)
		response.raise_for_status()
	except requests.RequestException as error:
		raise EmailDeliveryError("resend_delivery_failed") from error

	return True


def _send_with_smtp(to_address, subject, html):
	import smtplib
	from email.mime.text import MIMEText
	from email.utils import formatdate, make_msgid
	import dkim

	msg = MIMEText(html, 'html')
	msg['Subject'] = subject
	msg['From'] = EMAIL_FROM
	msg['To'] = to_address
	msg['Date'] = formatdate()
	msg['Message-ID'] = make_msgid(domain=SITE)

	with open("/dkim_private.pem", "rb") as fh:
		private_key = fh.read()
	headers = b'subject:from:to:date:message-id'
	signature = dkim.sign(
		message=msg.as_bytes(),
		selector=b'default',
		domain=SITE.encode(),
		privkey=private_key,
		headers=headers.split(b':'),
	)
	msg["DKIM-Signature"] = signature.decode().split(': ', 1)[1]

	with smtplib.SMTP('localhost', 25) as server:
		server.sendmail(EMAIL_FROM, [to_address], msg.as_string())
	return True


def send_mail(to_address, subject, html):
	if EMAIL_PROVIDER == "resend":
		return _send_with_resend(to_address, subject, html)
	if EMAIL_PROVIDER in ("", "none", "disabled"):
		raise EmailDeliveryError("email_not_configured")
	if EMAIL_PROVIDER == "smtp":
		return _send_with_smtp(to_address, subject, html)
	raise EmailDeliveryError("email_provider_unavailable")


def send_verification_email(user, email=None):
	if not email:
		email = user.email
	url = f"https://{SITE}/activate"
	now = int(time.time())
	token = generate_hash(f"{email}+{user.id}+{now}")
	params = f"?email={quote(email)}&id={user.id}&time={now}&token={token}"
	link = url + params
	send_mail(
		to_address=email,
		html=render_template("email/email_verify.html", action_url=link, v=user),
		subject=f"Verify your {SITE_NAME} account email",
	)
	return True
