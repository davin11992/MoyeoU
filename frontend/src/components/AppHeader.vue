<script setup>
import { RouterLink } from 'vue-router'

const navLinks = [
  { label: '홈', to: '/' },
  { label: '모임 찾기', to: '/meetings' },
  { label: '캠퍼스 주변', to: '/locations' },
]
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-line bg-white/90 backdrop-blur">
    <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
      <RouterLink to="/" class="flex items-center gap-2">
        <span class="text-2xl font-bold text-brand">모여유</span>
        <span class="rounded-md bg-brand px-2 py-0.5 text-xs font-semibold text-white">SSAFY 대전</span>
      </RouterLink>

      <nav class="flex items-center gap-1">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="rounded-lg px-3 py-2 text-sm font-medium text-ink/70 transition-colors hover:text-brand"
          exact-active-class="text-brand"
        >
          {{ link.label }}
        </RouterLink>
        <RouterLink to="/meetings/new" class="btn-primary ml-2 text-sm">
          모임 만들기
        </RouterLink>
      </nav>
    </div>
  </header>
</template>
