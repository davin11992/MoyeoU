<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import {
  getMeetingById,
  joinMeeting,
  leaveMeeting,
  createComment,
  deleteComment,
} from "@/services/api";
import BaseModal from "@/components/BaseModal.vue";
import MeetingEditModal from "@/components/MeetingEditModal.vue";
import MeetingDeleteModal from "@/components/MeetingDeleteModal.vue";

const route = useRoute();
const router = useRouter();
const meetingId = Number(route.params.id);

const meeting = ref(null);
const loading = ref(true);
const errorMsg = ref("");

// 모달 상태 관리
const showJoinModal = ref(false);
const showLeaveModal = ref(false);
const showEditModal = ref(false); // 수정 모달 노출 상태
const showDeleteModal = ref(false);

const joined = ref(false);
const left = ref(false);
const isSubmitting = ref(false);

// 입력 폼 상태 관리
const joinForm = ref({ nickname: "", password: "" });
const leaveForm = ref({ nickname: "", password: "" });

// 댓글 및 대댓글 폼 상태 관리
const commentForm = ref({ nickname: "", password: "", content: "" });
const activeReplyId = ref(null);
const replyForm = ref({ nickname: "", password: "", content: "" });

// 초기 데이터 로드
onMounted(async () => {
  await fetchMeetingData();
});

// 데이터 새로고침
async function fetchMeetingData() {
  loading.value = true;
  errorMsg.value = "";
  try {
    const data = await getMeetingById(meetingId);
    if (data) {
      meeting.value = data;
    } else {
      errorMsg.value = "존재하지 않거나 삭제된 모임입니다.";
    }
  } catch (error) {
    console.error("모임 상세 조회 실패:", error);
    errorMsg.value = "데이터를 불러오는 중 문제가 발생했습니다.";
  } finally {
    loading.value = false;
  }
}

// 수정 완료 콜백 핸들러
async function onEditSuccess() {
  showEditModal.value = false;
  await fetchMeetingData(); // 최신 정보로 리프레시
}

// 모임 참여 신청 API 연동
async function join() {
  const nicknameVal = joinForm.value.nickname.trim();
  const passwordVal = joinForm.value.password;

  if (!nicknameVal || !passwordVal) {
    alert("닉네임과 참여 비밀번호를 모두 입력해 주세요!");
    return;
  }

  if (passwordVal.length < 4) {
    alert("참여 비밀번호는 최소 4자리 이상 입력해 주세요.");
    return;
  }

  isSubmitting.value = true;
  try {
    await joinMeeting(meetingId, {
      nickname: nicknameVal,
      password: passwordVal,
    });

    if (meeting.value) {
      // 참여 인원 1 증가
      meeting.value.current_participants += 1;

      // 인원이 꽉 찼다면 실시간으로 모집 완료 상태로 전환
      if (
        meeting.value.current_participants >= meeting.value.max_participants
      ) {
        meeting.value.status = "CLOSED";
      }
    }

    joined.value = true;
  } catch (error) {
    console.error("참여 신청 실패:", error);
    const serverErrorMsg = error.response?.data?.detail;

    if (Array.isArray(serverErrorMsg)) {
      alert(
        `입력 형식 오류: ${serverErrorMsg[0]?.msg || "형식을 확인해 주세요."}`,
      );
    } else {
      alert(
        serverErrorMsg ||
          "참여 신청에 실패했습니다. 정원이 초과되었거나 중복 신청일 수 있습니다.",
      );
    }
  } finally {
    isSubmitting.value = false;
  }
}

// 모임 참여 취소 API 연동
async function leave() {
  if (!leaveForm.value.nickname.trim() || !leaveForm.value.password) {
    alert("신청하셨던 닉네임과 비밀번호를 입력해 주세요!");
    return;
  }

  isSubmitting.value = true;
  try {
    await leaveMeeting(meetingId, {
      nickname: leaveForm.value.nickname,
      password: leaveForm.value.password,
    });

    if (meeting.value && meeting.value.current_participants > 0) {
      meeting.value.current_participants -= 1;
    }

    left.value = true;
  } catch (error) {
    console.error("참여 취소 실패:", error);
    alert(
      error.response?.data?.detail ||
        "참여 취소에 실패했습니다. 입력 정보를 다시 한 번 확인해 주세요.",
    );
  } finally {
    isSubmitting.value = false;
  }
}

