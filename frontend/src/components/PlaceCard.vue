<script setup>
import { useRouter } from "vue-router";

const props = defineProps({
  place: {
    type: Object,
    required: true,
  },
});

const router = useRouter();

// 💡 공공데이터 필드를 수정된 프론트 UI 카테고리 명칭으로 변경해주는 함수
const getMappedCategory = (contentType) => {
  if (contentType === "관광지") return "관광";
  if (contentType === "문화시설" || contentType === "축제공연행사") return "문화생활";
  if (contentType === "레포츠") return "운동·산책";
  if (contentType === "음식점") return "맛집";
  if (contentType === "쇼핑") return "쇼핑";
  if (contentType === "숙박" || contentType === "여행코스") return "여행";
  return "관광";
};

function createMeetingHere() {
  router.push({
    path: "/meetings/new",
    query: {
      loc_id: props.place.id,
      loc_name: props.place.title,
    },
  });
}

function showDetail() {
  const displayCategory = getMappedCategory(props.place.content_type);
  alert(`${props.place.title}\n종류: ${displayCategory}\n주소: ${props.place.address}`);
}
</script>

<template>
  <div class="card flex flex-col">
    <span
      class="mb-2 w-fit rounded-full bg-brand-light px-2.5 py-1 text-xs font-medium text-brand-hover"
    >
      {{ getMappedCategory(place.content_type) }}
    </span>

    <h3 class="mb-1 text-lg font-semibold text-ink">{{ place.title }}</h3>

    <p class="mb-4 flex-1 text-sm text-ink/70">{{ place.address }}</p>

    <div class="flex gap-2">
      <button type="button" class="btn-outline flex-1 text-sm" @click="showDetail">
        상세 보기
      </button>
      <button type="button" class="btn-primary flex-1 text-sm" @click="createMeetingHere">
        여기서 모임 만들기
      </button>
    </div>
  </div>
</template>
