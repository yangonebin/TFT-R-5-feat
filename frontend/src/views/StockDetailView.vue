<template>
  <div class="container" v-if="video">
    <h2 class="video-title" v-html="video.snippet.title"></h2>
    
    <div class="video-wrapper">
      <iframe 
        width="100%" 
        height="500" 
        :src="videoUrl" 
        title="YouTube video player" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
      ></iframe>
    </div>

    <div class="video-info">
      <div class="channel-info">
        <h3>{{ video.snippet.channelTitle }}</h3>
        <p class="upload-date">게시일: {{ formatDate(video.snippet.publishTime) }}</p>
      </div>
      <p class="description">{{ video.snippet.description }}</p>
      
      <button class="back-btn" @click="$router.go(-1)">목록으로 돌아가기</button>
    </div>
  </div>
  
  <div v-else class="loading">
    <p>영상 정보를 불러오는 중이거나 존재하지 않습니다.</p>
    <button class="back-btn" @click="$router.push({ name: 'stock' })">검색하러 가기</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useYoutubeStore } from '@/stores/youtube'

const route = useRoute()
const store = useYoutubeStore()

// store에 저장된 선택된 비디오 가져오기
const video = computed(() => store.selectedVideo)

// iframe src 생성
const videoUrl = computed(() => {
  const videoId = route.params.videoId
  return `https://www.youtube.com/embed/${videoId}`
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.video-title {
  font-size: 1.8rem;
  margin-bottom: 20px;
  color: #111;
}

.video-wrapper {
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  border-radius: 12px;
  overflow: hidden;
}

.video-info {
  background: white;
  padding: 30px;
  border-radius: 12px;
  border: 1px solid #eee;
}

.channel-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.channel-info h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #154580;
}

.description {
  white-space: pre-line; /* 줄바꿈 적용 */
  color: #555;
  line-height: 1.6;
  margin-bottom: 30px;
}

.back-btn {
  padding: 10px 20px;
  background-color: #666;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
}

.back-btn:hover {
  background-color: #444;
}

.loading {
  text-align: center;
  padding: 100px;
}
</style>