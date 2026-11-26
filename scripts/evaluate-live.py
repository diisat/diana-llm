"""Explicit live smoke check; consumes provider quota. Never prints credentials."""
import json
import time
from pathlib import Path
import httpx
from dotenv import dotenv_values
root=Path(__file__).resolve().parents[1]
env=dotenv_values(root/'.env')
if not env.get('GROQ_API_KEY'):raise SystemExit('Configure GROQ_API_KEY first.')
questions=[('en','What technologies did Diana use at Covéa?'),('fr','Quel était son rôle chez TransUnion en 2023 ?'),('es','¿Cuándo trabajó en Assura?'),('en','What salary does Diana want?')]
with httpx.Client(timeout=35) as client:
 for i,(locale,message) in enumerate(questions):
  if i: time.sleep(35)  # Keep this small check friendly to low provider token quotas.
  r=client.post('http://127.0.0.1:8001/api/chat',headers={'Authorization':'Bearer '+env['CHAT_SERVICE_TOKEN']},json={'message':message,'locale':locale})
  r.raise_for_status();print(json.dumps({'locale':locale,'question':message,**r.json()},ensure_ascii=False),flush=True)
