# uvicorn webhook:app --port='8080' --host='0.0.0.0' --reload

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from event_tracker import Event

# initiate fast api app
app = FastAPI(
    title="Resend event slack",
    version="0.0.1",
    description='Resend event slack'
)

# inject middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" APIs """


@app.post("/resend/event")
async def health(request: Request):
    body = await request.json()
    email_type = body.get('type')
    email_id = body.get('data').get('email_id')
    Event(email_type, email_id).update_email()
    return 200


handler = Mangum(app)
