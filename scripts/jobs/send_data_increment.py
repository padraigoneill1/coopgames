import smtplib

sender = "Private Person <from@example.com>"
receiver = "Padraig <contact.padraig.o.neill@gmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
    server.starttls()
    server.login("MAILTRAP_USERNAME", "MAILTRAP_PASSWORD")
    server.sendmail(sender, receiver, message)