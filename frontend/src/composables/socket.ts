import { type Socket, io } from "socket.io-client";
import { type Ref, ref } from "vue";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

// Single socket instance
let socket: Socket | null = null;

// Reactive global variables
export const totalClientCount: Ref<number> = ref(0);
export const roomClientCount: Ref<number> = ref(0);
export const chatHistory: Ref<ChatHistory[]> = ref([]);
export const chatRoomId: Ref<string> = ref("");

interface ChatHistory {
	id: string;
	role: "server" | "user";
	message: string;
	timestamp: string;
}

// Initialize socket and listeners
function initializeSocket(): Socket {
	if (!socket) {
		socket = io(BACKEND_URL);
		setupSocketListeners();
	}
	return socket;
}

function setupSocketListeners() {
	if (!socket) return;

	socket.on("client_count", (count: number) => {
		totalClientCount.value = count;
	});

	socket.on("room_client_count", ({ room_id, client_count }) => {
		if (room_id === chatRoomId.value) {
			roomClientCount.value = client_count;
		}
	});

	socket.on("chat_message", (data) => {
		chatHistory.value.push({
			id: Math.random().toString(36).substring(7),
			role: "server",
			message: data.message,
			timestamp: new Date(data.timestamp).toLocaleString(),
		});
	});
}

// Export methods
export function getSocket(): Socket {
	return initializeSocket();
}

export function joinRoom(roomId: string) {
	chatRoomId.value = roomId;
	getSocket().emit("join_room", roomId);
}

export function sendMessage(message: string) {
	if (!message) return;
	chatHistory.value.push({
		id: Math.random().toString(36).substring(7),
		role: "user",
		message,
		timestamp: new Date().toLocaleString(),
	});
	getSocket().emit("chat_message", {
		room_id: chatRoomId.value,
		message,
	});
}

// Initialize socket on module load
initializeSocket();
