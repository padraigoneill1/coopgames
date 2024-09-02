import os
import json
import boto3
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# AWS configuration
DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
AWS_REGION = os.getenv('AWS_REGION')
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'dynamodb_data.json')

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT_URL, region_name=AWS_REGION)

# Get the DynamoDB table
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def scan_table():
    """
    Scan the DynamoDB table and return all items.
    """
    scan_kwargs = {}
    done = False
    start_key = None
    items = []

    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key

        response = table.scan(**scan_kwargs)
        items.extend(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None

    return items

def save_to_file(data, filename):
    """
    Save the data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, default=str, indent=4)
    print(f"Data saved to {filename}")

def main():
    # Scan the DynamoDB table
    data = scan_table()

    # Save the data to a JSON file
    save_to_file(data, OUTPUT_FILE)

if __name__ == "__main__":
    main()
