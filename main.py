from fastapi import FastAPI, Request, HTTPException, Depends
import uuid
import json
from typing import Optional
import os

app = FastAPI()
valid_keys = set()
JSON_PATH = './keys.json'

def load_keys(path) -> set:
    if os.path.exists(path):
        with open(path, "r") as file:
            return set(json.load(file))
    return set()

def save_keys(keys, path):
    with open(path, "w") as file:
        json.dump(list(keys), file)

def generate_key() -> str:
    new_key = str(uuid.uuid4())
    valid_keys.add(new_key)
    print(f"[ ADDED ] {new_key}")
    return new_key

async def validate_uuid(request: Request):
    request_uuid = request.headers.get("X-API-UUID")
    if request_uuid not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing UUID")
    valid_keys.remove(request_uuid)
    save_keys(valid_keys, JSON_PATH)
    print(f"[ REMOVED ] {request_uuid}")

@app.middleware("http")
async def add_new_uuid_to_response(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-API-UUID"] = generate_key()
    return response

@app.get("/")
async def root():
    return {"message": "Hello from Spotipi!"}

@app.get("/api/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None, valid: bool = Depends(validate_uuid)):
    return {"item_id": item_id, "q": q}

# Initialize the first UUID
@app.on_event("startup")
async def startup_event():
    generate_key()
