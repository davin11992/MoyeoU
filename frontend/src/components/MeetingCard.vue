<script setup>
import { RouterLink } from "vue-router";

defineProps({
  meeting: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <RouterLink
    :to="`/meetings/${meeting.id}`"
    class="card block border border-line rounded-xl bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
  >
    <div class="mb-3 flex items-center justify-between gap-2">
      <span class="rounded-full bg-brand-light px-2.5 py-1 text-xs font-medium text-brand-hover">
        {{ meeting.category }}
      </span>

      <span
        class="rounded-full px-2.5 py-1 text-xs font-medium transition-colors"
        :class="{
          'bg-brand text-white': meeting.status === 'OPEN',
          'bg-gray-200 text-gray-700': meeting.status === 'CLOSED',
          'bg-line text-ink/60': meeting.status !== 'OPEN' && meeting.status !== 'CLOSED',
        }"
      >
        <template v-if="meeting.status === 'OPEN'">모집 중</template>
        <template v-else-if="meeting.status === 'CLOSED'">모집 완료</template>
        <template v-else>마감</template>
      </span>
    </div>

    <h3 class="mb-2 text-lg font-semibold text-ink">{{ meeting.title }}</h3>

    <ul class="space-y-1 text-sm text-ink/70">
      <li>
        일시 · {{ meeting.meeting_date }}
        {{ meeting.meeting_time ? meeting.meeting_time.substring(0, 5) : "" }}
      </li>
      <li>장소 · {{ meeting.location_name }}</li>
      <li>인원 · {{ meeting.current_participants }} / {{ meeting.max_participants }}명</li>
    </ul>
  </RouterLink>
</template>
