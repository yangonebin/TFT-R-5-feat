import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const token = ref(null)
  const user = ref(null) 

  const isAuthenticated = computed(() => !!token.value) 
  const API_URL = 'http://127.0.0.1:8000'


  const signUp = function (payload) {

    const signupData = {
      ...payload,
      password2: payload.password2 || payload.password 
    }

    axios({
      method: 'post',
      url: `${API_URL}/accounts/signup/`,
      data: signupData 
    })
      .then((res) => {
        alert('회원가입이 완료되었습니다!')
        
        router.push({ name: 'LogInView' }) 
      })
      .catch((err) => {
        console.log(err)
       
        const msg = err.response?.data ? JSON.stringify(err.response.data) : '입력 정보를 확인하세요.'
        alert(`회원가입 실패: ${msg}`)
      })
  }


  const logIn = function (payload) {
    axios({
      method: 'post',
      url: `${API_URL}/accounts/login/`,
      data: payload
    })
      .then((res) => {

        const accessToken = res.data.access || res.data.key
        
        token.value = accessToken
        localStorage.setItem('token', accessToken) 
        
        alert('로그인 성공!')
    
        router.push({ name: 'home' }) 
      })
      .catch((err) => {
        console.log(err)
        alert('로그인 실패: 아이디와 비밀번호를 확인해주세요.')
      })
  }


  const logOut = function () {
    token.value = null
    user.value = null
    localStorage.removeItem('token') 
    
    alert('로그아웃 되었습니다.')
    router.push({ name: 'LogInView' }) 
  }

  return { token, user, isAuthenticated, signUp, logIn, logOut, API_URL }
}, { persist: true })