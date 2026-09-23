html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>P2P File Transfer & Chat</title>
  <style>
    :root {
      --bg: #0a0a0a;
      --sidebar-bg: #111b21;
      --chat-bg: #0b141a;
      --header-bg: #202c33;
      --message-in: #202c33;
      --message-out: #005c4b;
      --text-main: #e9edef;
      --text-muted: #8696a0;
      --accent: #00a884;
      --accent-hover: #008f6f;
      --border: #222d34;
      --input-bg: #2a3942;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    /* Sidebar (Left) */
    .sidebar {
      width: 350px;
      background-color: var(--sidebar-bg);
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border);
    }
    
    .sidebar-header {
      background-color: var(--header-bg);
      padding: 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 60px;
    }
    
    .scan-btn {
      background-color: var(--accent);
      color: #fff;
      border: none;
      padding: 8px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
    }
    .scan-btn:hover { background-color: var(--accent-hover); }
    .scan-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    .peer-list {
      flex-grow: 1;
      overflow-y: auto;
    }
    
    .peer-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      cursor: pointer;
      border-bottom: 1px solid var(--border);
    }
    
    .peer-item:hover, .peer-item.active {
      background-color: var(--header-bg);
    }
    
    .peer-avatar {
      width: 45px;
      height: 45px;
      border-radius: 50%;
      background-color: var(--accent);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      margin-right: 15px;
    }

    .peer-details { flex-grow: 1; }
    .peer-alias { font-size: 16px; margin-bottom: 3px; }
    .peer-ip { font-size: 13px; color: var(--text-muted); }

    /* Main Chat Area (Right) */
    .chat-area {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      background-color: var(--chat-bg);
      position: relative;
    }
    
    .empty-chat {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: var(--chat-bg);
      z-index: 10;
      color: var(--text-muted);
      font-size: 18px;
    }

    .chat-header {
      background-color: var(--header-bg);
      padding: 10px 20px;
      display: flex;
      align-items: center;
      height: 60px;
    }
    
    .chat-header .peer-alias { font-weight: 500; font-size: 16px; margin-bottom: 2px;}
    
    .messages-container {
      flex-grow: 1;
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    
    .message {
      max-width: 65%;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 15px;
      line-height: 1.4;
      position: relative;
      word-wrap: break-word;
    }
    
    .message.in {
      align-self: flex-start;
      background-color: var(--message-in);
      border-top-left-radius: 0;
    }
    
    .message.out {
      align-self: flex-end;
      background-color: var(--message-out);
      border-top-right-radius: 0;
    }
    
    .message-time {
      font-size: 11px;
      color: rgba(255,255,255,0.6);
      text-align: right;
      margin-top: 4px;
    }

    .file-attachment {
      display: flex;
      align-items: center;
      background: rgba(0,0,0,0.2);
      padding: 10px;
      border-radius: 6px;
      margin-bottom: 5px;
      border: 1px solid rgba(255,255,255,0.1);
    }
    .file-icon { font-size: 24px; margin-right: 12px; }
    .file-name { font-weight: 500; font-size: 14px; }

    /* Input Area */
    .input-area {
      background-color: var(--header-bg);
      padding: 12px 20px;
      display: flex;
      align-items: center;
      gap: 15px;
    }
    
    .action-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 22px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: color 0.2s;
    }
    .action-btn:hover { color: var(--text-main); }
    
    .message-input {
      flex-grow: 1;
      background-color: var(--input-bg);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 12px 15px;
      border-radius: 8px;
      font-size: 15px;
      outline: none;
    }
    .message-input:focus { border-color: var(--accent); }

    /* Modals & Alerts */
    .modal {
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
      align-items: center; justify-content: center; z-index: 100;
    }
    .modal-content {
      background: var(--header-bg); padding: 25px; border-radius: 12px; width: 400px;
      border: 1px solid var(--border);
    }
    .modal h3 { margin-bottom: 15px; }
    .modal input { width: 100%; padding: 10px; margin-bottom: 15px; border-radius: 6px; border: 1px solid var(--border); background: var(--input-bg); color: white; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; }
    .btn { padding: 8px 15px; border-radius: 6px; border: none; cursor: pointer; color: white; font-weight:500;}
    .btn-cancel { background: var(--border); }
    .btn-primary { background: var(--accent); }

  </style>
