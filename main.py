from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from cards import tarot_cards
import random
from config import API_KEY, BASE_URL, MODEL, FIREBASE_WEB_API_KEY, ALLOWED_EMAILS
import json
import requests
from ddgs import DDGS
from openai import OpenAI
from ai_resources import *
import uuid
import firebase_admin
from firebase_admin import credentials
import os
from fastapi import Depends, HTTPException, status                                                                                
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials                                                             
from firebase_admin import auth  

firebase_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

cred = credentials.Certificate(firebase_path)
firebase_admin.initialize_app(cred)





cards = tarot_cards
app = FastAPI()
bearer_scheme = HTTPBearer()
app.mount("/static", StaticFiles(directory="static"), name="static")
ai_description = AI_DESCRIPTION
client = client

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        decoded = auth.verify_id_token(creds.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return decoded

@app.get("/")
def index():
    return FileResponse("static/index.html")

# card_list = []
# reason_data = ""
card_list = {}
reason_data = {}


@app.get("/get_id")
def get_id():
    myuuid = uuid.uuid4()
    return myuuid



class Reason(BaseModel):
    uuid: str
    reason: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/reason")
def reason(reason: Reason, user = Depends(get_current_user)):
    global reason_data
    global card_list
    card_list[reason.uuid] = []
    reason_data[reason.uuid] = reason.reason
    return{"reason": reason.reason}

@app.get("/get_card")
def get_card(uuid: str, user = Depends(get_current_user)):
    if uuid not in reason_data:
        return "No reason given, so I can't consult the stars..."
    
    length_card = len(card_list[uuid])
    card = random.choice(cards)

    if length_card < 3:
        card_list[uuid].append(card)

    return{"Heres your card": card_list[uuid]}


@app.get("/overview")
def overview(uuid: str, user = Depends(get_current_user)):  
    message = ai_message(card_list=card_list[uuid], reason=reason_data[uuid])
    if len(card_list[uuid]) <= 2:
        return "Not enough cards given. The stars can't work if not enough information is given!"
    else:
        return{"message": message}

def check_email_allowed(email: str):
    if email.lower() not in {e.lower() for e in ALLOWED_EMAILS}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not allowed in this web."
        )


@app.post("/login")
def login(body: LoginRequest):
    check_email_allowed(body.email)
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"  
    payload = {
        "email": body.email,
        "password": body.password,
        "returnSecureToken": True
    }          
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    data = response.json()
    return{"idToken": data["idToken"]}


            
        

@app.post("/signup")
def signup(body: LoginRequest):
    check_email_allowed(body.email)
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"  
    payload = {
        "email": body.email,
        "password": body.password,
        "returnSecureToken": True
    }          
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    data = response.json()
    return{"idToken": data["idToken"]}
    

   
    


# card_list = []

# card_list.append("dfd")

# card_list = {}

# card_list["mydofkjhdsoi"] = []

# card_list["mydofkjhdsoi"].append("dfd")


# card_list = {
#     "dfd":[],
#     "user 2":[],
#     "user 3":[],
#     "user 4":[],
#     "user 5":[],
# }

