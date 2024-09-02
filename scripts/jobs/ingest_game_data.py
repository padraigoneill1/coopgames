import os
import boto3
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# AWS configuration
SQS_ENDPOINT_URL = os.getenv('SQS_ENDPOINT_URL')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

# Initialize SQS client
sqs = boto3.client('sqs', endpoint_url=SQS_ENDPOINT_URL, region_name='us-east-1')

# Function to send a test message to SQS
def send_test_message_to_sqs():
    test_message = {
        'id': 1,
        'name': 'Test Game',
        'multiplayer_modes': [
            {
                'campaigncoop': True,
                'splitscreen': True,
                'onlinecoop': True
            }
        ]
    }

    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=str(test_message),
        MessageGroupId='testGroup',
        MessageDeduplicationId='testMessage1'
    )

    print(f"Sent test message to SQS: {response['MessageId']}")

# Main function to trigger the test
def main():
    send_test_message_to_sqs()

if __name__ == "__main__":
    main()
