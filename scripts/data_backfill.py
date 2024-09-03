import os
import json
import boto3
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from a .env file
load_dotenv()

# IGDB and AWS configuration
IGDB_CLIENT_ID = os.getenv('IGDB_CLIENT_ID')
IGDB_ACCESS_TOKEN = os.getenv('IGDB_ACCESS_TOKEN')
DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
AWS_REGION = os.getenv('AWS_REGION')

# Game ID to fetch
GAME_ID = os.getenv('GAME_ID')

# Initialize AWS DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT_URL, region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# IGDB API request headers
headers = {
    'Client-ID': IGDB_CLIENT_ID,
    'Authorization': f'Bearer {IGDB_ACCESS_TOKEN}',
}

def fetch_game_by_id(game_id):
    url = "https://api.igdb.com/v4/games"

    query = f"""
    fields id, name, first_release_date, platforms.name, genres.name, 
           multiplayer_modes.*, summary, storyline, cover.url, 
           total_rating, total_rating_count, involved_companies.company.name;
    where id = {game_id} & first_release_date <= {int(datetime.now().timestamp())} & multiplayer_modes != null;
    limit 1;
    """
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        games = response.json()
        if games:
            return games[0]
        else:
            print("No game found with the given ID or the game has not been released yet.")
            return None
    else:
        print(f"Failed to fetch data from IGDB: {response.status_code}")
        return None

def backfill_dynamodb(game):
    item = {
        'id': str(game['id']),
        'name': game.get('name'),
        'first_release_date': game.get('first_release_date', 0),  # Store as Unix timestamp
        'platforms': [platform['name'] for platform in game.get('platforms', [])],
        'genres': [genre['name'] for genre in game.get('genres', [])],
        'multiplayer_modes': game.get('multiplayer_modes', []),
        'summary': game.get('summary', 'N/A'),
        'storyline': game.get('storyline', 'N/A'),
        'cover_url': game.get('cover', {}).get('url', 'N/A'),
        'total_rating': game.get('total_rating', 0),
        'total_rating_count': game.get('total_rating_count', 0),
        'involved_companies': [company['company']['name'] for company in game.get('involved_companies', [])]
    }

    # Check if the item already exists in DynamoDB
    response = table.get_item(Key={'id': item['id']})
    if 'Item' in response:
        print(f"Game with ID {item['id']} already exists. Updating record.")
        table.update_item(
            Key={'id': item['id']},
            UpdateExpression="set #name=:n, #first_release_date=:f, #platforms=:p, #genres=:g, #multiplayer_modes=:m, #summary=:s, #storyline=:st, #cover_url=:c, #total_rating=:tr, #total_rating_count=:trc, #involved_companies=:ic",
            ExpressionAttributeNames={
                '#name': 'name',
                '#first_release_date': 'first_release_date',
                '#platforms': 'platforms',
                '#genres': 'genres',
                '#multiplayer_modes': 'multiplayer_modes',
                '#summary': 'summary',
                '#storyline': 'storyline',
                '#cover_url': 'cover_url',
                '#total_rating': 'total_rating',
                '#total_rating_count': 'total_rating_count',
                '#involved_companies': 'involved_companies'
            },
            ExpressionAttributeValues={
                ':n': item['name'],
                ':f': item['first_release_date'],
                ':p': item['platforms'],
                ':g': item['genres'],
                ':m': item['multiplayer_modes'],
                ':s': item['summary'],
                ':st': item['storyline'],
                ':c': item['cover_url'],
                ':tr': item['total_rating'],
                ':trc': item['total_rating_count'],
                ':ic': item['involved_companies']
            }
        )
    else:
        print(f"Adding new game with ID {item['id']} to DynamoDB.")
        table.put_item(Item=item)

def main():
    game = fetch_game_by_id(GAME_ID)
    if game:
        backfill_dynamodb(game)

if __name__ == "__main__":
    main()
