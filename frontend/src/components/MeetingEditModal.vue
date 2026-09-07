<script setup>
import { ref, watch } from "vue";
import { updateMeeting } from "@/services/api";
import BaseModal from "@/components/BaseModal.vue";

// 부모 컴포넌트로부터 전달받을 Props 정의
const props = defineProps({
  open: { type: Boolean, required: true },
  meeting: { type: Object, default: null },
});

// 부모 컴포넌트에 이벤트를 전달할 Emits 정의
const emit = defineEmits(["close", "success"]);

const isSubmitting = ref(false);

const editForm = ref({
  title: "",
  category: "맛집",
  meeting_date: "",
  meeting_time: "",
  location_name: "",
  max_participants: 4,
  content: "",
  password: "",
});

const categories = ["관광", "문화생활", "운동·산책", "맛집", "쇼핑", "여행"];

// 모달이 열리거나 모임 데이터가 변경될 때 폼 값을 기존 상세 데이터로 동기화
watch(
  () => props.open,
  (newVal) => {
    if (newVal && props.meeting) {
      editForm.value = {
        title: props.meeting.title,
        category: props.meeting.category,
        meeting_date: props.meeting.meeting_date,
        meeting_time: props.meeting.meeting_time ? props.meeting.meeting_time.substring(0, 5) : "",
        location_name: props.meeting.location_name,
        max_participants: props.meeting.max_participants,
        content: props.meeting.content,
        password: "", // 비밀번호는 보안상 매번 새로 입력하도록 비워둠
      };
    }
  },
);

function handleClose() {
  emit("close");
}

// 모임 정보 수정 처리 (PUT)
async function handleUpdate() {
  if (!editForm.value.password) {
    alert("모임 등록 시 설정했던 비밀번호를 입력해 주세요!");
    return;
  }

  isSubmitting.value = true;
  try {
    await updateMeeting(props.meeting.id, {
      title: editForm.value.title,
      category: editForm.value.category,
      meeting_date: editForm.value.meeting_date,
      meeting_time: editForm.value.meeting_time ? `${editForm.value.meeting_time}:00` : null,
      location_name: editForm.value.location_name,
      max_participants: Number(editForm.value.max_participants),
      content: editForm.value.content,
      password: editForm.value.password,
    });

    alert("모임 정보가 성공적으로 수정되었습니다.");
    emit("success"); // 수정 성공을 부모 컴포넌트에 알림
  } catch (error) {
    console.error("모임 수정 실패:", error);
    alert(error.response?.data?.detail || "수정에 실패했습니다. 비밀번호를 확인해 주세요.");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <BaseModal :open="open" title="모임 글 수정하기" @close="handleClose">
    <form @submit.prevent="handleUpdate" class="space-y-4 text-left py-2">
      <div>
        <label class="block text-xs font-semibold mb-1 text-ink/70">카테고리</label>
        <select v-model="editForm.category" class="w-full p-2 border rounded-lg text-sm bg-white">
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold mb-1 text-ink/70">모임 제목</label>
        <input
          v-model="editForm.title"
          type="text"
          required
          class="w-full p-2 border rounded-lg text-sm"
          placeholder="수정할 모임 제목"
        />
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="block text-xs font-semibold mb-1 text-ink/70">모임 날짜</label>
          <input
            v-model="editForm.meeting_date"
            type="date"
            required
            class="w-full p-2 border rounded-lg text-sm"
          />
        </div>
        <div>
          <label class="block text-xs font-semibold mb-1 text-ink/70">모임 시간</label>
          <input
            v-model="editForm.meeting_time"
            type="time"
            required
            class="w-full p-2 border rounded-lg text-sm"
          />
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold mb-1 text-ink/70">만날 장소</label>
        <input
          v-model="editForm.location_name"
          type="text"
          required
          class="w-full p-2 border rounded-lg text-sm"
        />
      </div>

      <div>
        <label class="block text-xs font-semibold mb-1 text-ink/70">모집 정원 (명)</label>
        <input
          v-model="editForm.max_participants"
          type="number"
          min="2"
          max="100"
          required
          class="w-full p-2 border rounded-lg text-sm"
        />
      </div>

      <div>
        <label class="block text-xs font-semibold mb-1 text-ink/70">상세 안내 내용</label>
        <textarea
          v-model="editForm.content"
          required
          rows="4"
          class="w-full p-2 border rounded-lg text-sm resize-none"
        ></textarea>
      </div>

      <div class="rounded-lg bg-brand-light p-3 border border-line">
        <label class="block text-xs font-bold text-brand-hover mb-1">모임 생성 시 패스워드</label>
        <input
          v-model="editForm.password"
          type="password"
          required
          class="w-full p-2 border rounded-lg text-sm bg-white"
          placeholder="비밀번호를 입력해야 수정이 반영됩니다."
        />
      </div>

      <div class="flex gap-2 pt-2">
        <button type="button" @click="handleClose" class="flex-1 py-2 border rounded-lg text-sm">
          취소
        </button>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="flex-1 py-2 bg-brand text-white font-bold rounded-lg text-sm hover:bg-brand/90 flex justify-center items-center gap-1"
        >
          <span
            v-if="isSubmitting"
            class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"
          ></span>
          수정 완료
        </button>
      </div>
    </form>
  </BaseModal>
</template>
