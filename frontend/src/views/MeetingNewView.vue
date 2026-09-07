<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { createMeeting } from "@/services/api";
import lightningIcon from "@/assets/lightning.svg";

const route = useRoute();
const router = useRouter();

const categories = ["관광", "문화생활", "운동·산책", "맛집", "쇼핑", "여행"];

const form = ref({
  title: "",
  category: categories[0],
  date: "",
  time: "",
  location: "", // 만날 장소 명칭 (자유 입력)
  max: 4,
  description: "",
  password: "",
  location_id: null,
  map_y: 36.3504, // 위도
  map_x: 127.3845, // 경도
});

// 지도용 독립 검색 키워드 바인딩 변수
const mapSearchKeyword = ref("");

const submitted = ref(false);
const validationError = ref("");

// 지도 관련 객체
const mapContainer = ref(null);
let map = null;
let selectedMarker = null;
let placeService = null;

onMounted(() => {
  if (route.query.loc_name) {
    form.value.location = String(route.query.loc_name);
    mapSearchKeyword.value = String(route.query.loc_name);
  }
  if (route.query.loc_id) {
    form.value.location_id = String(route.query.loc_id);
  }

  if (window.kakao && window.kakao.maps) {
    window.kakao.maps.load(initMap);
  }
});

const initMap = () => {
  const container = mapContainer.value;
  if (!container) return;

  const initialPosition = new window.kakao.maps.LatLng(form.value.map_y, form.value.map_x);

  const options = {
    center: initialPosition,
    level: 3,
  };

  // 1. 지도 생성
  map = new window.kakao.maps.Map(container, options);

  // 2. 검색 서비스 선언을 최상단으로 올려서 안전성 선확보 ✅
  if (window.kakao.maps.services && window.kakao.maps.services.Places) {
    placeService = new window.kakao.maps.services.Places();
  } else {
    // 0.5초 대기 백업 가드
    setTimeout(() => {
      if (window.kakao.maps.services && window.kakao.maps.services.Places) {
        placeService = new window.kakao.maps.services.Places();
        if (mapSearchKeyword.value) searchLocation();
      }
    }, 500);
  }

  // 마커 아이콘 생성 및 지도 표시
  const imageSrc = lightningIcon;
  const imageSize = new window.kakao.maps.Size(40, 40);
  const imageOption = { offset: new window.kakao.maps.Point(20, 40) };
  const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize, imageOption);

  selectedMarker = new window.kakao.maps.Marker({
    position: initialPosition,
    image: markerImage,
    map: map,
  });

  // 지도 클릭 이벤트 리스너
  window.kakao.maps.event.addListener(map, "click", (mouseEvent) => {
    const latlng = mouseEvent.latLng;
    selectedMarker.setPosition(latlng);
    form.value.map_y = Number(latlng.getLat().toFixed(6));
    form.value.map_x = Number(latlng.getLng().toFixed(6));
  });

  // 3. 인스턴스가 확실히 할당되었을 때만 자동 쿼리 검색 호출 ✅
  if (mapSearchKeyword.value && placeService) {
    searchLocation();
  }
};

// 독립 지도 검색 함수
const searchLocation = () => {
  if (!mapSearchKeyword.value.trim()) {
    alert("검색할 지역, 지하철역, 장소 등을 입력해 주세요!");
    return;
  }

  if (!placeService) {
    console.error("카카오 맵 API 서비스가 완벽하게 준비되지 않았습니다.");
    return;
  }

  placeService.keywordSearch(mapSearchKeyword.value, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      const targetPlace = data[0];
      const newPos = new window.kakao.maps.LatLng(targetPlace.y, targetPlace.x);

      map.setCenter(newPos);
      selectedMarker.setPosition(newPos);

      form.value.map_y = Number(Number(targetPlace.y).toFixed(6));
      form.value.map_x = Number(Number(targetPlace.x).toFixed(6));
    } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
      alert("검색 결과가 없습니다. 올바른 장소명을 입력하시거나 수동으로 찍어주세요!");
    } else {
      alert("검색 서버와 통신 중 장애가 발생했습니다.");
    }
  });
};

