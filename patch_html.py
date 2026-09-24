import sys

content = open('templates/index.html').read()

script_top = """    let activePeerIp = null;
    let autoRefreshInterval = null;"""

new_script_top = """    let activePeerIp = null;
    let autoRefreshInterval = null;
    let peersRefreshInterval = null;
    let knownPeersCount = 0;"""
content = content.replace(script_top, new_script_top)

scan_network_str = """      } finally {
        btn.disabled = false;
        btn.textContent = 'Scan';
      }
    }"""

new_scan_network_str = """      } finally {
        btn.disabled = false;
        btn.textContent = 'Scan';
      }
    }

    async function pollPeers() {
      try {
        const res = await fetch('/api/peers');
        const data = await res.json();
        if (data.peers && data.peers.length > 0) {
          if (data.peers.length !== knownPeersCount) {
             // If peer count changed (e.g. new message received), re-render sidebar silently
             knownPeersCount = data.peers.length;
             renderPeerList(data.peers);
          }
        }
      } catch (e) {}
    }

    function renderPeerList(peers) {
        const list = document.getElementById('peer-list');
        list.innerHTML = '';
        peers.forEach(peer => {
            const el = document.createElement('div');
            el.className = 'peer-item' + (activePeerIp === peer.ip ? ' active' : '');
            el.onclick = () => selectPeer(peer.ip, peer.alias || 'Unknown');
            el.innerHTML = `
              <div class="peer-avatar">💻</div>
              <div class="peer-details">
                <div class="peer-alias">${escapeHtml(peer.alias || 'Unknown')}</div>
                <div class="peer-ip">${peer.ip}</div>
              </div>
              <div class="peer-status-dot"></div>
            `;
            list.appendChild(el);
        });
    }"""
content = content.replace(scan_network_str, new_scan_network_str)

# In scanNetwork we also want to call renderPeerList
scan_replace_str = """        if (!data.peers || data.peers.length === 0) {
          list.innerHTML = '<div style="padding: 30px 20px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No peers found.<br>Make sure they are running the app.</div>';
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
              <div class="peer-status-dot"></div>
            `;
            list.appendChild(el);
          });
        }"""

new_scan_replace_str = """        if (!data.peers || data.peers.length === 0) {
          list.innerHTML = '<div style="padding: 30px 20px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No peers found.<br>Make sure they are running the app.</div>';
          knownPeersCount = 0;
        } else {
          knownPeersCount = data.peers.length;
          renderPeerList(data.peers);
        }"""
content = content.replace(scan_replace_str, new_scan_replace_str)

init_str = """    // Allow enter key in modal
    document.getElementById('path-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendPath();
        }
    });"""

new_init_str = """    // Allow enter key in modal
    document.getElementById('path-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendPath();
        }
    });
    
    // Start polling peers list automatically
    peersRefreshInterval = setInterval(pollPeers, 3000);
    pollPeers(); // initial call"""
content = content.replace(init_str, new_init_str)

open('templates/index.html', 'w').write(content)
