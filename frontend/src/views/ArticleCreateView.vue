<template>
  <div class="create-container">
    <h1>📝 새 글 작성하기</h1>
    <form @submit.prevent="createArticle" class="create-form">
      <div class="form-group">
        <label for="title">제목</label>
        <input type="text" id="title" v-model="title" placeholder="제목을 입력해주세요" required>
      </div>
      <div class="form-group">
        <label for="content">내용</label>
        <textarea id="content" v-model="content" placeholder="내용을 입력해주세요" rows="10" required></textarea>
      </div>
      <div class="btn-group">
        <button type="submit" class="submit-btn">작성 완료</button>
        <button type="button" @click="router.back()" class="cancel-btn">취소</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const store = useAuthStore()
const router = useRouter()
const title = ref('')
const content = ref('')

const createArticle = () => {
  // 1. 토큰 확인
  if (!store.token) {
    alert('로그인이 필요한 기능입니다.')
    router.push({ name: 'login' })
    return
  }

  axios({
    method: 'post',
    // ✅ [핵심 수정 1] 주소에 'articles'가 한 번만 들어가야 함!
    url: `${store.API_URL}/articles/`, 
    data: {
      title: title.value,
      content: content.value
    },
    headers: {
      // ✅ [핵심 수정 2] JWT 방식은 보통 'Bearer'를 씁니다.
      Authorization: `Bearer ${store.token}`
    }
  })
    .then(() => {
      alert('게시글이 등록되었습니다!')
      router.push({ name: 'articles' })
    })
    .catch((err) => {
      console.error(err)
      alert('작성 실패! (콘솔의 에러 메시지를 확인하세요)')
    })
}
</script>

<style scoped>
.create-container { max-width: 800px; margin: 40px auto; padding: 30px; background: #fff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
.form-group { margin-bottom: 20px; }
label { display: block; font-weight: bold; margin-bottom: 8px; color: #34495e; }
input, textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
.btn-group { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
button { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
.submit-btn { background-color: #3498db; color: white; }
.cancel-btn { background-color: #95a5a6; color: white; }
</style>