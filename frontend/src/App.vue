<template>
  <div class="app-wrapper">
    <TheHeader />
    <div class="main-content">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'

import TheHeader from '@/components/Common/TheHeader.vue' 
</script>

<style>

@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");


:root {
  
  --color-primary: #154580;       
  --color-primary-light: #3182f6; 
  --color-bg: #f5f7fa;          
  --color-text: #333333;          
  --color-gray: #8b95a1;          
}

body {
  margin: 0;
  font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, "Helvetica Neue", "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
  -webkit-font-smoothing: antialiased;
  background-color: var(--color-bg);
  color: var(--color-text);
}

a {
  text-decoration: none;
  color: inherit;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}
</style>