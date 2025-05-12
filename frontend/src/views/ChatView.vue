<template>
  <div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-3">
      <RouterLink :to="{ name: 'Landing' }" class="text-2xl font-medium">Anon Chat</RouterLink>
      <div class="px-3 text-green-600">People: {{ roomClientCount }}</div>
    </div>
    <div id="chatSection" class="border rounded-lg h-[60vh] overflow-auto">
      <div v-for="message in chatHistory" :key="message.id" class="p-2" :class="message.role === 'server' ? 'text-blue-400 mr-10' : 'text-right ml-10'">
        <div class="border rounded-lg inline-block p-2 border-gray-700 whitespace-pre-wrap">
          {{ message.message }}
          <div class="text-xs text-gray-600">{{ message.timestamp }}</div>
        </div>
      </div>
    </div>
    <form @submit.prevent="handleSendMessage(inputMessage)" v-on:keypress.ctrl.enter="handleSendMessage(inputMessage)">
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

<script setup lang="ts">
import {
	chatHistory,
	chatRoomId,
	joinRoom,
	roomClientCount,
	sendMessage,
} from "@/composables/socket";
import Button from "primevue/button";
import TextArea from "primevue/textarea";
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const $router = useRouter();
const $route = useRoute();
const inputMessage = ref("");

interface ChatMessage {
	message: string;
	room_id: string;
	timestamp: string;
}

onMounted(async () => {
	await $router.isReady();
	chatRoomId.value = $route.params.roomId as string;
	joinRoom(chatRoomId.value);
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
		chatHistory.value = data.map((message: ChatMessage, index: number) => ({
			id: index,
			role: "server",
			message: message.message,
			timestamp: new Date(message.timestamp).toLocaleString(),
		}));
	} catch (error) {
		console.error("Error fetching chat history:", error);
	}
};

const handleSendMessage = async (message: string) => {
	sendMessage(message);
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

<style scoped>
</style>
