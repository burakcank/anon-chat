<template>
  <div class="h-dvh container mx-auto p-4 flex flex-col">
    <div class="flex justify-between items-center mb-3">
      <RouterLink :to="{ name: 'Landing' }" class="text-2xl font-medium">Anon Chat</RouterLink>
      <div class="px-3 text-green-600">People: {{ roomClientCount }}</div>
    </div>
    <div id="chatSection" class="grow border rounded-lg overflow-auto">
      <div v-for="message in chatHistory" :key="message.id" class="p-2"
        :class="message.role === 'server' ? 'text-blue-400 mr-10' : 'text-right ml-10'">
        <div class="border rounded-lg inline-block p-2 border-gray-700 whitespace-pre-wrap">
          {{ message.message }}
          <div class="text-xs text-gray-600">{{ message.timestamp }}</div>
        </div>
      </div>
    </div>
    <form @submit.prevent="handleSendMessage(inputMessage)">
      <div class="flex flex-col mt-4">
        <TextArea
          class="max-h-[20vh] min-h-[5vh]"
          placeholder="Type your message"
          v-model="inputMessage"
          rows="4"
          maxlength="2000"
          @keydown="handleKeydown"
        />
        <div class="flex justify-between py-2 gap-2">
          <div class="text-xs bg-gray-800 opacity-50 w-full rounded-lg flex items-center p-2">
            <span v-if="!isMobile">Press Ctrl + Enter to send</span>
          </div>
          <Button :disabled="!inputMessage" type="submit" icon="pi pi-send" size="small" class="px-5!" />
        </div>
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
const isMobile = ref(false);

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
	detectMobile();
});

const detectMobile = () => {
	const userAgent = navigator.userAgent || navigator.vendor;
	isMobile.value =
		/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
			userAgent.toLowerCase(),
		);
};

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
	if (!message.trim()) return;
	sendMessage(message);
	inputMessage.value = "";

	// keep the focus on the input field
	const inputField = document.querySelector("textarea");
	if (inputField) {
		(inputField as HTMLTextAreaElement).focus();
	}
};

const handleKeydown = (event: KeyboardEvent) => {
	if (event.ctrlKey && event.key === "Enter") {
		event.preventDefault();
		handleSendMessage(inputMessage.value);
	}
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
