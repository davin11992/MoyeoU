<script setup>
import { ref } from "vue";

const props = defineProps({
  placeholder: {
    type: String,
    default: "모임 장소, 카테고리 키워드로 검색해보세요. (예: 관광)",
  },
  suggestions: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["search"]);

const query = ref("");

function submit() {
  if (!query.value.trim()) return;
  emit("search", query.value.trim());
}

function useSuggestion(text) {
  query.value = text;
  emit("search", text);
}

// CJK IME 조합 중에는 Enter 제출을 막습니다.
function onKeydown(e) {
  if (e.isComposing || e.keyCode === 229) return;
  submit();
}
</script>

<template>
  <div class="w-full">
    <div class="flex flex-col gap-2 sm:flex-row">
      <input
        v-model="query"
        type="text"
        :placeholder="props.placeholder"
        class="field-input flex-1"
        @keydown.enter="onKeydown"
      />
      <button type="button" class="btn-primary whitespace-nowrap" @click="submit">
        원하는 모임 찾기
      </button>
    </div>

    <div v-if="props.suggestions.length" class="mt-3 flex flex-wrap gap-2">
      <button
        v-for="s in props.suggestions"
        :key="s"
        type="button"
        class="chip"
        @click="useSuggestion(s)"
      >
        {{ s }}
      </button>
    </div>
  </div>
</template>
