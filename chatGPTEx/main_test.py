import json
from typing import Optional
from fastapi import FastAPI, Request, Response
from flask import jsonify
ChatContext = '233'
app = FastAPI()
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

# @app.post('/chat')
# async def chat(prompt: str, options: Optional[ChatContext] = None):
#     try:
#         response = await chatReply(prompt, options)
#         return response
#     except Exception as e:
#         return str(e)
data = {
        "role": "assistant",
        "id": "chatcmpl-6qxiTlAbab2j7II4742JB4ncfGnGK",
        "parentMessageId": "84acbd68-7f63-443a-b112-b0f68e49f6b8",
        "text": "Hello! How can I assist you today?",
        "delta": "?",
        "detail": {
            "id": "chatcmpl-6qxiTlAbab2j7II4742JB4ncfGnGK",
            "object": "chat.completion.chunk",
            "created": 1678080625,
            "model": "gpt-3.5-turbo-0301",
            "choices": [
                {
                    "delta": {"content": "?"},
                    "index": 0,
                    "finish_reason": None
                }
            ]
        }
    }
@app.post('/chat-process')
async def chat_process():
    return Response(content=jsonify(data), media_type="application/json")

# @app.post('/config')
# async def config():
#     try:
#         response = await chatConfig()
#         return response
#     except Exception as e:
#         return str(e)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=3002)
