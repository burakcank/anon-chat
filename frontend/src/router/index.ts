import { createRouter, createWebHistory } from "vue-router";

const routes = [
	{
		path: "/",
		name: "Landing",
		component: () => import("@/views/LandingView.vue"),
	},
	{
		path: "/:roomId",
		name: "Chat",
		component: () => import("@/views/ChatView.vue"),
	},
];

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes,
});

export default router;
