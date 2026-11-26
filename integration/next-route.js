// Same-origin gateway: the browser never receives service/provider credentials.
export const runtime='nodejs';
export async function POST(request){
 const json=(error,status)=>Response.json({error},{status,headers:{'Cache-Control':'no-store'}});
 const origin=request.headers.get('origin');
 try{if(origin&&(!['http:','https:'].includes(new URL(origin).protocol)||new URL(origin).host!==request.headers.get('host')))return json('Invalid origin',403);}catch{return json('Invalid origin',403);}
 if(request.headers.get('sec-fetch-site')==='cross-site')return json('Invalid origin',403);
 if(!request.headers.get('content-type')?.startsWith('application/json'))return json('JSON required',415);
 const token=process.env.CHAT_SERVICE_TOKEN,base=process.env.CHAT_SERVICE_URL;
 if(!token||!base)return json('Chat unavailable',503);
 try{
  const reader=request.body?.getReader();if(!reader)return json('Body required',400);
  let size=0;const chunks=[];while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;if(size>16384){await reader.cancel();return json('Request too large',413);}chunks.push(value);}
  const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
  let payload;try{payload=JSON.parse(new TextDecoder().decode(bytes));}catch{return json('Invalid JSON',400);}
  const upstream=await fetch(`${base.replace(/\/$/,'')}/api/chat`,{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},body:JSON.stringify(payload),signal:AbortSignal.any([AbortSignal.timeout(32000),request.signal]),cache:'no-store'});
  if(!upstream.ok){const status=[400,413,422,429,503,504].includes(upstream.status)?upstream.status:502;return json('Chat unavailable',status);}
  const data=await upstream.json();if(typeof data.answer!=='string'||data.answer.length>5000)return json('Invalid response',502);
  return Response.json({answer:data.answer,sources:data.sources||[]},{headers:{'Cache-Control':'no-store'}});
 }catch{return json('Chat unavailable',503);}
}
