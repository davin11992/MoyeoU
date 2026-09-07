<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import PlaceCard from "@/components/PlaceCard.vue";
import CategoryFilter from "@/components/CategoryFilter.vue";

const router = useRouter();
const places = ref([]);
const selectedCategory = ref("전체");

// 💡 수정된 요구사항에 맞춘 UI용 카테고리 리스트
const categories = ["전체", "관광", "문화생활", "운동·산책", "맛집", "쇼핑", "여행"];

// 배포 대비 환경변수 적용
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

onMounted(async () => {
  try {
    // 명시적으로 넉넉히 limit 파라미터를 넘겨주거나 기본 호출합니다.
    const response = await axios.get(`${API_BASE_URL}/api/locations`, {
      params: { limit: 1000 },
    });
    places.value = response.data;
    console.log(`불러온 데이터 개수: ${places.value.length}개`); // 브라우저 콘솔(F12)에서 확인용
  } catch (error) {
    console.error("공공데이터 로드 실패:", error);
  }
});

// 💡 공공데이터(content_type) -> 수정된 프론트 카테고리 매핑 로직
const getMappedCategory = (contentType) => {
  if (contentType === "관광지") return "관광";
  if (contentType === "문화시설" || contentType === "축제공연행사") return "문화생활";
  if (contentType === "레포츠") return "운동·산책";
  if (contentType === "음식점") return "맛집";
  if (contentType === "쇼핑") return "쇼핑";
  if (contentType === "숙박" || contentType === "여행코스") return "여행";
  return "관광"; // 매칭 예외 시 기본값
};

// 필터링 동작 로직
const filteredPlaces = computed(() => {
  if (selectedCategory.value === "전체") return places.value;

  return places.value.filter((p) => {
    const mapped = getMappedCategory(p.content_type);
    return mapped === selectedCategory.value;
  });
});
</script>

<template>
  <div class="mx-auto max-w-6xl px-6 py-10">
    <h1 class="mb-2 text-3xl font-bold text-ink">캠퍼스 주변</h1>
    <p class="mb-6 text-ink/70">
      SSAFY 대전 캠퍼스 근처 스터디·맛집·운동 스팟을 둘러보고 함께 갈 동료를 모집해보세요.
    </p>

    <div class="mb-6">
      <CategoryFilter :categories="categories" v-model="selectedCategory" />
    </div>

    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="p in filteredPlaces"
        :key="p.id"
        class="group relative flex flex-col justify-between"
      >
        <PlaceCard :place="p" />
      </div>
    </div>
  </div>
</template>
