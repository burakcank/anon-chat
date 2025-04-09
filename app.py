import json
import uuid
from datetime import datetime, timezone

import redis
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from loguru import logger

from config import Config

r = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
socketio = SocketIO(cors_allowed_origins="*")

connected_clients = set[str]()


@socketio.on("connect")
def handle_connect():
    logger.debug(f"Client connected: {request.sid}")
    connected_clients.add(request.sid)
    logger.debug(f"Connected clients: {connected_clients}")
    socketio.emit("client_count", len(connected_clients))


@socketio.on("disconnect")
def handle_disconnect():
    logger.debug(f"Client disconnected: {request.sid}")
    connected_clients.discard(request.sid)
    logger.debug(f"Connected clients: {connected_clients}")
    socketio.emit("client_count", len(connected_clients))


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
    socketio.emit("chat_message", message, skip_sid=request.sid)


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
