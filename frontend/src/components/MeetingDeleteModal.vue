<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { deleteMeeting } from "@/services/api";
import BaseModal from "@/components/BaseModal.vue";

const props = defineProps({
  open: { type: Boolean, required: true },
  meetingId: { type: Number, required: true },
});

const emit = defineEmits(["close"]);
const router = useRouter();

const password = ref("");
const isSubmitting = ref(false);

function handleClose() {
  password.value = "";
  emit("close");
}

// 모임 삭제 처리 (DELETE)
async function handleDelete() {
  if (!password.value) {
    alert("모임 삭제를 위해 비밀번호를 입력해 주세요.");
    return;
  }

  isSubmitting.value = true;
  try {
    // api.js에 정의된 deleteMeeting 호출
    await deleteMeeting(props.meetingId, { password: password.value });

    alert("모임이 성공적으로 삭제되었습니다. 다음에 더 멋진 모임으로 만나요! 👋");

    // 모달 닫고 홈 화면으로 이동
    emit("close");
    router.push("/");
  } catch (error) {
    console.error("모임 삭제 실패:", error);
    alert(error.response?.data?.detail || "비밀번호가 일치하지 않아 모임을 삭제할 수 없습니다.");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <BaseModal :open="open" title="모임 삭제하기" @close="handleClose">
    <div class="space-y-4 py-2 text-left">
      <div class="rounded-xl bg-red-50 p-4 border border-red-100 text-center">
        <span class="text-3xl block mb-2">😢</span>
        <p class="text-sm font-bold text-red-800">정말로 이 모임을 떠나보내실 건가요?</p>
        <p class="text-xs text-red-600/80 mt-1">
          모임을 삭제하시면 등록된 댓글과 참여자 목록이 모두 사라지며, 복구할 수 없습니다.
        </p>
      </div>

      <div class="space-y-1.5">
        <label class="block text-xs font-bold text-ink/70">모임 생성 시 설정한 패스워드</label>
        <input
          v-model="password"
          type="password"
          required
          class="w-full p-2 border rounded-lg text-sm bg-white"
          placeholder="비밀번호를 입력해야 삭제가 처리됩니다."
        />
      </div>

      <div class="flex gap-2 pt-2">
        <button
          type="button"
          @click="handleClose"
          class="flex-1 py-2.5 border rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          아니오, 유지할래요
        </button>
        <button
          type="button"
          @click="handleDelete"
          :disabled="isSubmitting"
          class="flex-1 py-2.5 bg-red-500 text-white font-bold rounded-lg text-sm hover:bg-red-600 transition-colors flex justify-center items-center gap-1"
        >
          <span
            v-if="isSubmitting"
            class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"
          ></span>
          네, 삭제하겠습니다
        </button>
      </div>
    </div>
  </BaseModal>
</template>
