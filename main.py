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



cards = tarot_cards
app = FastAPI()
ai_description = AI_DESCRIPTION
client = client


card_list = []
reason_data = ""


class Reason(BaseModel):
    reason: str


@app.post("/reason")
def reason(reason: Reason):
    global reason_data
    reason_data = reason.reason
    return{"reason": reason.reason}

@app.get("/get_card")
def get_card():
    length_card = len(card_list)
    card = random.choice(cards)
    if length_card < 3:
        card_list.append(card)
    if reason_data == "":
        return "No reason given, so I can't consult the stars..."
    else:
        return{"Heres your card": card_list}

# def ai_message():
#     messages = [
#             {"role": "system", "content": AI_DESCRIPTION["system_prompt"]},
#             {"role": "user", "content": f"""
#             Reason for reading: {reason}
#             Cards drawn: {card_list}
#     """}]

#     response = client.chat.completions.create(
#                 model=MODEL,
#                 messages=messages,
#             )

#     message = response.choices[0].message.content
#     return message


@app.get("/overview")
def overview():
    message = ai_message(card_list=card_list, reason=reason_data)
    if len(card_list) <= 2:
        return "Not enough cards given. The stars can't work if not enough information is given!"
    else:
        return{"message": message}

