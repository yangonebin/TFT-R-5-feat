<template>
  <div class="page-container">
    
    <div v-if="!article" class="loading-state">
      <div class="spinner"></div>
      <p>데이터를 불러오는 중입니다...</p>
    </div>

    <div v-else class="article-card">
      
      <header class="card-header">
        <div class="header-top">
          <span class="category-badge">자유게시판</span>
          <div class="action-buttons" v-if="store.user?.username === article.user_name">
            <button @click="deleteArticle" class="btn-delete">삭제</button>
          </div>
        </div>
        <h1 class="title">{{ article.title }}</h1>
        <div class="meta-info">
          <div class="user-info">
            <div class="avatar-placeholder">{{ article.user_name.charAt(0).toUpperCase() }}</div>
            <span class="username">{{ article.user_name }}</span>
          </div>
          <span class="date">{{ article.created_at?.substring(0, 10) }}</span>
        </div>
      </header>

      <hr class="divider">

      <section class="card-body">
        <div class="content">{{ article.content }}</div>
      </section>

      <hr class="divider">

      <section class="comment-section">
        <h3>댓글 <span class="comment-count">{{ article.comments?.length || 0 }}</span></h3>

        <ul class="comment-list">
          <li v-for="comment in article.comments" :key="comment.id" class="comment-item">
            <div class="comment-avatar">
              {{ comment.user_name.charAt(0) }}
            </div>
            <div class="comment-content-wrapper">
              <div class="comment-header">
                <span class="comment-author">{{ comment.user_name }}</span>
                <button 
                  v-if="store.user?.username === comment.user_name" 
                  @click="deleteComment(comment.id)"
                  class="btn-comment-delete"
                >✕</button>
              </div>
              <p class="comment-text">{{ comment.content }}</p>
            </div>
          </li>
          <li v-if="article.comments?.length === 0" class="no-comments">
            첫 번째 댓글을 남겨보세요!
          </li>
        </ul>

        <div class="comment-form" v-if="store.isLogin">
          <input 
            v-model="commentContent" 
            placeholder="따뜻한 댓글을 남겨주세요..." 
            @keyup.enter="createComment"
            class="comment-input"
          >
          <button @click="createComment" class="btn-submit" :disabled="!commentContent.trim()">등록</button>
        </div>
        <div v-else class="login-plz">
          <p>댓글을 작성하려면 <router-link :to="{name: 'login'}">로그인</router-link>이 필요합니다.</p>
        </div>
      </section>

      <div class="card-footer">
        <button @click="router.push({ name: 'articles' })" class="btn-back">목록으로</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const store = useAuthStore()
const article = ref(null)
const commentContent = ref('')

// 게시글 불러오기
const fetchArticle = () => {
  axios.get(`${store.API_URL}/articles/${route.params.id}/`)
    .then(res => article.value = res.data)
    .catch(err => {
      console.error(err)
      alert('게시글을 불러오지 못했습니다.')
      router.push({ name: 'articles' })
    })
}

onMounted(fetchArticle)

// 게시글 삭제
const deleteArticle = () => {
  if(!confirm('정말 삭제하시겠습니까? 복구할 수 없습니다.')) return
  
  axios.delete(`${store.API_URL}/articles/${article.value.id}/`, {
    headers: { Authorization: `Bearer ${store.token}` }
  })
  .then(() => {
    alert('삭제되었습니다.')
    router.push({ name: 'articles' })
  })
  .catch(err => console.error(err))
}

// 댓글 작성
const createComment = () => {
  if (!commentContent.value.trim()) return
  
  axios.post(`${store.API_URL}/articles/${article.value.id}/comments/`, 
    { content: commentContent.value },
    { headers: { Authorization: `Bearer ${store.token}` } }
  )
  .then(() => {
    commentContent.value = ''
    fetchArticle()
  })
  .catch(err => console.error(err))
}

// 댓글 삭제
const deleteComment = (commentId) => {
  if(!confirm('댓글을 삭제할까요?')) return
  
  axios.delete(`${store.API_URL}/articles/${article.value.id}/comments/${commentId}/`, {
    headers: { Authorization: `Bearer ${store.token}` }
  })
  .then(() => fetchArticle())
  .catch(err => console.error(err))
}
</script>

<style scoped>
/* 전체 배경 및 레이아웃 */
.page-container {
  background-color: #f8f9fa; /* 아주 연한 회색 배경 */
  min-height: 100vh;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
}

/* 카드 스타일 (핵심) */
.article-card {
  background: white;
  width: 100%;
  max-width: 800px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
  padding: 40px;
  display: flex;
  flex-direction: column;
}

/* 1. 헤더 영역 */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.category-badge {
  background-color: #e7f5ff;
  color: #1c7ed6;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  color: #343a40;
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #868e96;
  font-size: 0.95rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-placeholder {
  width: 32px;
  height: 32px;
  background-color: #dee2e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #495057;
}

.divider {
  border: 0;
  height: 1px;
  background: #f1f3f5;
  margin: 30px 0;
}

/* 2. 본문 영역 */
.content {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #495057;
  min-height: 150px;
  white-space: pre-wrap; /* 줄바꿈 유지 */
}

/* 3. 댓글 영역 */
.comment-section h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-count {
  color: #1c7ed6;
}

.comment-list {
  list-style: none;
  padding: 0;
  margin-bottom: 30px;
}

.comment-item {
  display: flex;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #f8f9fa;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  background-color: #e9ecef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #868e96;
  flex-shrink: 0;
}

.comment-content-wrapper {
  flex-grow: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.comment-author {
  font-weight: 700;
  font-size: 0.95rem;
}

.btn-comment-delete {
  background: none;
  border: none;
  color: #adb5bd;
  cursor: pointer;
  font-size: 1rem;
  padding: 0 5px;
  transition: color 0.2s;
}

.btn-comment-delete:hover {
  color: #fa5252;
}

.comment-text {
  margin: 0;
  font-size: 0.95rem;
  color: #495057;
}

/* 댓글 입력 폼 */
.comment-form {
  display: flex;
  gap: 10px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 12px;
}

.comment-input {
  flex-grow: 1;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 12px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.comment-input:focus {
  outline: none;
  border-color: #339af0;
}

.btn-submit {
  background-color: #339af0;
  color: white;
  border: none;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background-color: #1c7ed6;
}
.btn-submit:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}

/* 4. 버튼 스타일 */
.btn-delete {
  background-color: #fff0f6;
  color: #f03e3e;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-delete:hover {
  background-color: #ffdeeb;
}

.card-footer {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.btn-back {
  background-color: white;
  border: 1px solid #ced4da;
  color: #495057;
  padding: 10px 30px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background-color: #f1f3f5;
  border-color: #adb5bd;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  color: #868e96;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f3f5;
  border-top-color: #339af0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>