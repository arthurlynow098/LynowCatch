const $ = s => document.querySelector(s);
function read(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function save(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { msg('Armazenamento do navegador indisponível.'); } }
let jobs = [], running = false, paused = false;
let history = read('octohistory', []);
if (!Array.isArray(history)) history = [];
let endpoint = localStorage.getItem('octoendpoint') || (['localhost','127.0.0.1'].includes(location.hostname) && location.port === '8765' ? location.origin : '');
$('#endpoint').value = endpoint;
const msg = text => $('#message').textContent = text;
const bytes = n => n ? (n / 1048576).toFixed(2) + ' MB' : '—';
function tab(id) {
  ['download','history','settings'].forEach(t => $('#'+t).hidden = t !== id);
  document.querySelectorAll('[data-tab]').forEach(b => b.classList.toggle('active', b.dataset.tab === id));
  if (id === 'history') renderHistory();
}
document.querySelectorAll('[data-tab]').forEach(b => b.onclick = () => tab(b.dataset.tab));
$('#theme').onclick = () => { document.body.classList.toggle('light'); localStorage.setItem('octotheme', document.body.classList.contains('light') ? 'light' : 'dark'); };
if (localStorage.getItem('octotheme') === 'light') document.body.classList.add('light');
const prefs = read('octoprefs', {});
for (const id of ['format','quality']) {
  if (prefs[id]) $('#'+id).value = prefs[id];
  $('#'+id).onchange = () => save('octoprefs', {format: $('#format').value, quality: $('#quality').value});
}
$('#paste').onclick = async () => { try { $('#urls').value = await navigator.clipboard.readText(); } catch { msg('Use Ctrl+V no campo de links.'); $('#urls').focus(); } };
async function api(path, data, timeout) {
  if (!endpoint) throw Error('Conecte o motor na aba Conexão');
  const response = await fetch(endpoint + path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), ...(timeout ? {signal:AbortSignal.timeout(timeout)} : {})});
  const result = await response.json();
  if (!response.ok) throw Error(result.error || 'Operação indisponível');
  return result;
}
function button(label, action) { const b = document.createElement('button'); b.textContent = label; b.onclick = action; return b; }
function render() {
  const q = $('#queue'); q.replaceChildren();
  $('#count').textContent = '/ ' + String(jobs.length).padStart(2, '0');
  const done = jobs.filter(j => j.status === 'Concluído').length;
  $('#stat-total').textContent = jobs.length;
  $('#stat-done').textContent = done;
  $('#stat-size').textContent = bytes(jobs.reduce((n,j) => n+(j.size || 0), 0));
  $('#queueprogress').value = jobs.length ? done / jobs.length * 100 : 0;
  $('#pause').textContent = paused ? '▶ Retomar fila' : 'Ⅱ Pausar fila';
  if (!jobs.length) { const el = document.createElement('div'); el.className='empty'; el.textContent='↙ Sua fila está livre. Cole um link para começar.'; q.append(el); }
  jobs.forEach(j => {
    const row = document.createElement('div'); row.className = 'row';
    const icon = document.createElement('span'); icon.className = 'jobicon'; icon.textContent = j.status === 'Concluído' ? '✓' : j.status === 'Falha' ? '!' : '↙';
    const info = document.createElement('div'); info.className='info';
    const name = document.createElement('strong'); name.textContent=j.url; name.title=j.url;
    const detail = document.createElement('small'); detail.textContent=[j.format.toUpperCase(), j.quality+'p', j.status, j.size ? bytes(j.size) : '', j.error || ''].filter(Boolean).join(' · ');
    info.append(name, detail); row.append(icon,info);
    if (j.file) { const a=document.createElement('a'); a.textContent='Salvar ↓'; a.href=j.file; a.download=''; row.append(a); }
    if (j.status === 'Falha') row.append(button('Tentar novamente', () => { j.status='Aguardando motor'; j.error=''; render(); pump(); }));
    if (j.status !== 'Processando…') row.append(button('Remover', () => { jobs=jobs.filter(x => x !== j); render(); }));
    q.append(row);
  });
}
function renderHistory() {
  const el=$('#historylist'); el.replaceChildren();
  const search=$('#historysearch').value.toLowerCase();
  const filtered=history.slice().reverse().filter(h => h.url.toLowerCase().includes(search));
  if (!filtered.length) el.textContent='Nenhum registro encontrado.';
  filtered.forEach(h => {
    const row=document.createElement('div'); row.className='row';
    const info=document.createElement('div'); info.className='info';
    const title=document.createElement('strong'); title.textContent=h.url;
    const meta=document.createElement('small'); meta.textContent=h.format.toUpperCase()+' · '+new Date(h.date).toLocaleString('pt-BR')+' · '+bytes(h.size);
    info.append(title,meta); row.append(info);
    if (h.file) { const a=document.createElement('a'); a.textContent='Salvar ↓'; a.href=h.file; a.download=''; row.append(a); }
    row.append(button('Repetir', () => { jobs.push({url:h.url,format:h.format,quality:h.quality || '1080',start:h.start || 0,duration:h.duration || 0,status:'Aguardando motor'}); tab('download'); render(); pump(); }));
    el.append(row);
  });
}
$('#historysearch').oninput=renderHistory;
$('#clearhistory').onclick=() => { history=[]; save('octohistory',history); renderHistory(); };
$('#exporthistory').onclick=() => {
  const cell = v => '"'+String(v ?? '').replaceAll('"','""').replace(/^[=+@-]/,"'$&")+'"';
  const rows=[['Link','Formato','Qualidade','Data','Bytes'], ...history.map(h=>[h.url,h.format,h.quality,new Date(h.date).toISOString(),h.size])];
  const url=URL.createObjectURL(new Blob(['\uFEFF'+rows.map(r=>r.map(cell).join(';')).join('\r\n')],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a'); a.href=url; a.download='lynowcatch-historico.csv'; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
};
$('#clear').onclick=() => { jobs=jobs.filter(j=>j.status!=='Concluído'); render(); };
$('#pause').onclick=() => { paused=!paused; render(); if (!paused) pump(); else msg('Fila pausada. O arquivo em processamento será concluído.'); };
$('#clearwaiting').onclick=() => { jobs=jobs.filter(j=>j.status!=='Aguardando motor'); render(); };
async function connect() {
  try {
    const u=new URL($('#endpoint').value);
    if (!['http:','https:'].includes(u.protocol)) throw Error();
    const r=await fetch(u.origin+'/api/health',{signal:AbortSignal.timeout(5000)});
    const data=await r.json(); if (!['lynowcatch','octocatch'].includes(data.service)) throw Error();
    endpoint=u.origin; localStorage.setItem('octoendpoint',endpoint);
    $('#connectionstatus').textContent='Motor '+(data.version || '')+' conectado. '+(data.ffmpeg && data.ffprobe ? 'FFmpeg e ffprobe disponíveis.' : 'Instale FFmpeg e ffprobe para conversões.')+(data.ytdlp === false ? ' yt-dlp ausente.' : '');
    $('#enginebadge').textContent='● Motor conectado';
    pump();
  } catch { $('#connectionstatus').textContent='Não foi possível conectar. Execute INICIAR.bat e abra http://localhost:8765.'; $('#enginebadge').textContent='○ Motor desconectado'; }
}
$('#connect').onclick=connect;
$('#preview').onclick=async () => {
  const url=$('#urls').value.trim().split(/\s+/)[0];
  if (!url) return msg('Cole um link para consultar.');
  $('#preview').disabled=true; $('#previewbox').hidden=false; $('#previewbox').textContent='Consultando informações…';
  try { const p=await api('/api/preview',{url},65000); $('#previewbox').textContent=[p.title,p.uploader,p.duration ? Math.round(p.duration)+' segundos' : '',p.extractor].filter(Boolean).join(' · '); }
  catch(e) { $('#previewbox').textContent=e.message; }
  finally { $('#preview').disabled=false; }
};
document.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>{
  const preset={video:['mp4','1080'],audio:['mp3','1080'],light:['mp4','480'],gif:['gif','480']}[b.dataset.preset];
  $('#format').value=preset[0]; $('#quality').value=preset[1]; $('#duration').value=b.dataset.preset==='gif' ? 15 : ''; $('#start').value='';
  save('octoprefs',{format:preset[0],quality:preset[1]}); msg('Perfil aplicado: '+b.textContent.trim());
});
$('#add').onclick=() => {
  const urls=$('#urls').value.trim().split(/\s+/).filter(Boolean);
  if (!urls.length) return msg('Cole pelo menos um link.');
  if (urls.length>20) return msg('Adicione até 20 links por vez.');
  try { urls.forEach(s=>{if(!['http:','https:'].includes(new URL(s).protocol))throw Error();}); } catch {return msg('Use endereços completos começando com http:// ou https://.');}
  const start=Number($('#start').value), duration=Number($('#duration').value);
  if (!Number.isFinite(start)||!Number.isFinite(duration)||start<0||start>86400||duration<0||duration>3600) return msg('Confira o início (até 86400 s) e a duração (até 3600 s).');
  if ($('#format').value==='original' && (start || duration)) return msg('Escolha MP4, MP3 ou GIF para recortar.');
  let duplicates=0;
  urls.forEach(url=>{
    if (jobs.some(j=>j.url===url&&j.format===$('#format').value&&j.quality===$('#quality').value&&j.start===start&&j.duration===duration&&['Aguardando motor','Processando…'].includes(j.status))) {duplicates++;return;}
    jobs.push({url,format:$('#format').value,quality:$('#quality').value,start,duration,status:'Aguardando motor'});
  });
  $('#urls').value=''; $('#previewbox').hidden=true; render();
  msg(duplicates ? duplicates+' link(s) repetido(s) ignorado(s).' : 'Links adicionados à fila.');
  if (!endpoint) return msg('Conecte o motor na aba Conexão para começar.');
  pump();
};
async function pump() {
  if (running||paused||!endpoint) return;
  running=true;
  try {
    while (!paused) {
      const j=jobs.find(j=>j.status==='Aguardando motor'); if(!j) break;
      j.status='Processando…'; render();
      try {
        const d=await api('/api/download',j); j.file=endpoint+d.file; j.size=d.size; j.status='Concluído';
        history.push({...j,date:Date.now()}); history=history.slice(-100); save('octohistory',history);
        msg('Download pronto. Clique em Salvar para guardar o arquivo.');
      } catch(e) { j.status='Falha'; j.error=e.message; msg(e.message); }
      render();
    }
  } finally { running=false; }
}
render(); if(endpoint) connect();
