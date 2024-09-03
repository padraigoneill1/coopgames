import os
import json
import boto3
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv
from decimal import Decimal


# Load environment variables from a .env file
load_dotenv()

# LocalStack and AWS configuration

SQS_ENDPOINT_URL = os.getenv('SQS_ENDPOINT_URL')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')
DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
AWS_REGION = os.getenv('AWS_REGION')
MESSAGES_TO_PROCESS = int(os.getenv('MESSAGES_TO_PROCESS'))

# Initialize AWS clients
sqs = boto3.client('sqs', endpoint_url=SQS_ENDPOINT_URL, region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT_URL, region_name=AWS_REGION)

# Get the DynamoDB table
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def process_message(message_body):
    game = json.loads(message_body, parse_float=Decimal)

    # Check for split-screen multiplayer
    has_splitscreen = any(
        mode.get('splitscreen', False)
        for mode in game.get('multiplayer_modes', [])
    )

    if has_splitscreen:
        # Construct the item for DynamoDB
        item = {
            'id': str(game['id']),
            'name': game.get('name'),
            'first_release_date': game.get('first_release_date', 'N/A'),
            'platforms': game.get('platforms', []),
            'genres': game.get('genres', []),
            'multiplayer_modes': game.get('multiplayer_modes', []),
            'summary': game.get('summary', 'N/A'),
            'storyline': game.get('storyline', 'N/A'),
            'cover_url': game.get('cover_url', 'N/A'),
            'total_rating': game.get('total_rating', 0),
            'total_rating_count': game.get('total_rating_count', 0),
            'involved_companies': game.get('involved_companies', [])
        }

        try:
            response = table.put_item(
                Item=item,
                ConditionExpression=Attr('id').not_exists()  # Only add the item if 'id' doesn't already exist
            )
            print(f"Added game to DynamoDB: {response}")
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Game with id {item['id']} already exists. Skipping.")


def receive_and_process_messages():
    processed_messages = 0
    while processed_messages < MESSAGES_TO_PROCESS:
        # Receive a message from SQS
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        messages = response.get('Messages', [])
        if not messages:
            print("No messages to process")
            continue

        for message in messages:
            message_body = message['Body']
            process_message(message_body)

            # Delete the message from SQS after processing
            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )
            print(f"Deleted message from SQS")
            processed_messages  += 1
            if processed_messages >= MESSAGES_TO_PROCESS:
                print(f"Processed {processed_messages} messages, shutting down.")
                return


if __name__ == "__main__":
    receive_and_process_messages()
