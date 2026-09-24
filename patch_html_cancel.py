import sys

content = open('templates/index.html').read()

styles_insert = """    .toast-percent {
      color: var(--accent);
      font-weight: 600;
      font-size: 0.8rem;
    }"""

new_styles_insert = """    .toast-percent {
      color: var(--accent);
      font-weight: 600;
      font-size: 0.8rem;
    }
    
    .toast-cancel {
      background: none;
      border: none;
      color: var(--danger);
      cursor: pointer;
      font-size: 1.1rem;
      margin-left: 10px;
      padding: 0 5px;
    }
    .toast-cancel:hover { opacity: 0.8; }"""
content = content.replace(styles_insert, new_styles_insert)

js_insert = """              <div class="toast-header">
                <span style="font-size: 0.8rem; opacity: 0.7;">${directionIcon}</span>
                <span class="toast-percent">${percent}%</span>
              </div>
              <div class="toast-filename" title="${escapeHtml(t.file_name)}">${escapeHtml(t.file_name)}</div>
              <div class="progress-bar-bg">"""

new_js_insert = """              <div class="toast-header">
                <span style="font-size: 0.8rem; opacity: 0.7;">${directionIcon}</span>
                <div>
                  <span class="toast-percent">${percent}%</span>
                  <button class="toast-cancel" title="Cancel Transfer" onclick="cancelTransfer('${t.peer_ip}_${t.file_name.replace(/'/g, "\\'")}')">✖</button>
                </div>
              </div>
              <div class="toast-filename" title="${escapeHtml(t.file_name)}">${escapeHtml(t.file_name)}</div>
              <div class="progress-bar-bg">"""
content = content.replace(js_insert, new_js_insert)

js_func_insert = """    function formatBytes(bytes) {"""

new_js_func_insert = """    async function cancelTransfer(transferId) {
      if(!confirm("Are you sure you want to cancel this transfer?")) return;
      try {
        await fetch('/api/cancel', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({transfer_id: transferId})
        });
        // Optimistically remove from UI
        pollProgress();
      } catch (e) {
        alert("Failed to cancel: " + e.message);
      }
    }

    function formatBytes(bytes) {"""
content = content.replace(js_func_insert, new_js_func_insert)

open('templates/index.html', 'w').write(content)
