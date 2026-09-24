import sys

content = open('templates/index.html').read()

styles_insert = """    /* Modals & Alerts */"""

new_styles_insert = """    /* Transfer Toasts */
    .toast-container {
      position: absolute;
      top: 20px;
      right: 20px;
      z-index: 1000;
      display: flex;
      flex-direction: column;
      gap: 10px;
      width: 320px;
    }
    
    .toast {
      background-color: var(--sidebar-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 15px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.4);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .toast-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9rem;
      font-weight: 500;
    }
    
    .toast-filename {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 200px;
    }
    
    .toast-percent {
      color: var(--accent);
      font-weight: 600;
      font-size: 0.8rem;
    }
    
    .progress-bar-bg {
      height: 6px;
      background-color: var(--input-bg);
      border-radius: 3px;
      overflow: hidden;
    }
    
    .progress-bar-fill {
      height: 100%;
      background-color: var(--accent);
      width: 0%;
      transition: width 0.2s ease-out;
      box-shadow: 0 0 10px var(--accent-glow);
    }
    
    /* Modals & Alerts */"""
content = content.replace(styles_insert, new_styles_insert)

html_insert = """  <!-- Main Chat -->
  <div class="chat-area">"""

new_html_insert = """  <!-- Main Chat -->
  <div class="chat-area">
    <div class="toast-container" id="toast-container"></div>"""
content = content.replace(html_insert, new_html_insert)

js_insert = """    // Start polling peers list automatically
    peersRefreshInterval = setInterval(pollPeers, 3000);"""

new_js_insert = """    async function pollProgress() {
      try {
        const res = await fetch('/api/progress');
        const data = await res.json();
        const container = document.getElementById('toast-container');
        
        if (!data.transfers || data.transfers.length === 0) {
          container.innerHTML = '';
          return;
        }
        
        container.innerHTML = data.transfers.map(t => {
          const percent = t.total > 0 ? Math.floor((t.transferred / t.total) * 100) : 0;
          const directionIcon = t.direction === 'out' ? '↗️ Sending' : '↙️ Receiving';
          return `
            <div class="toast">
              <div class="toast-header">
                <span style="font-size: 0.8rem; opacity: 0.7;">${directionIcon}</span>
                <span class="toast-percent">${percent}%</span>
              </div>
              <div class="toast-filename" title="${escapeHtml(t.file_name)}">${escapeHtml(t.file_name)}</div>
              <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: ${percent}%;"></div>
              </div>
              <div style="font-size: 0.75rem; opacity: 0.6; text-align: right;">
                ${formatBytes(t.transferred)} / ${formatBytes(t.total)}
              </div>
            </div>
          `;
        }).join('');
      } catch (e) {}
    }
    
    function formatBytes(bytes) {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Start polling peers list automatically
    peersRefreshInterval = setInterval(pollPeers, 3000);
    setInterval(pollProgress, 1000);"""
content = content.replace(js_insert, new_js_insert)

open('templates/index.html', 'w').write(content)
