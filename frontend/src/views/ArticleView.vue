<template>
  <div class="community-container">
    <header class="community-header">
      <div>
        <h1>🗣️ 자유 게시판</h1>
        <p class="subtitle">자유롭게 이야기를 나누는 공간입니다.</p>
      </div>
      <button class="write-btn">✏️ 글쓰기</button>
    </header>

    <div class="article-list">
      <div 
        v-for="article in articles" 
        :key="article.id" 
        class="article-card"
      >
        <div class="card-main">
          <h3 class="article-title">
            <span v-if="article.id === 1" class="notice-badge">공지</span>
            {{ article.title }}
          </h3>
          <div class="comment-count__wrapper">
             💬 <span class="comment-count">{{ article.comment_count }}</span>
          </div>
        </div>
        
        <div class="card-meta">
          <span class="author">{{ article.user }}</span>
          <span class="separator">·</span>
          <span class="date">{{ article.created_at }}</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

// 💡 임시 데이터 (백엔드가 아직 준비 안 됐을 때 화면 확인용)
const articles = ref([
  { id: 1, title: '커뮤니티 이용 규칙 안내 (필독)', user: '관리자', created_at: '2023.11.01', comment_count: 25 },
  { id: 2, title: '요즘 예적금 금리 너무 낮지 않나요? ㅠㅠ', user: '김싸피', created_at: '2023.11.15', comment_count: 12 },
  { id: 3, title: '주식 초보 질문드립니다! 삼성전자 지금 사도 될까요?', user: '이주린', created_at: '2023.11.15', comment_count: 8 },
  { id: 4, title: '오늘 점심 메뉴 추천 좀 해주세요', user: '배고파', created_at: '2023.11.14', comment_count: 3 },
  { id: 5, title: '환율이 계속 오르네요. 여행 갈 수 있을까요?', user: '여행가고파', created_at: '2023.11.13', comment_count: 19 },
])

// 나중에 백엔드가 준비되면 이 부분을 활성화해서 진짜 데이터를 받아오면 됩니다.
/*
import axios from 'axios'
import { onMounted } from 'vue'

onMounted(() => {
  axios({
    method: 'get',
    url: 'http://127.0.0.1:8000/api/v1/articles/'
  })
  .then(res => articles.value = res.data)
  .catch(err => console.log(err))
})
*/
</script>

<style scoped>

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
  background-color: var(--color-primary-light); 
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.write-btn:hover {
  background-color: var(--color-primary);
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
  border-color: var(--color-primary-light);
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

.notice-badge {
    background-color: #ffe3e3;
    color: #e03131;
    font-size: 0.8rem;
    padding: 4px 8px;
    border-radius: 4px;
    margin-right: 8px;
    vertical-align: middle;
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
    color: var(--color-primary-light);
}


.card-meta {
  font-size: 0.9rem;
  color: #adb5bd;
}

.separator {
  margin: 0 8px;
}
</style>