'use client';
import {useEffect,useRef,useState} from 'react';
import './chat.css';
const copy={
 en:{title:'Meet Diana, through a conversation.',intro:'I’m Diana’s AI assistant. Ask about her experience, projects or creative side.',placeholder:'What would you like to know?',send:'Send',close:'Close chat',clear:'New conversation',busy:'Thinking…',error:'I couldn’t answer right now. Please try again.',unavailable:'DianaLLM is not available yet. You can explore Diana’s journey in the meantime.',limit:'The chat has reached its limit. Please try later.',retry:'Try again',privacy:'AI assistant · May make mistakes. Messages are sent to Groq to generate a reply. This app does not save your conversations.',sources:'Related pages',suggestions:['What has Diana built?','How does she use AI?','Tell me about her artistic side.']},
 fr:{title:'Rencontrer Diana, en quelques questions.',intro:'Je suis l’assistant IA de Diana. Parlons de ses expériences, de ses projets ou de son côté créatif.',placeholder:'Que souhaites-tu savoir ?',send:'Envoyer',close:'Fermer le chat',clear:'Nouvelle conversation',busy:'Je réfléchis…',error:'Je n’ai pas pu répondre. Réessaie dans un instant.',unavailable:'DianaLLM n’est pas encore disponible. Tu peux découvrir le parcours de Diana en attendant.',limit:'Le chat a atteint sa limite. Réessaie plus tard.',retry:'Réessayer',privacy:'Assistant IA · Peut se tromper. Les messages sont envoyés à Groq pour générer une réponse. Cette application ne conserve pas les conversations.',sources:'Pages associées',suggestions:['Quels projets Diana a-t-elle réalisés ?','Comment utilise-t-elle l’IA ?','Parle-moi de son côté artistique.']},
 es:{title:'Conoce a Diana, conversando.',intro:'Soy el asistente de IA de Diana. Pregúntame por su experiencia, proyectos o lado creativo.',placeholder:'¿Qué te gustaría saber?',send:'Enviar',close:'Cerrar chat',clear:'Nueva conversación',busy:'Pensando…',error:'No pude responder ahora. Inténtalo de nuevo.',unavailable:'DianaLLM aún no está disponible. Puedes explorar la trayectoria de Diana mientras tanto.',limit:'El chat ha alcanzado su límite. Inténtalo más tarde.',retry:'Reintentar',privacy:'Asistente de IA · Puede equivocarse. Los mensajes se envían a Groq para generar una respuesta. Esta aplicación no guarda las conversaciones.',sources:'Páginas relacionadas',suggestions:['¿Qué proyectos ha creado Diana?','¿Cómo utiliza la IA?','Cuéntame sobre su lado artístico.']}
};
export default function ChatSidebar({locale='en',open,onClose,endpoint='/api/chat'}){
 const t=copy[locale]||copy.en,dialog=useRef(null),input=useRef(null),end=useRef(null),controller=useRef(null),busy=useRef(false);
 const [messages,setMessages]=useState([]),[question,setQuestion]=useState(''),[loading,setLoading]=useState(false),[error,setError]=useState(''),[retry,setRetry]=useState(null);
 useEffect(()=>{if(open&&!dialog.current.open){dialog.current.showModal();input.current?.focus();}else if(!open&&dialog.current.open)dialog.current.close();},[open]);
 useEffect(()=>()=>controller.current?.abort(),[]);
 useEffect(()=>{end.current?.scrollIntoView({block:'nearest',behavior:'instant'});},[messages,loading,error]);
 function reset(){controller.current?.abort();controller.current=null;busy.current=false;setLoading(false);setMessages([]);setQuestion('');setError('');setRetry(null);input.current?.focus();}
 async function send(text,previous=messages){
  const message=text.trim();if(!message||busy.current)return;
  busy.current=true;const abort=new AbortController();controller.current=abort;setLoading(true);setError('');setRetry(null);setQuestion('');
  setMessages([...previous,{role:'user',content:message}]);
  const history=previous.slice(-8).map(({role,content})=>({role,content:content.slice(0,1000)}));
  const timeout=setTimeout(()=>abort.abort(),35000);
  try{
   const r=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,history,locale}),signal:abort.signal});
   if(!r.ok)throw new Error(r.status===503?'unavailable':r.status===429?'limit':'error');
   const data=await r.json();if(typeof data.answer!=='string'||!data.answer.trim())throw new Error('error');
   if(controller.current!==abort)return;
   const sources=Array.isArray(data.sources)?data.sources.filter(s=>typeof s.path==='string'&&/^\/(en|fr|es)\/(journey|about|projects|work\/[-a-z0-9]+)$/.test(s.path)):[];
   setMessages([...previous,{role:'user',content:message},{role:'assistant',content:data.answer,sources}]);
  }catch(e){if(controller.current===abort){setError(['unavailable','limit'].includes(e.message)?e.message:'error');setRetry({text:message,previous});}}
  finally{clearTimeout(timeout);if(controller.current===abort){busy.current=false;setLoading(false);controller.current=null;}}
 }
 return <dialog ref={dialog} className="diana-chat" aria-labelledby="diana-chat-title" onClose={onClose} onClick={e=>{if(e.target===e.currentTarget)dialog.current.close();}}>
  <div className="diana-chat-shell">
   <header className="diana-chat-header"><div><span className="diana-chat-mark" aria-hidden="true">✦</span><strong id="diana-chat-title">DianaLLM</strong><span className="diana-chat-label">AI</span></div><button type="button" aria-label={t.close} onClick={()=>dialog.current.close()}>×</button></header>
   <div className="diana-chat-scroll"><div className="diana-chat-welcome"><h2>{t.title}</h2><p>{t.intro}</p></div>
    {!messages.length&&<div className="diana-chat-suggestions">{t.suggestions.map(s=><button key={s} type="button" onClick={()=>send(s)}>{s}<span aria-hidden="true">↗</span></button>)}</div>}
    <div className="diana-chat-log" role="log" aria-live="polite" aria-relevant="additions text">{messages.map((m,i)=><article key={i} className={`diana-chat-message ${m.role}`}><span className="diana-chat-speaker">{m.role==='assistant'?'DianaLLM':{en:'You',fr:'Toi',es:'Tú'}[locale]}</span><p>{m.content}</p>{m.sources?.length>0&&<nav aria-label={t.sources}>{m.sources.map(s=><a key={s.id} href={s.path}>{s.title} ↗</a>)}</nav>}</article>)}</div>
    {loading&&<p className="diana-chat-status" role="status">{t.busy}</p>}
    {error&&<div className="diana-chat-error" role="alert"><p>{t[error]}</p>{retry&&<button type="button" onClick={()=>send(retry.text,retry.previous)}>{t.retry}</button>}</div>}<div ref={end}/>
   </div>
   <footer className="diana-chat-footer"><button type="button" className="diana-chat-reset" onClick={reset}>{t.clear} ↺</button><form onSubmit={e=>{e.preventDefault();send(question);}}><label className="diana-chat-sr" htmlFor="diana-question">{t.placeholder}</label><input ref={input} id="diana-question" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={1500} autoComplete="off" placeholder={t.placeholder}/><button type="submit" disabled={loading||!question.trim()} aria-label={t.send}>↑</button></form><p>{t.privacy}</p></footer>
  </div>
 </dialog>;
}
