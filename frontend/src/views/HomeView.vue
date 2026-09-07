<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { getMeetings, getLocations } from "@/services/api";
import AiSearchBar from "@/components/AiSearchBar.vue";
import MeetingCard from "@/components/MeetingCard.vue";
import PlaceCard from "@/components/PlaceCard.vue";
import serviceLogo from "@/assets/moyeou_logo.svg";
import KakaoMap from "@/components/KakaoMap.vue";

const router = useRouter();
const meetings = ref([]);
const places = ref([]);

const suggestions = ["여행", "대전 시청", "맛집"];

onMounted(async () => {
  const meetingsData = await getMeetings();
  const meetingsList =
    meetingsData && meetingsData.items
      ? meetingsData.items
      : Array.isArray(meetingsData)
        ? meetingsData
        : [];

  meetings.value = meetingsList;

  const locationsData = await getLocations();
  const locationsList = Array.isArray(locationsData) ? locationsData : [];

  places.value = locationsList.slice(0, 4);
});

const recentMeetings = computed(() => {
  return meetings.value.slice(0, 4);
});

function handleSearch(query) {
  router.push({ path: "/meetings", query: { q: query } });
}
</script>

<template>
  <div class="home-view-container">
    <section class="bg-white">
      <div class="mx-auto max-w-6xl px-6 py-12 text-center flex flex-col items-center">
        <div class="mb-1 transition-transform duration-300 hover:scale-105 active:scale-95">
          <img
            :src="serviceLogo"
            alt="SSAFY 모여유 로고"
            class="mx-auto h-40 w-auto object-contain drop-shadow-md"
          />
        </div>

        <h1 class="mt-0 text-balance text-4xl font-bold text-ink md:text-5xl">
          교육 끝나고, 누구와 함께할까요?
        </h1>
        <p class="mx-auto mt-4 max-w-2xl text-pretty text-lg leading-relaxed text-ink/70">
          모각코·CS 스터디부터 프로젝트 팀원, 점심 메이트, 러닝까지. 같은 기수 동료들과 번개로
          모여요.
        </p>
        <div class="mx-auto mt-8 max-w-2xl w-full">
          <AiSearchBar :suggestions="suggestions" @search="handleSearch" />
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-6xl px-6 py-12">
      <div class="mb-6 flex items-center justify-between">
        <h2 class="text-2xl font-bold text-ink">지금 모집 중인 번개</h2>
        <RouterLink to="/meetings" class="text-sm font-medium text-brand hover:text-brand-hover">
          전체 보기
        </RouterLink>
      </div>
      <div class="grid gap-6 md:grid-cols-12 items-stretch">
        <div class="md:col-span-5 min-h-[380px] flex">
          <KakaoMap :meetings="meetings" :is-cluster="true" class="w-full h-full" />
        </div>
        <div class="md:col-span-7 grid gap-4 grid-cols-1 sm:grid-cols-2 content-start">
          <MeetingCard v-for="m in recentMeetings" :key="m.id" :meeting="m" />
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-6xl px-6 pb-16">
      <div class="mb-6 flex items-center justify-between">
        <h2 class="text-2xl font-bold text-ink">캠퍼스 주변, 같이 가볼까요?</h2>
        <RouterLink to="/locations" class="text-sm font-medium text-brand hover:text-brand-hover">
          전체 보기
        </RouterLink>
      </div>
      <div class="grid gap-5 md:grid-cols-4">
        <PlaceCard v-for="p in places" :key="p.id" :place="p" />
      </div>
    </section>
  </div>
</template>
