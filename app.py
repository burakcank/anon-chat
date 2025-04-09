import json
import uuid
from datetime import datetime, timezone

import redis
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from loguru import logger

from config import Config

r = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
socketio = SocketIO(cors_allowed_origins="*")

clients_per_room: dict[str, set] = {}
client_count = 0


@socketio.on("connect")
def handle_connect():
    logger.debug(f"Client connected: {request.sid}")
    global client_count
    client_count += 1
    emit("client_count", client_count, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    logger.debug(f"Client disconnected: {request.sid}")
    global client_count
    client_count -= 1
    emit("client_count", client_count, broadcast=True)

    for room_id, clients in clients_per_room.items():
        if request.sid in clients:
            clients.discard(request.sid)
            leave_room(room_id)
            emit(
                "room_client_count",
                {"room_id": room_id, "client_count": len(clients)},
                room=room_id,
            )

    rooms_to_remove = []
    for room_id, clients in clients_per_room.items():
        if not clients:
            rooms_to_remove.append(room_id)

    for room_id in rooms_to_remove:
        del clients_per_room[room_id]
        logger.debug(f"Removed empty room: {room_id}")


@socketio.on("join_room")
def handle_join_room(data):
    room_id = data
    logger.debug(f"Client {request.sid} joined room: {room_id}")
    clients_per_room.setdefault(room_id, set())
    clients_per_room[room_id].add(request.sid)
    join_room(room_id)
    emit(
        "room_client_count",
        {"room_id": room_id, "client_count": len(clients_per_room[room_id])},
        room=room_id,
    )


@socketio.on("chat_message")
def handle_message(data):
    logger.debug(f"Received message: {data}")
    message = {
        "room_id": data["room_id"],
        "message": data["message"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    message_key = f"{data['room_id']}:{uuid.uuid4()}"
    r.set(message_key, json.dumps(message), ex=60 * 60 * 24)  # 24 hours
    emit("chat_message", message, to=data["room_id"], skip_sid=request.sid)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    socketio.init_app(app)

    @app.route("/chat/<room_id>")
    def chat_history(room_id):
        messages = []
        for key in r.scan_iter(f"{room_id}:*"):
            message = r.get(key)
            if message:
                messages.append(json.loads(message))

        messages.sort(key=lambda x: x["timestamp"])
        return jsonify(messages)

    return app
