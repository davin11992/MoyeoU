import { createRouter, createWebHistory } from "vue-router";

import HomeView from "@/views/HomeView.vue";
import MeetingListView from "@/views/MeetingListView.vue";
import MeetingNewView from "@/views/MeetingNewView.vue";
import MeetingDetailView from "@/views/MeetingDetailView.vue";
import LocationsView from "@/views/LocationsView.vue";

const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/meetings", name: "meetings", component: MeetingListView },
  { path: "/meetings/new", name: "meeting-new", component: MeetingNewView },
  { path: "/meetings/:id", name: "meeting-detail", component: MeetingDetailView },
  { path: "/locations", name: "locations", component: LocationsView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
