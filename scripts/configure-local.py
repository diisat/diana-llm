"""Configure a shared local service token without printing secrets or overwriting a Groq key."""
from pathlib import Path
import secrets
root=Path(__file__).resolve().parents[1]
p=root/'.env'
s=p.read_text() if p.exists() else (root/'.env.example').read_text()
entries=dict(line.split('=',1) for line in s.splitlines() if '=' in line and not line.startswith('#'))
token=entries.get('CHAT_SERVICE_TOKEN') or secrets.token_urlsafe(32)
lines=[line for line in s.splitlines() if not line.startswith('CHAT_SERVICE_TOKEN=')]
p.write_text('\n'.join(lines)+'\nCHAT_SERVICE_TOKEN='+token+'\n');p.chmod(0o600)
f=root.parent/'diana-creative-portfolio/frontend/.env.local'
if f.parent.exists():
 s=f.read_text() if f.exists() else ''
 lines=[line for line in s.splitlines() if not line.startswith(('CHAT_SERVICE_URL=','CHAT_SERVICE_TOKEN='))]
 f.write_text('\n'.join(lines)+'\nCHAT_SERVICE_URL=http://127.0.0.1:8001\nCHAT_SERVICE_TOKEN='+token+'\n');f.chmod(0o600)
print('Local service token configured. Add GROQ_API_KEY to diana-llm/.env; do not commit that file.')
