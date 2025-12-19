<template>
  <div class="container">
    <h1 class="page-title">관심 종목 뉴스</h1>
    
    <div class="search-box">
      <input 
        type="text" 
        v-model="keyword" 
        @keyup.enter="onSearch" 
        placeholder="종목명이나 이슈를 검색해보세요 (예: 삼성전자)"
      >
      <button @click="onSearch" class="search-btn">검색</button>
    </div>

    <div v-if="store.videos.length > 0" class="video-grid">
      <div 
        v-for="video in store.videos" 
        :key="video.id.videoId" 
        class="video-card"
        @click="goToDetail(video)"
      >
        <div class="thumbnail">
          <img :src="video.snippet.thumbnails.medium.url" alt="thumbnail">
        </div>
        <div class="info">
          <h3 class="video-title" v-html="video.snippet.title"></h3>
          <p class="channel-name">{{ video.snippet.channelTitle }}</p>
          <p class="date">{{ formatDate(video.snippet.publishTime) }}</p>
        </div>
      </div>
    </div>

    <div v-else class="no-result">
      <p>검색 결과가 없습니다.<br>관심 있는 경제 이슈를 검색해보세요.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useYoutubeStore } from '@/stores/youtube'

const store = useYoutubeStore()
const router = useRouter()
const keyword = ref('')

const onSearch = () => {
  if (keyword.value.trim()) {
    store.searchVideos(keyword.value)
  }
}

const goToDetail = (video) => {
  store.clickVideo(video) // 선택한 영상 정보 저장
  router.push({ 
    name: 'stock-detail', 
    params: { videoId: video.id.videoId } 
  })
}

// 날짜 포맷팅 (YYYY-MM-DD)
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toISOString().split('T')[0]
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: #154580;
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 50px;
}

.search-box input {
  width: 400px;
  padding: 12px 20px;
  border: 1px solid #ddd;
  border-radius: 30px;
  font-size: 1rem;
}

.search-btn {
  padding: 12px 24px;
  background-color: #3182f6;
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-weight: 600;
}

/* 카드 그리드 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.video-card {
  cursor: pointer;
  transition: transform 0.2s;
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.thumbnail img {
  width: 100%;
  height: auto;
  display: block;
}

.info {
  padding: 16px;
}

.video-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.channel-name {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.date {
  font-size: 0.8rem;
  color: #999;
  margin-top: 4px;
}

.no-result {
  text-align: center;
  padding: 50px;
  color: #888;
}
</style>