import os
import uvicorn

from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

def main():
    uvicorn.run("serve_bench.main:app", host="127.0.0.1",
        port=int(os.environ.get("PORT", "8000")))
