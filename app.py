from datetime import datetime, timezone

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sock import Sock

app = Flask(__name__)
CORS(app)
sock = Sock(app)

chat_rooms = {}  # {room_id: {"messages": [], "clients": set()}}


@app.route("/chat/<room_id>")
def get_chat_messages(room_id):
    return jsonify(chat_rooms.get(room_id, {}).get("messages", []))


@sock.route("/chat/<room_id>")
def chat_socket(ws, room_id):
    if room_id not in chat_rooms:
        chat_rooms[room_id] = {"messages": [], "clients": set()}

    chat_rooms[room_id]["clients"].add(ws)

    try:
        while True:
            print("active clients", len(chat_rooms[room_id]["clients"]))
            message = ws.receive()
            if message:
                chat_message = {
                    "message": message,
                    "sent_at": datetime.now(tz=timezone.utc).isoformat(),
                }
                chat_rooms[room_id]["messages"].append(chat_message)

                for client in chat_rooms[room_id]["clients"]:
                    if client != ws:
                        client.send(message)
    finally:
        chat_rooms[room_id]["clients"].remove(ws)
