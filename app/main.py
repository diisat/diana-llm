import asyncio
import os
import secrets
import time
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from groq import RateLimitError
from .schemas import ChatRequest, ChatResponse

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
# No tracing or chat persistence by default. Do not log prompts or provider exceptions.
from .service import generate_answer

app = FastAPI(title='DianaLLM', version='1.0.0', docs_url=None, redoc_url=None, openapi_url=None)
slots = asyncio.Semaphore(3)

class Budget:
    def __init__(self):
        self.minute = self.day = time.monotonic()
        self.minute_count = self.day_count = 0
    def take(self):
        now = time.monotonic()
        if now-self.minute >= 60:
            self.minute, self.minute_count = now, 0
        if now-self.day >= 86400:
            self.day, self.day_count = now, 0
        if self.minute_count >= int(os.getenv('CHAT_REQUESTS_PER_MINUTE','20')) or self.day_count >= int(os.getenv('CHAT_REQUESTS_PER_DAY','200')):
            raise HTTPException(429, 'Chat limit reached', headers={'Retry-After':'60'})
        self.minute_count += 1
        self.day_count += 1
budget = Budget()

class BodyLimit:
    def __init__(self, app): self.app = app
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        size, chunks = 0, []
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect': return
            chunk = message.get('body', b'');size += len(chunk)
            if size > 16384:
                return await JSONResponse({'detail':'Request too large'},status_code=413)(scope,receive,send)
            chunks.append(chunk)
            if not message.get('more_body'): break
        sent = False
        async def bounded_receive():
            nonlocal sent
            if not sent:
                sent = True
                return {'type':'http.request','body':b''.join(chunks),'more_body':False}
            return await receive()
        await self.app(scope, bounded_receive, send)
app.add_middleware(BodyLimit)

async def authorize(request: Request):
    token = os.getenv('CHAT_SERVICE_TOKEN','')
    if not token:
        raise HTTPException(503, 'Service configuration required')
    if not secrets.compare_digest(request.headers.get('authorization',''), 'Bearer '+token):
        raise HTTPException(401, 'Unauthorized')

@app.get('/health')
async def health():
    return {'status':'ok','configured':bool(os.getenv('GROQ_API_KEY') and os.getenv('CHAT_SERVICE_TOKEN'))}

@app.post('/api/chat', response_model=ChatResponse, dependencies=[Depends(authorize)])
async def chat(payload: ChatRequest):
    if not os.getenv('GROQ_API_KEY'):
        raise HTTPException(503, 'Chat is not configured yet')
    if slots.locked():
        raise HTTPException(429, 'Chat busy', headers={'Retry-After':'10'})
    budget.take()
    async with slots:
        try:
            return await asyncio.wait_for(generate_answer(payload), timeout=30)
        except RateLimitError:
            raise HTTPException(429, 'Model provider limit reached', headers={'Retry-After':'60'}) from None
        except TimeoutError:
            raise HTTPException(504, 'Chat timed out') from None
        except Exception:
            raise HTTPException(502, 'Model provider temporarily unavailable') from None
