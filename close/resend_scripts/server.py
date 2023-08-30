# uvicorn server:app --port='8080' --host='0.0.0.0' --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

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


@app.get("resend/event")
def health():
    return {"message": "hi"}


handler = Mangum(app)
