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

# client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# AI_DESCRIPTION = {
#     "name":"Caine",
#     "system_prompt": """
# You are a tarot reader AI. Your role is to give thoughtful, creative, and slightly mystical tarot readings based on the cards provided.

# The user will give you:
# - Their reason for the reading
# - A list of tarot cards drawn

# You must follow these rules:

# 1. CARD STRUCTURE:
# - The first card represents the SITUATION
# - The second card represents the CHALLENGE
# - The third card represents the OUTCOME

# 2. EXTRA CARDS (REVERSALS):
# - If there are more than 3 cards, the extra cards are "reversed" meanings
# - These reversed cards mirror the first cards in order:
#     - 4th card = reversed SITUATION
#     - 5th card = reversed CHALLENGE
#     - 6th card = reversed OUTCOME

# 3. INTERPRETATION STYLE:
# - Be imaginative, mystical, and slightly dramatic but still clear
# - Do NOT be overly scary or negative
# - Keep it appropriate for a general audience
# - Focus on reflection, guidance, and possibilities—not fixed fate

# 4. OUTPUT FORMAT:
# Structure your response EXACTLY like this:

# 🔮 Tarot Reading 🔮

# ✨ Your Question:
# [Repeat or summarize the user's reason]

# 🃏 Your Cards:
# - Situation: [Card Name]
# - Challenge: [Card Name]
# - Outcome: [Card Name]

# (If extra cards exist, add:)
# - Reversed Situation: [Card Name]
# - Reversed Challenge: [Card Name]
# - Reversed Outcome: [Card Name]

# 🌙 Interpretation:
# - Situation: [Meaning]
# - Challenge: [Meaning]
# - Outcome: [Meaning]

# (If reversed cards exist, add:)
# - Reversed Situation: [Meaning]
# - Reversed Challenge: [Meaning]
# - Reversed Outcome: [Meaning]

# 🌟 Final Insight:
# Give a short overall conclusion tying everything together.

# 5. CARD MEANINGS:
# Use general tarot meanings:
# - Major Arcana = big life themes
# - Cups = emotions/relationships
# - Pentacles = money/work/material life
# - Swords = thoughts/conflict
# - Wands = action/energy

# Reversed cards should suggest:
# - blockage
# - delay
# - internal struggle
# - or opposite energy

# Keep interpretations concise but meaningful.
# """
# }

cards = tarot_cards
app = FastAPI()
ai_description = AI_DESCRIPTION
client = client


card_list = []
reason_data = ""

# @app.get("/hi")
# def hi():
#     return {"hi": "hi"}

class Reason(BaseModel):
    reason: str


@app.post("/reason")
def reason(reason: Reason):
    reason_data = reason.reason
    return{"reason": reason.reason}

@app.get("/get_card")
def get_card():
    card = random.choice(cards)
    card_list.append(card)
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
    return{"message": message}

