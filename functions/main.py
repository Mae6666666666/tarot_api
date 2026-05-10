from firebase_functions import https_fn
import firebase_admin
from cards import tarot_cards
from ai_resources import *
import uuid

firebase_admin.initialise_app()

cards = tarot_cards
ai_description = AI_DESCRIPTION
client = client

card_list = {}
reason_data = {}

@https_fn.on_request()
def get_id(req: https_fn.Request) -> https_fn.Response:
    myuuid = uuid.uuid4()
    return https_fn.Response(f"{myuuid}")



