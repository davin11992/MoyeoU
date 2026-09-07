<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getMeetings } from "@/services/api";
import MeetingCard from "@/components/MeetingCard.vue";
import CategoryFilter from "@/components/CategoryFilter.vue";

const route = useRoute();

const meetings = ref([]);
const isLoading = ref(false);
const errorMsg = ref("");

const keyword = ref(route.query.q ? String(route.query.q) : "");
const selectedCategory = ref("전체");
const onlyOpen = ref(false);

const categories = ["전체", "관광", "문화생활", "운동·산책", "맛집", "쇼핑", "여행"];

onMounted(async () => {
  isLoading.value = true;
  errorMsg.value = "";
  try {
    const response = await getMeetings();

    // 콘솔에서 보인 구조에 맞추어 items 배열을 안전하게 추출합니다.
    if (response && Array.isArray(response.items)) {
      // response 자체가 { items: [...] } 인 경우
      meetings.value = response.items;
    } else if (response && response.data && Array.isArray(response.data.items)) {
      // Axios 등을 통해 response.data 안에 { items: [...] } 가 있는 경우
      meetings.value = response.data.items;
    } else if (Array.isArray(response)) {
      // 백엔드가 바로 배열을 반환하는 기존 경우 대응
      meetings.value = response;
    } else if (response && Array.isArray(response.data)) {
      // response.data 자체가 배열인 기존 경우 대응
      meetings.value = response.data;
    } else {
      meetings.value = [];
    }
  } catch (error) {
    errorMsg.value = "모임 목록을 불러오지 못했습니다. 백엔드 서버 상태를 확인해주세요.";
    console.error(error);
  } finally {
    isLoading.value = false;
  }
});

const filteredMeetings = computed(() => {
  const targetMeetings = Array.isArray(meetings.value) ? meetings.value : [];

  const rawKeyword = keyword.value.trim().toLowerCase();
  const tokens = rawKeyword.split(/\s+/).filter(Boolean);

  return targetMeetings.filter((m) => {
    const title = (m.title || "").toLowerCase();
    const locationName = (m.location_name || "").toLowerCase();
    const address = (m.address || "").toLowerCase();
    const category = (m.category || "").toLowerCase();
    const content = (m.content || "").toLowerCase();

    // 1. 키워드 필터
    const matchKeyword =
      tokens.length === 0 ||
      tokens.every(
        (token) =>
          title.includes(token) ||
          locationName.includes(token) ||
          address.includes(token) ||
          category.includes(token) ||
          content.includes(token),
      );

    // 2. 카테고리 필터
    const matchCategory =
      selectedCategory.value === "전체" || m.category === selectedCategory.value;

    // 3. 모집 중 필터 (유연성 강화)
    // 백엔드 status가 대소문자 구분 없이 'OPEN' 또는 'open'인지 체크하거나,
    // 만약 백엔드에서 is_active 필드를 불리언(true/false)으로 내려주고 있다면 그것도 함께 호환시킵니다.
    const isMeetingOpen = String(m.status).toUpperCase() === "OPEN" || m.is_active === true;

    const matchOpen = !onlyOpen.value || isMeetingOpen;

    return matchKeyword && matchCategory && matchOpen;
  });
});
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-ink">모임 찾기</h1>

    <div class="mb-6 space-y-4 rounded-xl border border-line bg-white p-5">
      <input
        v-model="keyword"
        type="text"
        placeholder="키워드로 검색 (예: 모각코, 알고리즘, 프로젝트)"
        class="field-input w-full p-3 border border-line rounded-lg focus:outline-none focus:border-brand"
      />
      <CategoryFilter :categories="categories" v-model="selectedCategory" />
      <label class="flex w-fit cursor-pointer items-center gap-2 text-sm text-ink/80">
        <input v-model="onlyOpen" type="checkbox" class="h-4 w-4 accent-brand" />
        모집 중만 보기
      </label>
    </div>

    <div v-if="isLoading" class="py-16 text-center">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-brand mx-auto"></div>
      <p class="mt-4 text-ink/60">모임 목록을 가져오는 중입니다...</p>
    </div>

    <div v-else-if="errorMsg" class="py-16 text-center text-red-500 font-semibold">
      {{ errorMsg }}
    </div>

    <div v-else-if="filteredMeetings.length" class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <MeetingCard v-for="m in filteredMeetings" :key="m.id" :meeting="m" />
    </div>

    <div v-else class="py-16 text-center text-ink/50">
      <p>조건에 맞는 모임이 없어요.</p>
    </div>
  </div>
</template>
