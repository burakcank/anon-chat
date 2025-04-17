<script setup lang="ts">
import Button from "primevue/button";
import TextArea from "primevue/textarea";
import { io } from "socket.io-client";
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

interface ChatHistory {
	id: string;
	role: "server" | "user";
	message: string;
	timestamp: string;
}

const $router = useRouter();
const $route = useRoute();
const socket = io(BACKEND_URL);
const roomClientCount = ref(0);
const totalClientCount = ref(0);
const inputMessage = ref("");
const chatHistory = ref<ChatHistory[]>([]);
const chatRoomId = ref<string>("");

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

onMounted(async () => {
	await $router.isReady();
	chatRoomId.value = $route.query.chat_id as string;
	if (!chatRoomId.value) {
		chatRoomId.value = Math.random().toString(36).substring(7);
		$router.push({ query: { chat_id: chatRoomId.value } });
	}

	socket.emit("join_room", chatRoomId.value);
	getChatHistory();
	setupScrollObserver("#chatSection");
});

const getChatHistory = async () => {
	try {
		const response = await fetch(`${BACKEND_URL}/chat/${chatRoomId.value}`, {
			method: "GET",
			headers: { "Content-Type": "application/json" },
		});
		if (!response.ok) {
			throw new Error("Request failed for chat history");
		}

		const data = await response.json();
		chatHistory.value = data.map((message: any) => ({
			id: message.id,
			role: "server",
			message: message.message,
			timestamp: new Date(message.timestamp).toLocaleString(),
		}));
	} catch (error) {
		console.error("Error fetching chat history:", error);
	}
};

const sendMessage = (message: string) => {
	if (!message) return;
	chatHistory.value.push({
		id: Math.random().toString(36).substring(7),
		role: "user",
		message,
		timestamp: new Date().toLocaleString(),
	});
	socket.emit("chat_message", {
		room_id: chatRoomId.value,
		message,
	});
	inputMessage.value = "";
};

function setupScrollObserver(containerSelector: string) {
	const container = document.querySelector(containerSelector);
	if (!container) return;

	const observer = new MutationObserver(() => {
		container.scrollTo({
			top: container.scrollHeight,
			behavior: "smooth",
		});
	});

	observer.observe(container, {
		childList: true,
		subtree: true,
	});

	return observer;
}
</script>

<template>
  <div class="container mx-auto p-4">
	<div class="flex justify-between items-center mb-3">
		<h1 class="text-2xl font-medium">Anon Chat</h1>
		<div class="px-3 text-green-600">{{ roomClientCount }}/{{ totalClientCount }}</div>
	</div>
    <div id="chatSection" class="border rounded-lg h-[60vh] overflow-auto">
      <div v-for="message in chatHistory" :key="message.id" class="p-2" :class="message.role === 'server' ? 'text-blue-400 mr-10' : 'text-right ml-10'">
        <div
          class="border rounded-lg inline-block p-2 border-gray-700 whitespace-pre-wrap"
        >
          {{ message.message }}
          <div class="text-xs text-gray-600">{{ message.timestamp }}</div>
        </div>
      </div>
    </div>
    <form @submit.prevent="sendMessage(inputMessage)">
      <div class="flex mt-4 w-full">
        <TextArea
          class="grow me-4 max-h-100"
          placeholder="Type your message"
          v-model="inputMessage"
          rows="5"
		  maxlength="2000"
        />
        <Button :disabled="!inputMessage" type="submit" label="Send" />
      </div>
    </form>
  </div>
</template>

<style scoped>
</style>