function closeModal() {
  showJoinModal.value = false;
  showLeaveModal.value = false;
  joined.value = false;
  left.value = false;
  joinForm.value = { nickname: "", password: "" };
  leaveForm.value = { nickname: "", password: "" };
}

// 부모가 없는 최상위 댓글 필터링
const rootComments = computed(() => {
  if (!meeting.value?.comments) return [];
  return meeting.value.comments.filter((c) => !c.parent_id);
});

// 특정 부모 ID를 가진 자식 대댓글 필터링
const getReplies = (parentId) => {
  if (!meeting.value?.comments) return [];
  return meeting.value.comments.filter((c) => c.parent_id === parentId);
};

// 대댓글 입력 폼 토글
const toggleReplyForm = (commentId) => {
  if (activeReplyId.value === commentId) {
    activeReplyId.value = null;
  } else {
    activeReplyId.value = commentId;
    replyForm.value = { nickname: "", password: "", content: "" };
  }
};

// 최상위 댓글 등록 (서버 싱크 업데이트 적용)
async function submitComment() {
  if (
    !commentForm.value.nickname.trim() ||
    !commentForm.value.password ||
    !commentForm.value.content.trim()
  ) {
    alert("댓글 정보를 모두 채워주세요!");
    return;
  }
  try {
    await createComment(meetingId, {
      nickname: commentForm.value.nickname,
      password: commentForm.value.password,
      content: commentForm.value.content,
      parent_id: null,
    });

    // 직접 클라이언트 배열에 push하는 대신 데이터베이스 최신 상태 동기화
    await fetchMeetingData();

    commentForm.value = { nickname: "", password: "", content: "" };
  } catch (error) {
    console.error("댓글 등록 처리 중 에러 발생:", error);
    alert("댓글 등록에 실패했습니다.");
  }
}

// 대댓글 등록 (서버 싱크 업데이트 적용)
async function submitReply(parentId) {
  if (
    !replyForm.value.nickname.trim() ||
    !replyForm.value.password ||
    !replyForm.value.content.trim()
  ) {
    alert("답글 내용을 모두 채워주세요!");
    return;
  }
  try {
    await createComment(meetingId, {
      nickname: replyForm.value.nickname,
      password: replyForm.value.password,
      content: replyForm.value.content,
      parent_id: parentId,
    });

    // 직접 클라이언트 배열에 push하는 대신 데이터베이스 최신 상태 동기화
    await fetchMeetingData();

    activeReplyId.value = null;
  } catch (error) {
    console.error("대댓글 등록 처리 중 에러 발생:", error);
    alert("답글 등록에 실패했습니다.");
  }
}

// 댓글 삭제
async function triggerDeleteComment(commentId) {
  const password = prompt("댓글 삭제 비밀번호를 입력해 주세요:");
  if (!password) return;

  try {
    await deleteComment(meetingId, commentId, { password });

    if (!meeting.value || !meeting.value.comments) {
      throw new Error("모임 또는 댓글 데이터가 존재하지 않습니다.");
    }

    meeting.value.comments = meeting.value.comments.filter(
      (c) => c.id !== commentId && c.parent_id !== commentId,
    );

    alert("댓글이 정상적으로 삭제되었습니다.");
  } catch (error) {
    console.error("댓글 삭제 처리 중 에러 발생:", error);

    const serverErrorMsg = error.response?.data?.detail;
    alert(serverErrorMsg || "비밀번호가 일치하지 않거나 삭제 권한이 없습니다.");
  }
}

