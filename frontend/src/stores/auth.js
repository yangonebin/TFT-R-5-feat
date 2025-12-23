import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null)
  const userInfo = ref(null) // 추가: 로그인한 유저 정보를 담을 변수
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()

  const isLogin = computed(() => token.value !== null)

  // 회원가입 (F02)
  const signUp = function (payload) {
    axios({
      method: 'post',
      url: `${API_URL}/accounts/signup/`,
      data: {
        username: payload.username,
        nickname: payload.nickname,
        password1: payload.password,
        password2: payload.passwordConfirm
      }
    })
    .then((res) => {
      alert('회원가입이 완료되었습니다! 로그인을 진행해주세요.')
      router.push({ name: 'login' })
    })
    .catch((err) => {
      console.error('상세 에러:', err.response?.data)
      alert("회원가입 실패: 입력한 정보를 다시 확인해주세요.")
    })
  }

  // 로그인 (F02)
 const logIn = function (payload) {
  axios({
    method: 'post',
    url: `${API_URL}/accounts/login/`,
    data: payload
  })
  .then((res) => {
    // 1. 토큰 저장
    token.value = res.data.access || res.data.key
    
    // 2. 유저 정보 저장 (중요!)
    // 서버 응답에 따라 res.data.user 전체를 넣거나 필드를 직접 지정합니다.
    userInfo.value = res.data.user 
    
    // 콘솔에 찍어서 nickname이나 username이 들어있는지 꼭 확인하세요
    console.log('로그인 유저 정보:', res.data.user)

    alert('반갑습니다! 로그인이 완료되었습니다.')
    router.push({ name: 'deposit' }) 
  })
  .catch((err) => {
    console.error(err)
    alert('아이디 또는 비밀번호를 확인하세요.')
  })
}

  // 로그아웃 (F02)
  const logOut = function () {
    token.value = null
    userInfo.value = null // 유저 정보 초기화
    alert('로그아웃 되었습니다.')
    router.push({ name: 'login' })
  }

  return { token, userInfo, isLogin, API_URL, signUp, logIn, logOut }
}, { persist: true })