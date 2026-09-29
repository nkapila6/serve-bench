import os
import time
import uuid
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI

from transformers import AutoModelForCausalLM, AutoTokenizer
from contextlib import asynccontextmanager

MODEL_ID = os.environ.get("MODEL_ID", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

tokenizer = None
model = None


def load_model():
    global tokenizer, model
    start = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype="auto")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    end = time.perf_counter()
    loading_time = end - start
    print(f"loaded {MODEL_ID} in {loading_time:.2f}s", flush=True)


@asynccontextmanager
async def lifespan(app):
    load_model()
    yield
    print("shutting down", flush=True)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/healthz")
async def healthz():
    if model is None:
        return {"status": "loading", "model": MODEL_ID}

    return {"status": "ok", "model": MODEL_ID}


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    max_tokens: int | None = None
    stream: bool = False


@app.post("/v1/chat/completions")
async def completions(request: ChatCompletionRequest):
    # curl localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"x","messages":[{"role":"user","content":"hi"}]}'
    # model='x' messages=[Message(role='user', content='hi')] max_tokens=None stream=False
    # print(request)
    # print("model name is: " + request.model)

    user_req = request.messages[-1].content
    reply = "You said: " + user_req
    prompt_tokens = len(user_req.split())
    completion_tokens = len(reply.split())

    return {
        "id": "chatcmpl-" + uuid.uuid4().hex,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": reply},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,  # above 2 added
        },
    }


def main():
    uvicorn.run(
        "serve_bench.main:app",
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "8000")),
    )
