<template>
  <div class="community-container">
    <header class="community-header">
      <div>
        <h1>🗣️ 자유 게시판</h1>
        <p class="subtitle">자유롭게 이야기를 나누는 공간입니다.</p>
      </div>
      <button class="write-btn" @click="router.push({ name: 'article-create' })" v-if="store.isLogin">
        ✏️ 글쓰기
      </button>
    </header>

    <div class="article-list">
      <div v-if="articles.length === 0" class="no-article">
        아직 작성된 게시글이 없습니다. 첫 번째 글을 남겨보세요!
      </div>

      <div 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card"
        @click="goDetail(article.id)"
      >
        <div class="card-main">
          <h3 class="article-title">
            {{ article.title }}
          </h3>
          <div class="comment-count__wrapper">
             💬 <span class="comment-count">{{ article.comments?.length || 0 }}</span>
          </div>
        </div>
        
        <div class="card-meta">
          <span class="author">{{ article.user_name }}</span>
          <span class="separator">·</span>
          <span class="date">{{ article.created_at?.substring(0, 10) }}</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const store = useAuthStore()
const router = useRouter()
const articles = ref([])

// 백엔드에서 데이터 가져오기
onMounted(() => {
  axios({
    method: 'get',
    // ✅ [핵심 수정] 기존 '/articles/articles/' -> '/articles/' 로 변경!
    url: `${store.API_URL}/articles/` 
  })
  .then(res => {
    // ✅ [추가 기능] 최신 글이 위로 오도록 뒤집어서 저장 (.reverse())
    articles.value = res.data.reverse()
    console.log('게시글 목록 로드 성공:', res.data)
  })
  .catch(err => {
    console.log(err)
  })
})

// 상세 페이지로 이동 함수
const goDetail = (id) => {
  // router 이름이 'article-detail'인지 꼭 확인하세요!
  router.push({ name: 'article-detail', params: { id } })
}
</script>

<style scoped>
/* 기존 스타일 그대로 유지 */
.community-container {
  max-width: 900px; 
  margin: 40px auto; 
  padding: 0 20px;
}

.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f3f5;
}

.community-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #212529;
  margin-bottom: 8px;
}

.subtitle {
  color: #868e96;
  font-size: 1rem;
}

.write-btn {
  background-color: #4dabf7; 
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.write-btn:hover {
  background-color: #339af0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(49, 130, 246, 0.3);
}

.article-card {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
  cursor: pointer; 
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.article-card:hover {
  transform: translateY(-3px); 
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #a5d8ff;
}

.card-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.article-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #343a40;
  margin: 0;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 80%;
}

.comment-count__wrapper {
    font-size: 0.9rem;
    color: #868e96;
    display: flex;
    align-items: center;
}

.comment-count {
    margin-left: 4px;
    font-weight: 600;
    color: #4dabf7;
}

.card-meta {
  font-size: 0.9rem;
  color: #adb5bd;
}

.separator {
  margin: 0 8px;
}

.no-article {
  text-align: center;
  padding: 40px;
  color: #868e96;
}
</style>