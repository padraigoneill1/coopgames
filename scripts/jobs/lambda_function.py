import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_item = record['dynamodb']['NewImage']
            game_name = new_item['name']['S']

            # Mailtrap SMTP server configuration
            smtp_host = 'sandbox.smtp.mailtrap.io'
            smtp_port = 2525


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
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    print(f"Email sent successfully to {msg['To']}")
            except Exception as e:
                print(f"Failed to send email: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent')
    }
