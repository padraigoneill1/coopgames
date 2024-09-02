import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



def send_email(game_name):
    # Mailtrap SMTP server configuration
    smtp_host = 'sandbox.smtp.mailtrap.io'
    smtp_port = 2525
    MAILTRAP_USERNAME = os.getenv('MAILTRAP_USERNAME')
    MAILTRAP_PASSWORD = os.getenv('MAILTRAP_PASSWORD')
    smtp_user = MAILTRAP_USERNAME
    smtp_pass = MAILTRAP_PASSWORD

    # Email content
    subject = "New Game Added to DynamoDB"
    body = f"A new game has been added: {game_name}"

    # Create a MIMEText object
    msg = MIMEMultipart()
    msg['From'] = "sender@example.com"
    msg['To'] = "recipient@example.com"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using Mailtrap's SMTP server
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()

            print("A")
            server.login("MAILTRAP_USERNAME", "MAILTRAP_PASSWORD")
            print("B")
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            print("C")
            print(f"Email sent successfully to {msg['To']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def process_record(record):
    game_name = record['name']
    send_email(game_name)

def main():
    # Simulate a new record from DynamoDB
    simulated_record = {
        'id': '196161',
        'name': "LiMiT's Escape Room Games",
        'multiplayer_modes': [{'id': 18654, 'splitscreen': False}],
        'first_release_date': '2022-09-01',
        'platforms': ['PC'],
        'genres': ['Puzzle'],
        'summary': 'A fun escape room game.',
        'storyline': 'Solve puzzles to escape.',
        'cover_url': 'https://example.com/cover.jpg',
        'total_rating': 7.5,
        'total_rating_count': 123,
        'involved_companies': ['Example Studio']
    }

    # Process the simulated record
    process_record(simulated_record)

if __name__ == "__main__":
    main()
