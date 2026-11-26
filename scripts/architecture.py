"""Generate editable architecture SVGs using only Python's standard library."""
from pathlib import Path
from html import escape
from math import atan2, cos, sin
OUT=Path(__file__).resolve().parents[1]/'docs/images'
OUT.mkdir(parents=True,exist_ok=True)
INK='#28252b';WINE='#71334b';PAPER='#f8f7f5';LILAC='#ece5f3';GREEN='#e3ede6'
def start(title,subtitle,h=1060):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{h}" viewBox="0 0 1400 {h}"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="{WINE}" stroke-width="1.5"/></marker></defs><rect width="1400" height="{h}" fill="{PAPER}"/>',text(70,62,'L’ATELIER DE DIANA / SYSTEM DESIGN',15,WINE),text(70,112,title,37),text(70,150,subtitle,18,'#746d78')]
def text(x,y,t,size=18,color=INK):return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}">{escape(t)}</text>'
def box(x,y,w,h,title,lines,fill='white'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="#d4cbd9"/>'+text(x+24,y+38,title,23,WINE)+''.join(text(x+24,y+73+i*27,t,17) for i,t in enumerate(lines))
def head(x,y,angle):
 a=angle; pts=[(x,y),(x-12*cos(a)+5*sin(a),y-12*sin(a)-5*cos(a)),(x-12*cos(a)-5*sin(a),y-12*sin(a)+5*cos(a))]
 return '<polygon points="'+ ' '.join(f'{px},{py}' for px,py in pts)+'" fill="'+WINE+'"/>'
def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None):
 s=f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{WINE}" stroke-width="2" fill="none" marker-end="url(#arrow)"/>'
 return s+head(x2,y2,atan2(y2-y1,x2-x1))+(text(lx if lx is not None else (x1+x2)/2+12,ly if ly is not None else (y1+y2)/2-10,label,15,WINE) if label else '')
def save(name,parts): (OUT/(name+'.svg')).write_text(''.join(parts)+'</svg>')
p=start('DianaLLM · independent service','React sidebar + Python / FastAPI + LangChain + Groq. No model training or vector database.',1030)
p += [text(70,208,'PORTFOLIO REPOSITORY · atelier-diana',16,WINE),box(70,230,510,160,'React sidebar',['English / French / Spanish · light / dark','Accessible dialog, suggestions and source links','Conversation held in browser memory']),box(70,470,510,150,'Next.js · POST /api/chat',['Same-origin proxy · bounded JSON requests','CHAT_SERVICE_URL + CHAT_SERVICE_TOKEN'],LILAC),arrow(325,390,325,470,'Question + recent turns',340,435),text(750,208,'INDEPENDENT REPOSITORY · diana-llm',16,WINE),box(750,230,580,180,'FastAPI · POST /api/chat',['Shared-token authentication · input validation','Request budgets · concurrency limit · timeout','LangChain prompt + ChatGroq + structured answer'],LILAC),arrow(580,535,750,340,'Private HTTP',592,365),box(750,480,580,140,'diana-profile.json',['CV: authoritative dates, roles and technologies','Technical dossier: mission context and details'],GREEN),arrow(1040,480,1040,410,'Read-only',1055,450),box(750,720,580,135,'Groq API · hosted language model',['GROQ_API_KEY stays in the Python service','Receives public profile, question and recent turns']),arrow(1330,320,1370,320),'<path d="M1370 320L1370 785L1330 785" fill="none" stroke="#71334b" stroke-width="2" marker-end="url(#arrow)"/>',text(1170,680,'HTTPS to Groq',16,WINE),box(70,720,510,135,'JSON answer + related page links',['Response returns through the same API path','The application does not persist conversations']),text(70,940,'Pattern: layered service with adapters · React is an API client; Groq is a replaceable model adapter.',18),text(70,976,'No database dependency for chat. Rate budgets reset on service restart; use one worker in this version.',16,'#746d78')]
p += [head(1330,785,3.14159)]
save('diana-llm-architecture',p)
p=start('Portfolio + DianaLLM','Two independent repositories. One public website, with private application services.',1120)
p += [box(440,200,520,125,'Visitor · React / Next.js interface',['Portfolio pages + Three.js map + chat sidebar','Browser holds the conversation in memory']),arrow(700,325,700,390,'HTTPS in production',720,363),box(440,390,520,145,'Next.js server · public web service',['Pages, static files, CV and certificates','/api/notes → Java    /api/chat → FastAPI'],LILAC),box(70,650,510,150,'Spring Boot · Java 21',['Projects and moderated guestbook notes','Existing portfolio backend · private network']),box(820,650,510,150,'DianaLLM · Python / FastAPI',['Validation + budgets + LangChain + ChatGroq','Independent repository · private network'],LILAC),'<path d="M560 535L560 582L325 582L325 650" fill="none" stroke="#71334b" stroke-width="2" marker-end="url(#arrow)"/>',text(135,608,'API_URL · private HTTP',16,WINE),'<path d="M840 535L840 582L1075 582L1075 650" fill="none" stroke="#71334b" stroke-width="2" marker-end="url(#arrow)"/>',text(875,570,'CHAT_SERVICE_URL + shared token',16,WINE),box(70,890,510,125,'PostgreSQL 16',['Projects + guestbook · durable storage','Flyway migrations · no chat-history table'],GREEN),arrow(325,800,325,890,'JDBC · private connection',345,848),box(820,890,245,125,'Profile JSON',['Verified public facts','Read-only file'],GREEN),box(1090,890,240,125,'Groq API',['Hosted LLM','External HTTPS']),arrow(942,800,942,890,'read',956,848),arrow(1208,800,1208,890,'API key',1223,848),text(70,1080,'Secrets stay on servers. Deploy services privately; only the Next.js website needs a public URL.',18)]
p += [head(325,650,1.5708),head(1075,650,1.5708)]
save('portfolio-with-dianallm',p)
print('SVG architectures generated.')
