import json
import os
import boto3
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# IGDB and AWS configuration
IGDB_CLIENT_ID = os.getenv('IGDB_CLIENT_ID')
IGDB_ACCESS_TOKEN = os.getenv('IGDB_ACCESS_TOKEN')
SQS_ENDPOINT_URL = os.getenv('SQS_ENDPOINT_URL')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')
AWS_REGION = os.getenv('AWS_REGION')
MESSAGES_TO_PROCESS = int(os.getenv('MESSAGES_TO_PROCESS'))


# Initialize SQS client
sqs = boto3.client('sqs', endpoint_url=SQS_ENDPOINT_URL, region_name=AWS_REGION)

# IGDB API request headers
headers = {
    'Client-ID': IGDB_CLIENT_ID,
    'Authorization': f'Bearer {IGDB_ACCESS_TOKEN}',
}

# Function to fetch games with multiplayer and rating > 5 from IGDB
def fetch_multiplayer_games():
    url = "https://api.igdb.com/v4/games"

    query = f"""
    fields id, name, first_release_date, platforms.name, genres.name, 
           multiplayer_modes.*, summary, storyline, cover.url, 
           total_rating, total_rating_count, involved_companies.company.name;
    where multiplayer_modes != null & total_rating > 5;
    limit {MESSAGES_TO_PROCESS};
    """
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from IGDB: {response.status_code}")
        return []

# Function to send game data to SQS
def send_message_to_sqs(game):
    message_body = {
        'id': game['id'],
        'name': game['name'],
        'first_release_date': game.get('first_release_date', None),
        'platforms': [platform['name'] for platform in game.get('platforms', [])],
        'genres': [genre['name'] for genre in game.get('genres', [])],
        'multiplayer_modes': game.get('multiplayer_modes', []),
        'summary': game.get('summary', None),
        'storyline': game.get('storyline', None),
        'cover_url': game.get('cover', {}).get('url', None),
        'total_rating': game.get('total_rating', None),
        'total_rating_count': game.get('total_rating_count', None),
        'involved_companies': [company['company']['name'] for company in game.get('involved_companies', [])],
    }

    message_body_json = json.dumps(message_body)

    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=str(message_body_json),
        MessageGroupId='multiplayerGames',
        MessageDeduplicationId=str(game['id'])
    )

    print(f"Sent message to SQS: {response['MessageId']}")

# Main function to fetch games and send to SQS
def main():
    games = fetch_multiplayer_games()
    if games:
        for game in games:
            send_message_to_sqs(game)

if __name__ == "__main__":
    main()
