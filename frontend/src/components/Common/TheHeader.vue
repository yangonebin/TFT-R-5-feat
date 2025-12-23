<template>
  <header class="main-header">
    <div class="top-util-bar">
      <div class="container top-content">
        <div v-if="store.isLogin" class="user-info-area">
          <span class="welcome-text">
            <strong>{{ store.user?.username }}</strong>님 반갑습니다!
          </span>
          <RouterLink :to="{ name: 'profile' }" class="top-link bold">마이페이지</RouterLink>
          <span class="divider">|</span>
          <a @click.prevent="store.logOut" class="top-link logout">로그아웃</a>
        </div>
        <div v-else class="user-info-area">
          <RouterLink :to="{ name: 'login' }" class="top-link">로그인</RouterLink>
          <span class="divider">|</span>
          <RouterLink :to="{ name: 'signup' }" class="top-link">회원가입</RouterLink>
        </div>
      </div>
    </div>

    <div class="nav-main-bar">
      <div class="container nav-content">
        <RouterLink :to="{ name: 'home' }" class="main-logo">
          FinMatch
        </RouterLink>

        <nav class="main-navigation">
          <RouterLink :to="{ name: 'deposit' }" class="nav-item">예금비교</RouterLink>
          <RouterLink :to="{ name: 'exchange' }" class="nav-item">현물가격</RouterLink>
          <RouterLink :to="{ name: 'stock' }" class="nav-item">주식정보</RouterLink>
          <RouterLink :to="{ name: 'map' }" class="nav-item">은행지도</RouterLink>
          <RouterLink :to="{ name: 'articles' }" class="nav-item">게시판</RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()
</script>

<style scoped>
.main-header {
  width: 100%;
  background-color: #ffffff;
}

.container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 1. 최상단 유저 바 스타일 (image_adeccd.png 참고) */
.top-util-bar {
  background-color: #ffffff;
  border-bottom: 1px solid #f2f2f2;
  height: 35px;
  display: flex;
  align-items: center;
}

.top-content {
  display: flex;
  justify-content: flex-end; /* 오른쪽 끝 정렬 */
  width: 100%;
}

.user-info-area {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #888;
}

.top-link {
  text-decoration: none;
  color: #888;
  cursor: pointer;
}

.top-link.bold {
  color: #339af0;
  font-weight: bold;
}

.top-link.logout {
  color: #fa5252;
}

.divider {
  color: #eee;
}

/* 2. 메인 바 스타일 (image_ade94a.png 참고) */
.nav-main-bar {
  height: 75px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e1e4e8;
}

.nav-content {
  display: flex;
  justify-content: space-between; /* 양 끝 정렬 */
  align-items: center;
  width: 100%;
}

/* 로고 스타일 */
.main-logo {
  font-size: 1.8rem;
  font-weight: 900;
  color: #339af0;
  text-decoration: none;
  font-style: italic; /* 사용자님 로고 스타일 반영 */
}

/* 서비스 메뉴: 오른쪽 정렬 */
.main-navigation {
  display: flex;
  gap: 30px; /* 메뉴 간 간격 */
}

.nav-item {
  text-decoration: none;
  color: #444;
  font-size: 1.05rem;
  font-weight: 600;
  transition: all 0.2s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #339af0;
  border-bottom: 2px solid #339af0;
  padding-bottom: 5px;
}

/* 반응형 */
@media (max-width: 900px) {
  .main-navigation {
    gap: 15px;
  }
  .nav-item {
    font-size: 0.9rem;
  }
}
</style>