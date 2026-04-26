from fastapi import FastAPI
from pydantic import BaseModel
from cards import tarot_cards
import random
from config import API_KEY, BASE_URL, MODEL
import json
import requests
from ddgs import DDGS
from openai import OpenAI
from ai_resources import *
import uuid



cards = tarot_cards
app = FastAPI()
ai_description = AI_DESCRIPTION
client = client

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


@app.post("/reason")
def reason(reason: Reason):
    global reason_data
    global card_list
    card_list[reason.uuid] = []
    reason_data[reason.uuid] = reason.reason
    return{"reason": reason.reason}

@app.get("/get_card")
def get_card(uuid: str):
    if uuid not in reason_data:
        return "No reason given, so I can't consult the stars..."
    
    length_card = len(card_list[uuid])
    card = random.choice(cards)

    if length_card < 3:
        card_list[uuid].append(card)

    return{"Heres your card": card_list[uuid]}


@app.get("/overview")
def overview(uuid: str):
    message = ai_message(card_list=card_list[uuid], reason=reason_data[uuid])
    if len(card_list[uuid]) <= 2:
        return "Not enough cards given. The stars can't work if not enough information is given!"
    else:
        return{"message": message}
    


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

