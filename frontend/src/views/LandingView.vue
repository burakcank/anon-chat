<template>
    <div class="p-4 flex items-center justify-center min-h-screen">
        <div class="text-center">
            <h1 class="text-4xl mb-10 font-bold text-gray-200">Anonymous Chat</h1>
            <p class="mt-4 text-gray-300">No log records, no tracking, no registration needed.</p>
            <p class="mb-4 text-gray-300">Messages auto-delete after 24 hours.</p>
            <p class="mb-10 text-gray-300">
                Total Users:
                <span class="text-green-400">{{ totalClientCount }}</span>
            </p>
            <Button @click="startChat()" label="Start Chat" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { totalClientCount } from "@/composables/socket";
import Button from "primevue/button";
import { useRouter } from "vue-router";

const $router = useRouter();

const startChat = () => {
	const chatRoomId = Math.random().toString(36).substring(6);
	$router.push({ name: "Chat", params: { roomId: chatRoomId } });
};
</script>

<style scoped></style>