async function submit() {
  validationError.value = "";

  if (
    !form.value.title.trim() ||
    !form.value.date ||
    !form.value.time ||
    !form.value.location.trim() ||
    !form.value.password
  ) {
    validationError.value = "필수 입력 항목(*)을 모두 채워주세요!";
    return;
  }

  if (form.value.password.length < 4) {
    validationError.value = "비밀번호는 최소 4자리 이상 설정해 주세요.";
    return;
  }

  try {
    let formattedDate = form.value.date;
    if (formattedDate === "오늘") {
      formattedDate = new Date().toISOString().split("T")[0];
    } else if (formattedDate === "내일") {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      formattedDate = tomorrow.toISOString().split("T")[0];
    } else {
      const dateReg = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateReg.test(formattedDate)) {
        validationError.value =
          "날짜 형식(YYYY-MM-DD)을 올바르게 기입해 주시거나 달력에서 선택해 주세요.";
        return;
      }
    }

    let formattedTime = form.value.time;
    if (formattedTime && formattedTime.split(":").length === 2) {
      formattedTime = `${formattedTime}:00`;
    }

    const backendPayload = {
      title: form.value.title,
      category: form.value.category,
      meeting_date: formattedDate,
      meeting_time: formattedTime,
      location_name: form.value.location,
      max_participants: Number(form.value.max),
      content: form.value.description || "",
      password: form.value.password,
      location_id: form.value.location_id || null,
      map_y: form.value.map_y,
      map_x: form.value.map_x,
    };

    await createMeeting(backendPayload);
    submitted.value = true;

    setTimeout(() => router.push("/"), 1200);
  } catch (error) {
    console.error("모임 생성 실패 디버깅 로그:", error);
    validationError.value =
      error.response?.data?.detail?.[0]?.msg ||
      "모임 등록에 실패했습니다. 입력 양식을 다시 확인해 주세요!";
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-ink">모임 만들기</h1>

    <p v-if="submitted" class="mb-6 rounded-lg bg-green-50 px-4 py-3 text-green-700 font-semibold">
      🎉 모임이 성공적으로 등록되었습니다! 목록으로 이동합니다...
    </p>

    <div class="space-y-5 rounded-xl border border-line bg-white p-6 shadow-sm">
      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">제목 *</label>
        <input
          v-model="form.title"
          type="text"
          required
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="예: 주말에 삼겹살 맛집 같이 가실 분!"
        />
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">카테고리</label>
        <select v-model="form.category" class="field-input w-full p-2.5 border rounded-lg bg-white">
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="field-label block text-sm font-semibold mb-1 text-ink">날짜 *</label>
          <input
            v-model="form.date"
            type="date"
            required
            class="field-input w-full p-2.5 border rounded-lg"
          />
        </div>
        <div>
          <label class="field-label block text-sm font-semibold mb-1 text-ink">시간 *</label>
          <input
            v-model="form.time"
            type="time"
            required
            class="field-input w-full p-2.5 border rounded-lg"
          />
        </div>
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink"
          >만날 장소 상세 명칭 *</label
        >
        <input
          v-model="form.location"
          type="text"
          required
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="예: SSAFY 대전캠퍼스 2층 로비 정수기 앞"
        />
        <p v-if="form.location_id" class="mt-2 text-xs font-semibold text-emerald-600">
          추천 장소 정보가 자동으로 안전하게 기입되었습니다. (ID: {{ form.location_id }})
        </p>
      </div>

      <div class="space-y-3">
        <div>
          <label class="field-label block text-sm font-semibold mb-1 text-ink"
            >지도 위치 찾기</label
          >
          <div class="flex gap-2">
            <input
              v-model="mapSearchKeyword"
              type="text"
              class="field-input flex-1 p-2.5 border rounded-lg text-sm bg-gray-50"
              placeholder="예: 대전 유성구 동서대로 98-39 또는 한밭수목원"
              @keyup.enter="searchLocation"
            />
            <button
              type="button"
              class="px-4 bg-brand text-white font-bold rounded-lg hover:bg-brand/90 transition-all text-sm"
              @click="searchLocation"
            >
              위치 검색
            </button>
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="block text-xs font-bold text-brand-hover"
            >📍 위치 정밀 보정 (검색 후 지도 위를 탭하여 핀을 보정하세요)</label
          >
          <div class="w-full h-[250px] rounded-xl border border-line overflow-hidden shadow-inner">
            <div ref="mapContainer" class="w-full h-full"></div>
          </div>
          <div
            class="flex items-center gap-2 bg-gray-50 p-2 rounded-lg border border-line text-[11px] text-ink/60 font-mono"
          >
            <span
              >위도: <strong class="text-brand">{{ form.map_y }}</strong></span
            >
            <span
              >경도: <strong class="text-brand">{{ form.map_x }}</strong></span
            >
          </div>
        </div>
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink"
          >최대 모집 인원 *</label
        >
        <input
          v-model.number="form.max"
          type="number"
          min="2"
          max="100"
          required
          class="field-input w-full p-2.5 border rounded-lg"
        />
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink">상세 내용</label>
        <textarea
          v-model="form.description"
          rows="4"
          class="field-input w-full p-2.5 border rounded-lg resize-none"
          placeholder="모임에 대해 자유롭게 소개해주세요."
        ></textarea>
      </div>

      <div>
        <label class="field-label block text-sm font-semibold mb-1 text-ink"
          >수정·삭제용 비밀번호 *</label
        >
        <input
          v-model="form.password"
          type="password"
          required
          class="field-input w-full p-2.5 border rounded-lg"
          placeholder="최소 4자리 이상의 비밀번호"
        />
      </div>

      <p v-if="validationError" class="text-sm font-semibold text-red-500">{{ validationError }}</p>

      <button
        type="button"
        class="btn-primary w-full bg-brand py-3 text-white font-bold rounded-lg hover:bg-brand/90 transition-all"
        @click="submit"
      >
        모임 등록하기
      </button>
    </div>
  </div>
</template>
