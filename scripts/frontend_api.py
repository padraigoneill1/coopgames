from datetime import datetime
import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, Depends, Header, Form
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import boto3
from dotenv import load_dotenv



# Load environment variables from a .env file
load_dotenv()

# AWS and security configuration
DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
AWS_REGION = os.getenv('AWS_REGION')
API_KEY = os.getenv('API_KEY')

# Initialize AWS DynamoDB client
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT_URL, region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Security configuration
api_key_header = APIKeyHeader(name="api-key", auto_error=True)

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Convert Unix timestamp to readable format
def unix_to_readable(unix_timestamp: int) -> str:
    return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')


class Game(BaseModel):
    id: str
    name: Optional[str] = None
    first_release_date: Optional[int] = None
    platforms: Optional[List[str]] = []
    genres: Optional[List[str]] = []
    multiplayer_modes: Optional[List[dict]] = []
    summary: Optional[str] = None
    storyline: Optional[str] = None
    cover_url: Optional[str] = None
    total_rating: Optional[float] = None
    total_rating_count: Optional[int] = None
    involved_companies: Optional[List[str]] = []

@app.get("/", response_class=HTMLResponse, dependencies=[Depends(get_api_key)])
async def read_games(request: Request):
    response = table.scan()
    items = response.get('Items', [])
    return templates.TemplateResponse("index.html", {"request": request, "games": items})

@app.get("/game/{game_id}", response_class=HTMLResponse, dependencies=[Depends(get_api_key)])
async def read_game(request: Request, game_id: str):
    response = table.get_item(Key={'id': game_id})
    item = response.get('Item')
    if not item:
        raise HTTPException(status_code=404, detail="Game not found")
    return templates.TemplateResponse("game.html", {"request": request, "game": item})

@app.get("/add_game", response_class=HTMLResponse, dependencies=[Depends(get_api_key)])
async def add_game_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/add_game", dependencies=[Depends(get_api_key)])
async def add_game(
    id: str = Form(...),
    name: Optional[str] = Form(None),
    first_release_date: Optional[int] = Form(None),
    platforms: Optional[str] = Form(None),
    genres: Optional[str] = Form(None),
    multiplayer_modes: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    storyline: Optional[str] = Form(None),
    cover_url: Optional[str] = Form(None),
    total_rating: Optional[float] = Form(None),
    total_rating_count: Optional[int] = Form(None),
    involved_companies: Optional[str] = Form(None),
):
    item = {
        'id': id,
        'name': name,
        'first_release_date': first_release_date,
        'platforms': platforms.split(',') if platforms else [],
        'genres': genres.split(',') if genres else [],
        'multiplayer_modes': json.loads(multiplayer_modes) if multiplayer_modes else [],
        'summary': summary,
        'storyline': storyline,
        'cover_url': cover_url,
        'total_rating': total_rating,
        'total_rating_count': total_rating_count,
        'involved_companies': involved_companies.split(',') if involved_companies else []
    }
    table.put_item(Item=item)
    return {"message": "Game added"}

@app.get("/delete_game/{game_id}", dependencies=[Depends(get_api_key)])
async def delete_game(game_id: str):
    response = table.delete_item(Key={'id': game_id})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted"}
