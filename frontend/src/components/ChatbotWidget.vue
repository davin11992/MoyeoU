<script setup>
import { ref, nextTick } from "vue";
import { searchChat } from "@/services/api";
import MeetingCard from "@/components/MeetingCard.vue";
import PlaceCard from "@/components/PlaceCard.vue";

const open = ref(false);
const input = ref("");
const messages = ref([
  {
    role: "bot",
    text: "안녕하세요! SSAFY 동료들과 함께할 모임을 자연스럽게 물어보세요.",
    results: [],
    // 메시지 타입 기본값 세팅
    target: "MEETING",
  },
]);
const listRef = ref(null);

const suggestions = [
  "오늘 알고리즘 모각코 있어?",
  "CS 면접 스터디 찾아줘",
  "점심 같이 먹을 사람 있어?",
];

async function send(text) {
  const query = (text ?? input.value).trim();
  if (!query) return;

  // 프론트가 전송을 감지하는 순간에도 메시지 기본 target 형태 지정
  messages.value.push({ role: "user", text: query, results: [], target: "MEETING" });
  input.value = "";
  await scrollToBottom();

  // 백엔드에서 전송받는 matched_data와 target 구조 분해 할당
  const { reply, matched_data, target } = await searchChat(query);

  // 백엔드에서 수신한 matched_data를 results에 바인딩하고 target 정보를 함께 보관
  messages.value.push({
    role: "bot",
    text: reply,
    results: matched_data,
    target: target,
  });
  await scrollToBottom();
}

async function scrollToBottom() {
  await nextTick();
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight;
}

function onKeydown(e) {
  if (e.isComposing || e.keyCode === 229) return;
  send();
}
</script>

<template>
  <button
    type="button"
    class="fixed bottom-6 right-6 z-50 flex h-[5.5rem] w-[5.5rem] flex-col items-center justify-center rounded-full bg-gradient-to-b from-brand to-brand-hover text-white shadow-[0_4px_0_0_#0573c7,0_12px_20px_0_rgba(0,0,0,0.35)] transition-all duration-150 hover:translate-y-[-2px] hover:shadow-[0_8px_0_0_#0573c7,0_14px_24px_0_rgba(0,0,0,0.4)] active:translate-y-[4px] active:shadow-[0_2px_0_0_#0573c7,0_4px_10px_0_rgba(0,0,0,0.2)] focus:outline-none"
    aria-label="챗봇 열기"
    @click="open = !open"
  >
    <span v-if="open" class="text-xl font-medium">❌</span>
    <span
      v-else
      class="text-center text-[12pt] font-black leading-tight tracking-tighter drop-shadow-[0_1.5px_1px_rgba(0,0,0,0.3)]"
    >
      도와<br />줄까유?
    </span>
  </button>

  <Transition name="slide">
    <div
      v-if="open"
      class="fixed bottom-[8.25rem] right-6 z-50 flex h-[36.375rem] w-[26rem] flex-col overflow-hidden rounded-2xl border border-line bg-white shadow-2xl"
    >
      <div class="border-b border-line bg-brand px-5 py-4 text-white">
        <p class="text-lg font-bold">모여유 AI 도우미</p>
      </div>

      <div ref="listRef" class="flex-1 space-y-4 overflow-y-auto p-4">
        <div v-for="(msg, i) in messages" :key="i">
          <div
            class="max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed"
            :class="
              msg.role === 'user'
                ? 'ml-auto bg-brand text-white rounded-tr-none'
                : 'bg-brand-light text-ink rounded-tl-none'
            "
          >
            {{ msg.text }}
          </div>
          <div v-if="msg.results && msg.results.length" class="mt-3 space-y-3">
            <template v-if="msg.target === 'MEETING'">
              <MeetingCard v-for="m in msg.results" :key="m.id" :meeting="m" />
            </template>
            <template v-else-if="msg.target === 'LOCATION'">
              <PlaceCard v-for="p in msg.results" :key="p.id" :place="p" />
            </template>
          </div>
        </div>
      </div>

      <div class="border-t border-line bg-slate-50 p-4">
        <div class="mb-3 flex flex-wrap gap-2">
          <button
            v-for="s in suggestions"
            :key="s"
            type="button"
            class="rounded-full border border-line bg-white px-3 py-1.5 text-xs text-ink/70 transition-colors hover:border-brand hover:text-brand"
            @click="send(s)"
          >
            {{ s }}
          </button>
        </div>
        <div class="flex gap-2">
          <input
            v-model="input"
            type="text"
            placeholder="메시지를 입력하세요"
            class="field-input flex-1 text-sm bg-white"
            @keydown.enter="onKeydown"
          />
          <button type="button" class="btn-primary text-sm px-5" @click="send()">전송</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
