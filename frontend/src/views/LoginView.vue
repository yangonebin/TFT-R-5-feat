<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <h1>로그인</h1>
        <p>이용을 위해 아이디와 비밀번호를 입력해주세요.</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="input-container">
          <label for="username">아이디</label>
          <input 
            type="text" 
            id="username" 
            v-model.trim="username" 
            placeholder="아이디를 입력하세요" 
            required
          >
        </div>

        <div class="input-container">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model.trim="password" 
            placeholder="비밀번호를 입력하세요" 
            required
          >
        </div>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <div class="auth-footer">
        <span>계정이 없으신가요?</span>
        <router-link :to="{ name: 'signup' }">회원가입 하러가기</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()
const username = ref('')
const password = ref('')
const isLoading = ref(false) // 로그인 중 버튼 비활성화를 위한 상태

const handleLogin = async function () {
  if (!username.value || !password.value) {
    alert('아이디와 비밀번호를 모두 입력해주세요.')
    return
  }

  isLoading.value = true
  const payload = {
    username: username.value,
    password: password.value
  }
  
  // store의 logIn 함수를 실행
  try {
    await store.logIn(payload)
    // 성공 시 로직은 store.logIn 내부의 router.push가 처리함
  } catch (err) {
    console.error('로그인 에러:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 기존 CSS 스타일 유지 */
.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #f0f4f8;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  background: white;
  padding: 50px 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

.auth-header {
  text-align: center;
  margin-bottom: 35px;
}

.auth-header h1 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 12px;
  font-weight: 700;
}

.auth-header p {
  font-size: 15px;
  color: #7f8c8d;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-container label {
  font-size: 14px;
  font-weight: 500;
  color: #34495e;
  text-align: left;
}

.input-container input {
  padding: 14px;
  border: 1px solid #e0e6ed;
  border-radius: 8px;
  font-size: 15px;
  background-color: #f9fbfe;
  transition: all 0.3s ease;
}

.input-container input:focus {
  outline: none;
  border-color: #3498db;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.btn-primary {
  margin-top: 10px;
  padding: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: 30px;
  text-align: center;
  font-size: 14px;
  color: #95a5a6;
}

.auth-footer a {
  margin-left: 10px;
  color: #3498db;
  text-decoration: none;
  font-weight: 600;
}
</style>