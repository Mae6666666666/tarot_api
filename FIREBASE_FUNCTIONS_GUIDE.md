# Firebase Functions in Python — Quick Start

A walkthrough for the two endpoints scaffolded in `functions/`:

- `GET /hello?word=world` → returns `hallo world`
- `POST /combine` with `{"a":..., "b":..., "c":...}` → echoes them back joined together

---

## Step 1 — Folder layout

The scaffold I created looks like this:

```
tarot_api/
├── firebase.json          # tells the firebase CLI where the functions live
└── functions/
    ├── main.py            # your endpoint code
    ├── requirements.txt   # python deps
    └── .gitignore
```

The key file is `firebase.json` at the project root. Its `functions.source` field points at the `functions` folder, and `runtime` says we want Python 3.11:

```json
{
  "functions": [
    {
      "source": "functions",
      "runtime": "python311"
    }
  ]
}
```

---

## Step 2 — Link your firebase project

You already have the CLI installed. From the project root run:

```bash
firebase login            # only needed once per machine
firebase use --add        # pick the firebase project to associate with this folder
```

`firebase use --add` writes a small `.firebaserc` file next to `firebase.json` so the CLI knows which project to deploy to.

---

## Step 3 — Set up the Python virtual environment

Firebase's Python runtime expects a venv inside the `functions/` folder called `venv`. From the project root:

```bash
cd functions
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` only contains `firebase_functions` — that's the package that gives you the `https_fn` decorator and the `Request` / `Response` classes.

---

## Step 4 — Read the GET endpoint

Open `functions/main.py`:

```python
from firebase_functions import https_fn


@https_fn.on_request()
def hello(req: https_fn.Request) -> https_fn.Response:
    word = req.args.get("word", "")
    return https_fn.Response(f"hallo {word}")
```

What's going on, line by line:

- **`@https_fn.on_request()`** turns a plain Python function into an HTTP endpoint. Firebase reads every function decorated with this and exposes it as its own URL.
- **The function name *is* the URL path.** Because the function is called `hello`, it lives at `/hello`. If you renamed it to `greet`, the URL would become `/greet`.
- **`req: https_fn.Request`** is a Flask-style request object. `req.args` is the query string, so `?word=world` shows up as `req.args["word"]`.
- **`req.args.get("word", "")`** reads the `word` query param, defaulting to an empty string if it's missing. Using `.get(...)` instead of `req.args["word"]` avoids a `KeyError` if the caller forgets the param.
- **`https_fn.Response(...)`** sends a plain-text 200 response. You can pass `status=...` to change the status code.

> Note: `on_request()` accepts every HTTP method (GET, POST, PUT, …). For this endpoint we don't care because reading a query string works for any method. The POST one below shows how to gate by method.

---

## Step 5 — Read the POST endpoint

```python
@https_fn.on_request()
def combine(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return https_fn.Response("Use POST", status=405)

    data = req.get_json(silent=True) or {}
    a = data.get("a", "")
    b = data.get("b", "")
    c = data.get("c", "")

    return https_fn.Response(f"a={a}, b={b}, c={c} -> {a}{b}{c}")
```

Things to notice:

- **Method gating.** `on_request` doesn't filter by verb, so we manually return `405 Method Not Allowed` for anything other than POST. `405` is the standard "wrong HTTP verb" status code.
- **`req.get_json(silent=True)`** parses the JSON body. `silent=True` means: if the body is missing or invalid JSON, return `None` instead of raising. The trailing `or {}` then turns `None` into an empty dict so the `.get()` calls don't crash.
- **`.get("a", "")`** pulls each field out of the body, defaulting to empty string if absent. This keeps the endpoint forgiving — bad input doesn't 500.
- **The response** concatenates the three values so you can see them round-trip.

---

## Step 6 — Run it locally with the emulator

From the project root:

```bash
firebase emulators:start --only functions
```

The emulator will print URLs that look like:

```
http://127.0.0.1:5001/<your-project-id>/us-central1/hello
http://127.0.0.1:5001/<your-project-id>/us-central1/combine
```

Test the GET in your browser or with curl:

```bash
curl "http://127.0.0.1:5001/<your-project-id>/us-central1/hello?word=world"
# -> hallo world
```

Test the POST with curl:

```bash
curl -X POST "http://127.0.0.1:5001/<your-project-id>/us-central1/combine" \
  -H "Content-Type: application/json" \
  -d '{"a":"foo","b":"bar","c":"baz"}'
# -> a=foo, b=bar, c=baz -> foobarbaz
```

The `-H "Content-Type: application/json"` header is what tells the server "the body is JSON" so `req.get_json()` knows how to parse it.

---

## Step 7 — Deploy (optional)

When you're ready to put it on the public internet:

```bash
firebase deploy --only functions
```

The CLI will print the live URLs (they'll be on `cloudfunctions.net` or `run.app`). First deploy of a Python function takes a few minutes because the build step has to install your `requirements.txt` in the cloud.

---

## Cheat sheet — what to change to add a new endpoint

1. Add a new function to `functions/main.py` with the `@https_fn.on_request()` decorator.
2. The function name becomes the URL path.
3. Read inputs from `req.args` (query string) or `req.get_json()` (JSON body).
4. Return an `https_fn.Response(body, status=...)`.
5. Restart the emulator (or redeploy) and the new endpoint shows up.
