<template>
  <header class="header-wrapper">
    <div class="top-bar">
      <div class="container">
        <div class="top-menu">
          <RouterLink :to="{ name: 'login' }" class="util-link">로그인</RouterLink>
          <span class="divider"></span>
          <RouterLink :to="{ name: 'signup' }" class="util-link">회원가입</RouterLink>
        </div>
      </div>
    </div>

    <nav class="navbar">
      <div class="container nav-container">
        <RouterLink :to="{ name: 'home' }" class="logo">
          Bankbook
        </RouterLink>

        <ul class="gnb">
          <li><RouterLink :to="{ name: 'deposit' }" class="nav-item">예금비교</RouterLink></li>
          <li><RouterLink :to="{ name: 'exchange' }" class="nav-item">현물상품</RouterLink></li>
          <li><RouterLink :to="{ name: 'stock' }" class="nav-item">주식정보</RouterLink></li>
          <li><RouterLink :to="{ name: 'map' }" class="nav-item">은행지도</RouterLink></li>
          <li><RouterLink :to="{ name: 'community' }" class="nav-item">게시판</RouterLink></li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>

.header-wrapper {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.top-bar {
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
  padding: 8px 0;
  font-size: 13px;
}

.top-menu {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.util-link {
  color: #666;
  transition: color 0.2s;
}

.util-link:hover {
  color: var(--color-primary-light);
  font-weight: 500;
}

.divider {
  width: 1px;
  height: 10px;
  background-color: #ddd;
  margin: 0 12px;
}

.navbar {
  padding: 16px 0;
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 26px;
  font-weight: 800; 
  color: var(--color-primary);
  letter-spacing: -0.5px;
}

.gnb {
  display: flex;
  gap: 40px;
}

.nav-item {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  padding: 8px 0;
  position: relative; 
  transition: color 0.3s;
}

.nav-item:hover {
  color: var(--color-primary-light);
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0%;
  height: 2px;
  background-color: var(--color-primary-light);
  transition: width 0.3s;
}

.nav-item:hover::after {
  width: 100%;
}
</style>