// 날짜 포맷팅 헬퍼
const formatDate = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`;
};
</script>

<template>
  <div class="mx-auto max-w-3xl px-6 py-10">
    <div class="mb-4 flex justify-between items-center">
      <RouterLink to="/" class="text-sm text-brand hover:text-brand-hover">
        &larr; 모임 목록으로
      </RouterLink>

      <div v-if="meeting" class="flex gap-3 text-xs font-semibold">
        <button
          @click="showEditModal = true"
          class="text-ink/60 hover:text-brand hover:underline transition-colors"
        >
          수정
        </button>
        <button
          @click="showDeleteModal = true"
          class="text-red-500 hover:text-red-600 hover:underline transition-colors"
        >
          삭제
        </button>
      </div>
    </div>

    <p v-if="loading" class="py-16 text-center text-ink/50">불러오는 중...</p>
    <p
      v-else-if="errorMsg"
      class="py-16 text-center text-red-500 font-semibold"
    >
      {{ errorMsg }}
    </p>
    <p v-else-if="!meeting" class="py-16 text-center text-ink/50">
      모임을 찾을 수 없어요.
    </p>

    <div v-else class="mt-4 space-y-8">
      <div class="rounded-xl border border-line bg-white p-6 shadow-sm">
        <div class="mb-4 flex items-center gap-2">
          <span
            class="rounded-full bg-brand-light px-2.5 py-1 text-xs font-medium text-brand-hover"
          >
            {{ meeting.category }}
          </span>

          <span
            class="rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
            :class="{
              'bg-brand text-white': meeting.status === 'OPEN',
              'bg-gray-200 text-gray-700': meeting.status === 'CLOSED',
              'bg-line text-ink/60':
                meeting.status !== 'OPEN' && meeting.status !== 'CLOSED',
            }"
          >
            <span v-if="meeting.status === 'OPEN'">모집 중</span>
            <span v-else-if="meeting.status === 'CLOSED'">모집 완료</span>
            <span v-else>마감</span>
          </span>
        </div>

        <h1 class="mb-4 text-2xl font-bold text-ink">{{ meeting.title }}</h1>

        <dl class="mb-6 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt class="text-ink/50">일시</dt>
            <dd class="font-medium text-ink">
              {{ meeting.meeting_date }}
              {{
                meeting.meeting_time ? meeting.meeting_time.substring(0, 5) : ""
              }}
            </dd>
          </div>
          <div>
            <dt class="text-ink/50">장소</dt>
            <dd class="font-medium text-ink">{{ meeting.location_name }}</dd>
          </div>
          <div>
            <dt class="text-ink/50">참여 인원</dt>
            <dd class="font-medium text-ink">
              {{ meeting.current_participants }} /
              {{ meeting.max_participants }}명
            </dd>
          </div>
        </dl>

        <div class="mb-6">
          <h2 class="mb-2 font-bold text-ink text-base">상세 내용</h2>
          <p class="leading-relaxed text-ink/80 whitespace-pre-line">
            {{ meeting.content }}
          </p>
        </div>

        <p
          class="mb-6 rounded-lg bg-brand-light px-4 py-3 text-sm text-brand-hover"
        >
          개인정보 공유를 피하고, 공개된 장소에서 만나는 것을 권장합니다.
        </p>

        <div class="flex gap-2">
          <button
            type="button"
            class="btn-primary flex-1 bg-brand text-white font-bold py-3 rounded-lg hover:bg-brand/90 transition-opacity"
            :disabled="meeting.status !== 'OPEN'"
            @click="showJoinModal = true"
          >
            <span v-if="meeting.status === 'OPEN'">참여하기</span>
            <span v-else-if="meeting.status === 'CLOSED'"
              >모집 완료되었습니다</span
            >
            <span v-else>모집이 마감되었습니다</span>
          </button>

          <button
            type="button"
            class="btn-outline border px-5 rounded-lg text-ink/70 hover:bg-gray-50 font-semibold"
            @click="showLeaveModal = true"
          >
            참여 취소
          </button>
        </div>
      </div>

      <div class="space-y-6">
        <h3 class="text-lg font-bold text-ink">
          댓글 ({{ meeting.comments?.length || 0 }})
        </h3>

        <div v-if="rootComments.length > 0" class="space-y-4">
          <div
            v-for="comment in rootComments"
            :key="comment.id"
            class="space-y-2"
          >
            <div
              class="rounded-xl border border-line bg-white p-5 shadow-sm space-y-3"
            >
              <div class="flex justify-between items-center text-xs">
                <span class="font-bold text-ink">{{ comment.nickname }}</span>
                <span class="text-ink/50">{{
                  formatDate(comment.created_at)
                }}</span>
              </div>

              <p class="text-sm text-ink/90 whitespace-pre-line">
                {{ comment.content }}
              </p>

              <div class="flex gap-3 text-xs text-brand font-medium">
                <button
                  @click="toggleReplyForm(comment.id)"
                  class="hover:underline"
                >
                  답글 달기
                </button>
                <button
                  @click="triggerDeleteComment(comment.id)"
                  class="text-red-500 hover:underline"
                >
                  삭제
                </button>
              </div>

              <div
                v-if="activeReplyId === comment.id"
                class="mt-4 p-4 rounded-lg bg-gray-50 border border-line space-y-3"
              >
                <div class="flex gap-2">
                  <input
                    v-model="replyForm.nickname"
                    type="text"
                    placeholder="닉네임"
                    class="w-1/3 p-2 border rounded-lg text-xs"
                  />
                  <input
                    v-model="replyForm.password"
                    type="password"
                    placeholder="비밀번호"
                    class="w-2/3 p-2 border rounded-lg text-xs"
                  />
                </div>
                <textarea
                  v-model="replyForm.content"
                  placeholder="답글 내용을 입력하세요."
                  class="w-full p-2 border rounded-lg text-xs h-16"
                ></textarea>
                <div class="flex justify-end gap-2">
                  <button
                    @click="activeReplyId = null"
                    class="px-3 py-1 text-xs border bg-white rounded-md"
                  >
                    취소
                  </button>
                  <button
                    @click="submitReply(comment.id)"
                    class="px-3 py-1 text-xs bg-brand text-white rounded-md font-semibold"
                  >
                    등록
                  </button>
                </div>
              </div>
            </div>

            <div
              v-if="getReplies(comment.id).length > 0"
              class="pl-10 space-y-2"
            >
              <div
                v-for="reply in getReplies(comment.id)"
                :key="reply.id"
                class="rounded-lg border border-line bg-slate-50 p-4 shadow-xs flex items-start gap-3"
              >
                <span class="text-brand text-sm font-bold select-none pt-0.5"
                  >↳</span
                >

                <div class="flex-1 space-y-2">
                  <div class="flex justify-between items-center text-xs">
                    <span class="font-bold text-ink/80">{{
                      reply.nickname
                    }}</span>
                    <span class="text-ink/40">{{
                      formatDate(reply.created_at)
                    }}</span>
                  </div>

                  <p class="text-xs text-ink/80 whitespace-pre-line">
                    {{ reply.content }}
                  </p>

                  <div class="text-right">
                    <button
                      @click="triggerDeleteComment(reply.id)"
                      class="text-[10px] text-red-400 hover:text-red-500 hover:underline font-medium"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="text-center py-6 text-ink/40 text-xs">
          등록된 댓글이 아직 없습니다.
        </p>

        <div
          class="rounded-xl border border-line bg-white p-5 shadow-sm space-y-3"
        >
          <h4 class="font-bold text-ink text-xs">댓글 작성하기</h4>
          <div class="flex gap-3">
            <input
              v-model="commentForm.nickname"
              type="text"
              placeholder="닉네임"
              class="w-1/3 p-2 border rounded-lg text-xs"
            />
            <input
              v-model="commentForm.password"
              type="password"
              placeholder="비밀번호"
              class="w-2/3 p-2 border rounded-lg text-xs"
            />
          </div>
          <textarea
            v-model="commentForm.content"
            placeholder="질문이나 따뜻한 대화를 남겨주세요."
            class="w-full p-2 border rounded-lg text-xs h-16"
          ></textarea>
          <div class="text-right">
            <button
              @click="submitComment"
              class="px-4 py-2 bg-brand text-white font-bold rounded-lg text-xs hover:bg-brand/90"
            >
              댓글 등록
            </button>
          </div>
        </div>
      </div>
    </div>

    <BaseModal :open="showJoinModal" title="모임 참여하기" @close="closeModal">
      <div v-if="!joined" class="space-y-4">
        <div>
          <label class="field-label text-sm font-semibold block mb-1"
            >닉네임</label
          >
          <input
            v-model="joinForm.nickname"
            type="text"
            class="field-input w-full p-2 border rounded-lg"
            placeholder="사용할 닉네임"
          />
        </div>
        <div>
          <label class="field-label text-sm font-semibold block mb-1"
            >참여 비밀번호</label
          >
          <input
            v-model="joinForm.password"
            type="password"
            class="field-input w-full p-2 border rounded-lg"
            placeholder="비밀번호 설정"
          />
        </div>
        <button
          type="button"
          class="btn-primary w-full bg-brand text-white font-bold py-2.5 rounded-lg hover:bg-brand/90 flex justify-center items-center gap-2"
          @click="join"
          :disabled="isSubmitting"
        >
          <span
            v-if="isSubmitting"
            class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
          ></span>
          {{ isSubmitting ? "참여 신청 중..." : "참여 신청" }}
        </button>
      </div>
      <div v-else class="py-4 text-center">
        <p class="mb-4 text-ink font-medium">
          참여 신청이 성공적으로 완료되었어요! <br />약속 장소에서 안전하고
          유익한 시간 보내세요.
        </p>
        <button
          type="button"
          class="btn-outline border px-4 py-2 rounded-lg"
          @click="closeModal"
        >
          닫기
        </button>
      </div>
    </BaseModal>

    <BaseModal
      :open="showLeaveModal"
      title="모임 참여 취소"
      @close="closeModal"
    >
      <div v-if="!left" class="space-y-4">
        <div>
          <label class="field-label text-sm font-semibold block mb-1"
            >참여시 작성했던 닉네임</label
          >
          <input
            v-model="leaveForm.nickname"
            type="text"
            class="field-input w-full p-2 border rounded-lg"
            placeholder="닉네임 입력"
          />
        </div>
        <div>
          <label class="field-label text-sm font-semibold block mb-1"
            >참여 비밀번호</label
          >
          <input
            v-model="leaveForm.password"
            type="password"
            class="field-input w-full p-2 border rounded-lg"
            placeholder="비밀번호 입력"
          />
        </div>
        <button
          type="button"
          class="btn-primary w-full bg-red-500 text-white font-bold py-2.5 rounded-lg hover:bg-red-600 flex justify-center items-center gap-2"
          @click="leave"
          :disabled="isSubmitting"
        >
          <span
            v-if="isSubmitting"
            class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
          ></span>
          {{ isSubmitting ? "취소 처리 중..." : "참여 취소하기" }}
        </button>
      </div>
      <div v-else class="py-4 text-center">
        <p class="mb-4 text-ink font-medium">
          모임 참여 취소가 완료되었습니다. <br />다음에 더 즐거운 모임으로
          만나요!
        </p>
        <button
          type="button"
          class="btn-outline border px-4 py-2 rounded-lg"
          @click="closeModal"
        >
          닫기
        </button>
      </div>
    </BaseModal>

    <MeetingEditModal
      :open="showEditModal"
      :meeting="meeting"
      @close="showEditModal = false"
      @success="onEditSuccess"
    />

    <MeetingDeleteModal
      :open="showDeleteModal"
      :meetingId="meetingId"
      @close="showDeleteModal = false"
    />
  </div>
</template>