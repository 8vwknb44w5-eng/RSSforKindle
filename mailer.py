import os
import smtplib
from email.message import EmailMessage


def send_epub(epub_file):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]

    sender = os.environ["SMTP_FROM"]
    receiver = os.environ["KINDLE_EMAIL"]

    msg = EmailMessage()
    msg["Subject"] = "RSS Digest"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("RSS Digest")

    with open(epub_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="epub+zip",
            filename="RSS_Digest.epub",
        )

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)

    print("EPUB enviado correctamente al Kindle.")
