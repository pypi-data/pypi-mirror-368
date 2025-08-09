// Global helpers: toast & dialog, and small utilities for URL/port sync
(function(){
  window.RocmUI = window.RocmUI || {};

  RocmUI.toast = function(msg){
    const wrap = document.getElementById('toasts') || (()=>{ const d=document.createElement('div'); d.id='toasts'; d.style.position='fixed'; d.style.right='1rem'; d.style.bottom='1rem'; d.style.display='grid'; d.style.gap='.5rem'; d.style.zIndex='50'; document.body.appendChild(d); return d; })();
    const el = document.createElement('div');
    el.className = 'toast';
    el.textContent = msg;
    wrap.appendChild(el);
    setTimeout(()=> el.remove(), 3000);
  };

  RocmUI.showDialog = function(msg){
    const dlg = document.getElementById('miniDialog') || (()=>{ const dlg=document.createElement('dialog'); dlg.id='miniDialog'; dlg.innerHTML = `
      <article>
        <header>
          <strong>Hinweis</strong>
          <button aria-label="Close" rel="prev" onclick="document.getElementById('miniDialog').close()"></button>
        </header>
        <p class="msg">&nbsp;</p>
        <footer>
          <button class="primary" onclick="document.getElementById('miniDialog').close()">OK</button>
        </footer>
      </article>`; document.body.appendChild(dlg); return dlg; })();
    dlg.querySelector('.msg').textContent = msg;
    dlg.showModal();
  };

  // Utility: sync URL when host/port inputs change
  RocmUI.syncUrlFromHostPort = function(tool){
    const urlEl = document.getElementById(`url-${tool}`);
    const hostEl = document.getElementById(`host-${tool}`);
    const portEl = document.getElementById(`port-${tool}`);
    if (!urlEl || !hostEl || !portEl) return;
    let value = (urlEl.value || '').trim();
    if (!value) { value = 'http://'+(hostEl.value||'localhost'); }
    try {
      const u = new URL(value);
      if (hostEl.value) u.hostname = hostEl.value.trim();
      if (portEl.value) u.port = String(portEl.value).trim();
      urlEl.value = u.toString();
    } catch {
      // fallback, overwrite with composed one
      const host = hostEl.value || 'localhost';
      const port = portEl.value ? `:${portEl.value}` : '';
      urlEl.value = `http://${host}${port}`;
    }
  };

  // Utility: sync Host/Port when URL changes
  RocmUI.syncHostPortFromUrl = function(tool){
    const urlEl = document.getElementById(`url-${tool}`);
    const hostEl = document.getElementById(`host-${tool}`);
    const portEl = document.getElementById(`port-${tool}`);
    if (!urlEl || !hostEl || !portEl) return;
    const value = (urlEl.value || '').trim();
    if (!value) return;
    try {
      const u = new URL(value);
      if (u.hostname && !hostEl.value) hostEl.value = u.hostname;
      if (u.port && !portEl.value) portEl.value = u.port;
    } catch {/* ignore parse errors */}
  };
})();
