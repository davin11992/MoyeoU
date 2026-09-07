<script setup>
import AppHeader from '@/components/AppHeader.vue'
import ChatbotWidget from '@/components/ChatbotWidget.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1">
      <router-view />
    </main>
    <footer class="border-t border-line bg-white py-6 text-center text-sm text-ink/60">
      모여유 · SSAFY 대전 캠퍼스 번개 모임 커뮤니티
    </footer>
    <ChatbotWidget />
  </div>
</template>
