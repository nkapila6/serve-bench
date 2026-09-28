import os
import uvicorn
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


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

    return {
        "id": 0,  # need to look at uuid
        "object": "chat.completion",
        "created": 100,  # time
        "model": "urmum",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "yey"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,  # len(tokenized request)
            "completion_tokens": 100,  # len(output tokenized)
            "total": 110,  # above 2 added
        },
    }


def main():
    uvicorn.run(
        "serve_bench.main:app",
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "8000")),
    )
