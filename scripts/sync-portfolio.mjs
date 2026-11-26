import {copyFile,mkdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const portfolio=path.resolve(process.argv[2]||path.join(root,'../diana-creative-portfolio'));
await mkdir(path.join(portfolio,'frontend/components/diana-llm'),{recursive:true});
for(const file of ['ChatSidebar.jsx','chat.css'])await copyFile(path.join(root,'react',file),path.join(portfolio,'frontend/components/diana-llm',file));
console.log('Synced the React sidebar into '+portfolio);
