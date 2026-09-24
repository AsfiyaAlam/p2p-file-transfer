import sys

content = open('web_app.py').read()

import_str = "from transfer import FileTransfer, chat_history"
new_import_str = "from transfer import FileTransfer, chat_history, active_transfers"
content = content.replace(import_str, new_import_str)

get_chat_str = """        elif path == '/api/chat':
            query = parse_qs(parsed.query)"""

new_get_progress_str = """        elif path == '/api/progress':
            self._send_json({"transfers": list(active_transfers.values())})
            
        elif path == '/api/chat':
            query = parse_qs(parsed.query)"""
content = content.replace(get_chat_str, new_get_progress_str)

open('web_app.py', 'w').write(content)
