<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
})

defineEmits(['close'])
</script>

<template>
  <Transition name="fade">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-lg" role="dialog" aria-modal="true">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-ink">{{ title }}</h2>
          <button
            type="button"
            class="text-ink/50 transition-colors hover:text-ink"
            aria-label="닫기"
            @click="$emit('close')"
          >
            ✕
          </button>
        </div>
        <slot />
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
