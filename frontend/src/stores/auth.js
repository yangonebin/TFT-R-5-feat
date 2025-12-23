import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null)
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()

  const isLogin = computed(() => token.value !== null)

  // 회원가입
  const signUp = function (payload) {
    // 1. 프론트엔드 콘솔에서 데이터가 제대로 매핑되었는지 확인
    console.log('전송 시도 데이터:', payload)

    axios({
      method: 'post',
      url: `${API_URL}/accounts/signup/`,
      data: {
        username: payload.username,
        nickname: payload.nickname,
        password1: payload.password,        // payload.password가 존재해야 함
        password2: payload.passwordConfirm  // payload.passwordConfirm이 존재해야 함
      }
    })
    .then((res) => {
      alert('회원가입이 완료되었습니다! 로그인을 진행해주세요.')
      router.push({ name: 'login' })
    })
    .catch((err) => {
      const errorData = err.response?.data
      console.error('상세 에러:', errorData)
      
      let msg = ""
      if (errorData) {
        for (const key in errorData) {
          msg += `${key}: ${errorData[key]}\n`
        }
      }
      alert(msg || "가입 실패: 서버와의 통신 중 오류가 발생했습니다.")
    })
  }

  // 로그인
  const logIn = function (payload) {
    axios({
      method: 'post',
      url: `${API_URL}/accounts/login/`,
      data: payload
    })
    .then((res) => {
      // dj-rest-auth 설정에 따라 access 또는 key를 저장
      token.value = res.data.access || res.data.key
      alert('반갑습니다! 로그인이 완료되었습니다.')
      router.push({ name: 'deposit' }) // 가입 후 이동 경로 확인 필요
    })
    .catch((err) => {
      console.error(err)
      alert('아이디 또는 비밀번호를 확인하세요.')
    })
  }

  const logOut = function () {
    token.value = null
    alert('로그아웃 되었습니다.')
    router.push({ name: 'login' })
  }

  return { token, isLogin, API_URL, signUp, logIn, logOut }
}, { persist: true })