</head>
<body>

  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Peers</h2>
      <button class="scan-btn" id="scan-btn" onclick="scanNetwork()">Scan</button>
    </div>
    <div class="peer-list" id="peer-list">
      <div style="padding: 20px; text-align: center; color: var(--text-muted);">
        Click Scan to find peers
      </div>
    </div>
  </div>

  <!-- Main Chat -->
  <div class="chat-area">
    <div class="empty-chat" id="empty-chat">Select a peer to start chatting or transferring files</div>
    
    <div class="chat-header">
      <div class="peer-avatar">💻</div>
      <div class="peer-details">
        <div class="peer-alias" id="active-peer-alias">Alias</div>
        <div class="peer-ip" id="active-peer-ip">192.168.x.x</div>
      </div>
    </div>
    
    <div class="messages-container" id="messages-container">
      <!-- Messages will load here -->
    </div>
    
    <div class="input-area">
      <!-- File Upload button -->
      <button class="action-btn" title="Send File" onclick="document.getElementById('file-input').click()">📎</button>
      <input type="file" id="file-input" style="display: none;" onchange="sendFile(this.files[0])">
      
      <!-- Folder/Path Upload button -->
      <button class="action-btn" title="Send Folder Path" onclick="openPathModal()">📁</button>
      
      <input type="text" class="message-input" id="message-input" placeholder="Type a message..." onkeypress="handleEnter(event)">
      <button class="action-btn" onclick="sendTextMessage()">➤</button>
    </div>
  </div>

  <!-- Send Path Modal -->
  <div class="modal" id="path-modal">
    <div class="modal-content">
      <h3>Send Local Folder/File Path</h3>
      <input type="text" id="path-input" placeholder="e.g. /home/user/Documents/folder">
      <div class="modal-actions">
        <button class="btn btn-cancel" onclick="closePathModal()">Cancel</button>
        <button class="btn btn-primary" onclick="sendPath()">Send</button>
      </div>
    </div>
  </div>

  <script>
    let activePeerIp = null;
    let autoRefreshInterval = null;

    async function scanNetwork() {
      const btn = document.getElementById('scan-btn');
      btn.disabled = true;
      btn.textContent = 'Scanning...';
      try {
        const res = await fetch('/api/scan', { method: 'POST' });
        const data = await res.json();
        const list = document.getElementById('peer-list');
        list.innerHTML = '';
        
        if (!data.peers || data.peers.length === 0) {
          list.innerHTML = '<div style="padding:20px; text-align:center; color:gray;">No peers found.</div>';
        } else {
          data.peers.forEach(peer => {
            const el = document.createElement('div');
            el.className = 'peer-item' + (activePeerIp === peer.ip ? ' active' : '');
            el.onclick = () => selectPeer(peer.ip, peer.alias || 'Unknown');
            el.innerHTML = `
              <div class="peer-avatar">💻</div>
              <div class="peer-details">
                <div class="peer-alias">${escapeHtml(peer.alias || 'Unknown')}</div>
                <div class="peer-ip">${peer.ip}</div>
              </div>
            `;
            list.appendChild(el);
          });
        }
      } catch (e) {
        alert("Scan failed: " + e.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Scan';
      }
    }

    function selectPeer(ip, alias) {
      activePeerIp = ip;
      document.getElementById('empty-chat').style.display = 'none';
      document.getElementById('active-peer-alias').textContent = alias;
      document.getElementById('active-peer-ip').textContent = ip;
      
      // Update UI active state
      document.querySelectorAll('.peer-item').forEach(el => {
        el.classList.remove('active');
        if(el.querySelector('.peer-ip').textContent === ip) el.classList.add('active');
      });

      loadChatHistory();
      if(autoRefreshInterval) clearInterval(autoRefreshInterval);
      autoRefreshInterval = setInterval(loadChatHistory, 2000);
    }

    async function loadChatHistory() {
      if(!activePeerIp) return;
      try {
        const res = await fetch(`/api/chat?peer=${activePeerIp}`);
        const data = await res.json();
        if(data.messages) {
          renderMessages(data.messages);
        }
      } catch (e) {}
    }

    function renderMessages(messages) {
      const container = document.getElementById('messages-container');
      
      // Smart scroll logic: check if we are near bottom before updating
      const isNearBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 50;

      container.innerHTML = messages.map(msg => {
        const timeStr = new Date(msg.timestamp * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        if (msg.type === 'file') {
          return `
            <div class="message ${msg.direction}">
              <div class="file-attachment">
                <div class="file-icon">📄</div>
                <div>
                  <div class="file-name">${escapeHtml(msg.content)}</div>
                  <div style="font-size: 11px; opacity: 0.8;">${msg.direction === 'in' ? 'Received (Saved in inbox)' : 'Sent successfully'}</div>
                </div>
              </div>
              <div class="message-time">${timeStr}</div>
            </div>
          `;
        } else {
          return `
            <div class="message ${msg.direction}">
              <div>${escapeHtml(msg.content)}</div>
              <div class="message-time">${timeStr}</div>
            </div>
          `;
        }
      }).join('');

      if (isNearBottom) {
        container.scrollTop = container.scrollHeight;
      }
    }

    async function sendTextMessage() {
      if(!activePeerIp) return;
      const input = document.getElementById('message-input');
      const text = input.value.trim();
      if(!text) return;
      
      input.value = '';
      try {
        await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({target_ip: activePeerIp, message: text})
        });
        loadChatHistory();
      } catch(e) {
        alert("Failed to send message: " + e.message);
      }
    }

    function handleEnter(e) {
      if(e.key === 'Enter') sendTextMessage();
    }

    async function sendFile(file) {
      if(!file || !activePeerIp) return;
      
      const formData = new FormData();
      formData.append('target_ip', activePeerIp);
      formData.append('file', file);

      try {
        const res = await fetch('/api/send', { method: 'POST', body: formData });
        const data = await res.json();
        if(data.status !== 'success') throw new Error(data.message);
        loadChatHistory();
      } catch(e) {
        alert("Transfer failed: " + e.message);
      }
      document.getElementById('file-input').value = ''; // Reset
    }

    function openPathModal() {
      if(!activePeerIp) {
         alert("Select a peer first.");
         return;
      }
      document.getElementById('path-modal').style.display = 'flex';
    }
    function closePathModal() {
      document.getElementById('path-modal').style.display = 'none';
    }
    async function sendPath() {
      const path = document.getElementById('path-input').value.trim();
      if(!path) return;
      
      closePathModal();
      try {
        const res = await fetch('/api/send', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({target_ip: activePeerIp, file_path: path})
        });
        const data = await res.json();
        if(data.status !== 'success') throw new Error(data.message);
        loadChatHistory();
      } catch(e) {
        alert("Transfer failed: " + e.message);
      }
    }

    function escapeHtml(str) {
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
  </script>
</body>
</html>
"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
