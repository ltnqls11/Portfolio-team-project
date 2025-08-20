import os
import smtplib
from email.mime.text import MIMEText
from typing import Dict
from dotenv import load_dotenv


load_dotenv()


def send_email_via_smtp(to_addr: str, subject: str, body: str) -> Dict[str, str]:
    email_addr = os.getenv('GMAIL_EMAIL')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))

    if not email_addr or not app_password:
        raise RuntimeError("SMTP 환경변수(GMAIL_EMAIL/GMAIL_APP_PASSWORD)가 필요합니다")

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(email_addr, app_password)

    msg = MIMEText(body, _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = email_addr
    msg['To'] = to_addr

    smtp.sendmail(email_addr, [to_addr], msg.as_string())
    smtp.quit()
    return {"status": "sent", "to": to_addr}

