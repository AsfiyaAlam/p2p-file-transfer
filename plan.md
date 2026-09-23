# Implementation Plan

## Overview
Transform the application into a WhatsApp-style interface, merging peer discovery, file transfers, and a new text messaging feature into a unified chat interface.

## 1. Backend Changes (`transfer.py`)
- Add a global `chat_messages` list to store message history.
- Modify `FileTransfer.server()` to accept headers starting with `CHAT|`. When received, append to `chat_messages`.
- Add `FileTransfer.send_message(target_ip, message)` to initiate a TCP connection and send a `CHAT|...` header.
- Maintain existing `file_name|file_size|file_hash` logic for backward compatibility and file transfers.

## 2. Web API Changes (`web_app.py`)
- Add `GET /api/chat?peer=IP` to fetch chat history with a specific peer.
- Add `POST /api/chat` to send a text message.
- Modify `POST /api/send` to also record a "File Sent" event in the `chat_messages` history.

## 3. Frontend Changes (`templates/index.html`)
- Redesign the layout to a 2-column Chat UI:
  - **Left Sidebar:** Network Scanner and list of Discovered Peers (like chat contacts).
  - **Right Main Area:** 
    - **Header:** Currently selected peer's Alias and IP.
    - **Message Area:** Scrollable list of chat bubbles (Text messages, File transferred notifications).
    - **Input Area:** Text input field for messages, and an attachment button (paperclip) to send files via drag-and-drop or file picker.
- Add polling for `/api/chat?peer=IP` to auto-refresh the chat when the user has a peer selected.

