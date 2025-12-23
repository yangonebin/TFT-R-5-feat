<template>
  <header class="header-wrapper">
    <div class="top-bar">
      <div class="container">
        <div class="top-menu">
          <template v-if="!store.isLogin">
            <RouterLink :to="{ name: 'login' }" class="util-link">로그인</RouterLink>
            <span class="divider"></span>
            <RouterLink :to="{ name: 'signup' }" class="util-link">회원가입</RouterLink>
          </template>

          <template v-else>
            <span class="greeting">
              {{ store.user?.nickname || store.user?.username }}님 반갑습니다!
            </span>
            <span class="divider"></span>
            <a href="#" @click.prevent="store.logOut" class="util-link">로그아웃</a>
          </template>
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
          <li><RouterLink :to="{ name: 'articles' }" class="nav-item">게시판</RouterLink></li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()
const router = useRouter()

// 로그아웃 시 추가 로직 처리를 위한 함수
const handleLogout = () => {
  if (confirm('로그아웃 하시겠습니까?')) {
    store.logOut()
    // 로그아웃 성공 후 메인 페이지로 이동 등의 추가 처리가 가능합니다.
  }
}
</script>

<style scoped>
/* 기존 스타일을 유지하되 가독성을 위한 변수 처리를 확인하세요 */
:root {
  --color-primary: #3498db;
  --color-primary-light: #5dade2;
}

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
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.util-link:hover {
  color: #3498db; /* var 대신 직접 입력하거나 전역 스타일 확인 */
  font-weight: 500;
}

.greeting {
  color: #2c3e50;
  font-weight: 600;
  margin-right: 4px;
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
  color: #3498db;
  letter-spacing: -0.5px;
  text-decoration: none;
}

.gnb {
  display: flex;
  gap: 40px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  font-size: 17px;
  font-weight: 600;
  color: #333;
  padding: 8px 0;
  position: relative; 
  transition: color 0.3s;
  text-decoration: none;
}

.nav-item:hover {
  color: #3498db;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0%;
  height: 2px;
  background-color: #3498db;
  transition: width 0.3s;
}

.nav-item:hover::after {
  width: 100%;
}
</style>