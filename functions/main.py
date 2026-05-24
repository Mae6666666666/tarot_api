from firebase_functions import https_fn
import firebase_admin
from cards import tarot_cards
from ai_resources import *
import uuid
import json
import requests
from firebase_admin import auth
from config import FIREBASE_WEB_API_KEY, ALLOWED_EMAILS
from firebase_admin import firestore

firebase_admin.initialize_app()

cards = tarot_cards
ai_description = AI_DESCRIPTION
# client = client

# card_list = {}
# reason_data = {}

fun_times="Coding with abe"

def check_email_allowed(email: str) -> bool:
    # email.lower at first converts email to lowercase and then checks to see if its in allowed emails
    # with the following inside the {}
    return email.lower() in {email.lower() for email in ALLOWED_EMAILS}

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
        return https_fn.Response("Use POST", status=405)

    user = verify_token(req)
    if user is None:
        return https_fn.Response("Invalid or expired token", status=401)

    body = req.get_json(silent=True) or {}
    user_reason = body.get("reason", "")

    if not user_reason:
        return https_fn.Response("Missing reason", status=400)

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