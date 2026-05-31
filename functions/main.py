from firebase_functions import https_fn
import firebase_admin
from cards import tarot_cards
from ai_resources import *
import uuid
import json
import requests
from firebase_admin import auth
from config import FIREBASE_WEB_API_KEY, ALLOWED_EMAILS, API_KEY
from firebase_admin import firestore
import random

firebase_admin.initialize_app()

cards = tarot_cards
ai_description = AI_DESCRIPTION
# client = client

# card_list = {}
# reason_data = {}

fun_times="Coding with abe"

def get_allowed_emails() -> set:
    db = firestore.client()
    doc_ref = db.collection("config").document("access")
    doc = doc_ref.get()
    if not doc.exists:
        doc_ref.set({"allowed_emails": list(ALLOWED_EMAILS)})
        return set(ALLOWED_EMAILS)
    data = doc.to_dict()
    return set(data.get("allowed_emails", []))

def check_email_allowed(email: str) -> bool:
    allowed_emails = get_allowed_emails()
    return email.lower() in {email.lower() for email in allowed_emails}

@https_fn.on_request()
def signup(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return https_fn.Response("Use POST", status=405)

    body = req.get_json(silent=True) or {}
    email = body.get("email", "")
    password = body.get("password", "")

    if not check_email_allowed(email):
        return https_fn.Response("You're not allowed in this web.", status=403)

    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
        f"?key={FIREBASE_WEB_API_KEY}"
    )
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return https_fn.Response("Invalid email or password", status=401)

    data = response.json()
    return https_fn.Response(
        f'{{"idToken": "{data["idToken"]}"}}',
        mimetype="application/json",
    )

@https_fn.on_request()
def login(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return https_fn.Response("Use POST", status=405)

    body = req.get_json(silent=True) or {}
    email = body.get("email", "")
    password = body.get("password", "")

    if not check_email_allowed(email):
        return https_fn.Response("You're not allowed in this web.", status=403)

    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={FIREBASE_WEB_API_KEY}"
    )
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return https_fn.Response("Invalid email or password", status=401)

    data = response.json()
    return https_fn.Response(
        json.dumps({"idToken": data["idToken"]}),
        mimetype="application/json",
    )

def verify_token(req: https_fn.Request):
    header = req.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[len("Bearer "):]
    try:
        return auth.verify_id_token(token)
    except Exception:
        return None

@https_fn.on_request()
def reason(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return https_fn.Response("Use POST.", status=405)

    user = verify_token(req)
    if user is None:
        return https_fn.Response("Invalid or expired token.", status=401)

    body = req.get_json(silent=True) or {}
    user_reason = body.get("reason", "")

    if not user_reason:
        return https_fn.Response("Missing reason!", status=400)

    user_uuid = str(uuid.uuid4())

    db = firestore.client()
    db.collection("users").document(user["uid"]) \
    .collection("readings").document(user_uuid).set({
        "reason": user_reason,
        "cards": [],
        "response": None,
        "created_at": firestore.SERVER_TIMESTAMP,
    })

    return https_fn.Response(
        json.dumps({"uuid": user_uuid, "reason": user_reason}),
        mimetype="application/json",
    )

@https_fn.on_request()
def get_card(req: https_fn.Request) -> https_fn.Response:
    if req.method != "GET":
        return https_fn.Response("Use GET.", status=405)

    user = verify_token(req)
    if user is None:
        return https_fn.Response("Invalid or expired token.", status=401)

    user_uuid = req.args.get("uuid", "")
    if not user_uuid:
        return https_fn.Response("Missing uuid!", status=400)

    db = firestore.client()
    doc_ref = db.collection("users").document(user["uid"]) \
                .collection("readings").document(user_uuid)
    doc = doc_ref.get()

    if not doc.exists:
        return https_fn.Response("No reason given, so I can't consult the stars...", status=404)

    data = doc.to_dict()
    current_cards = data.get("cards", [])

    if len(current_cards) < 3:
        remaining = [card for card in cards if card not in current_cards]
        current_cards.append(random.choice(remaining))
        doc_ref.update({"cards": current_cards})

    return https_fn.Response(
        json.dumps({"Heres your card": current_cards}),
        mimetype="application/json",
    )

@https_fn.on_request(secrets=[API_KEY])
def overview(req: https_fn.Request) -> https_fn.Response:
    if req.method != "GET":
        return https_fn.Response("Use GET.", status=405)

    user = verify_token(req)
    if user is None:
        return https_fn.Response("Invalid or expired token.", status=401)

    user_uuid = req.args.get("uuid", "")
    if not user_uuid:
        return https_fn.Response("Missing uuid!", status=400)

    db = firestore.client()
    doc_ref = db.collection("users").document(user["uid"]) \
                .collection("readings").document(user_uuid)
    doc = doc_ref.get()

    if not doc.exists:
        return https_fn.Response("No reading found.", status=404)

    data = doc.to_dict()
    current_cards = data.get("cards", [])
    user_reason = data.get("reason", "")

    if len(current_cards) <= 2:
        return https_fn.Response(
            "Not enough cards given. The stars can't work if not enough information is given!",
            status=400,
        )

    message = ai_message(card_list=current_cards, reason=user_reason)
    doc_ref.update({"response": message})

    return https_fn.Response(
        json.dumps({"message": message}),
        mimetype="application/json",
    )