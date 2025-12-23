<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <h1>회원가입</h1>
        <p>나만의 금융 비서, FinMatch에 오신 것을 환영합니다!</p>
      </div>

      <form @submit.prevent="signUp" class="auth-form">
        <div class="input-container">
          <label for="username">아이디</label>
          <input type="text" id="username" v-model="username" placeholder="사용할 아이디를 입력하세요" required>
        </div>

        <div class="input-container">
          <label for="nickname">닉네임</label>
          <input type="text" id="nickname" v-model="nickname" placeholder="표시될 이름을 입력하세요">
        </div>

        <div class="input-container">
          <label for="password">비밀번호</label>
          <input type="password" id="password" v-model="password" placeholder="비밀번호를 입력하세요" required>
        </div>

        <div class="input-container">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input type="password" id="passwordConfirm" v-model="passwordConfirm" placeholder="비밀번호를 한 번 더 입력하세요" required>
        </div>

        <button type="submit" class="btn-primary">가입하기</button>
      </form>

      <div class="auth-footer">
        <span>이미 계정이 있으신가요?</span>
        <router-link :to="{ name: 'login' }">로그인 하러가기</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const store = useAuthStore()

// 반응형 변수 선언
const username = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')

const signUp = function () {
  
  if (password.value !== passwordConfirm.value) {
    alert('비밀번호가 일치하지 않습니다.')
    return
  }

  const payload = {
    username: username.value,
    nickname: nickname.value,
    password: password.value,
    passwordConfirm: passwordConfirm.value,
  }
  
  store.signUp(payload)
}
</script>

<style scoped>
.auth-wrapper { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  min-height: 85vh; 
  background-color: #f0f4f8; 
}
.auth-card { 
  width: 100%; 
  max-width: 450px; 
  background: white; 
  padding: 40px; 
  border-radius: 16px; 
  box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
}
.auth-header { 
  text-align: center; 
  margin-bottom: 30px; 
}
.auth-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
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
  text-align: left; 
}
.input-container label { 
  font-size: 14px; 
  font-weight: 600; 
  color: #34495e; 
}
.input-container input { 
  padding: 14px; 
  border: 1px solid #e0e6ed; 
  border-radius: 8px; 
  font-size: 15px; 
  outline: none;
  transition: border-color 0.2s;
}
.input-container input:focus {
  border-color: #3498db;
}
.btn-primary { 
  margin-top: 10px; 
  padding: 16px; 
  background-color: #3498db; 
  color: white; 
  border: none; 
  border-radius: 8px; 
  font-size: 16px; 
  font-weight: bold; 
  cursor: pointer; 
}
.btn-primary:hover {
  background-color: #2980b9;
}
.auth-footer { 
  margin-top: 25px; 
  text-align: center; 
  font-size: 14px; 
  color: #95a5a6; 
}
.auth-footer a {
  color: #3498db;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
}
</style>