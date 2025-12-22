import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null)
  const API_URL = 'http://127.0.0.1:8000'
  const router = useRouter()

  // 로그인 여부 확인
  const isLogin = computed(() => token.value !== null)

const signUp = function (payload) {
  // 전송 전 데이터가 잘 담겼는지 확인용
  console.log('전송 데이터:', payload)

  axios({
    method: 'post',
    url: `${API_URL}/accounts/signup/`,
    data: {
      username: payload.username,
      nickname: payload.nickname,
      password1: payload.password,        // 'password'가 아닌 'password1'
      password2: payload.passwordConfirm  // 'passwordConfirm'이 아닌 'password2'
    }
  })
  .then((res) => {
    alert('회원가입이 완료되었습니다! 로그인을 진행해주세요.')
    router.push({ name: 'login' })
  })
  .catch((err) => {
    // 에러 발생 시 서버가 주는 답변을 구체적으로 확인
    const errorData = err.response?.data
    console.error('가입 실패 상세 이유:', errorData)
    
    // 무엇이 문제인지 상세히 알림
    if (errorData?.password1) {
      alert(`비밀번호 오류: ${errorData.password1[0]}`)
    } else if (errorData?.username) {
      alert(`아이디 오류: ${errorData.username[0]}`)
    } else {
      alert('가입 정보를 다시 확인해주세요.')
    }
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
        // dj-rest-auth 응답에서 토큰 저장
        token.value = res.data.access_token || res.data.key
        router.push({ name: 'ProductListView' }) // 로그인 후 이동할 페이지
      })
      .catch((err) => alert('아이디 또는 비밀번호를 확인하세요.'))
  }

  // 로그아웃
  const logOut = function () {
    token.value = null
    router.push({ name: 'LoginView' })
  }

  return { token, isLogin, API_URL, signUp, logIn, logOut }
}, { persist: true }) // 새로고침해도 로그인이 유지되도록 설정 (pinia-plugin-persistedstate 설치 필요)