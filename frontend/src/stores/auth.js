import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const API_URL = 'http://127.0.0.1:8000'

  const token = ref(null)
  // ✅ [추가 1] 유저 정보를 저장할 변수 만들기
  const user = ref(null) 

  const isLogin = computed(() => token.value !== null)

  const logIn = function (payload) {
    const { username, password } = payload

    axios({
      method: 'post',
      url: `${API_URL}/accounts/login/`,
      data: { username, password }
    })
      .then((res) => {
        // 1. 토큰 저장
        token.value = res.data.access 
        
        // ✅ [추가 2] 유저 정보 저장 (백엔드가 보내준 user 객체)
        // (이게 있어야 게시글 상세페이지에서 내 글인지 확인 가능)
        user.value = res.data.user  
        
        console.log('로그인 성공!')
        console.log('토큰:', token.value)
        console.log('유저:', user.value) // 콘솔에서 유저 정보 확인 가능

        router.push({ name: 'articles' })
      })
      .catch((err) => {
        console.log(err)
        alert('로그인 실패: 아이디와 비밀번호를 확인하세요.')
      })
  }

  const logOut = function () {
    token.value = null
    // ✅ [추가 3] 로그아웃 시 유저 정보도 비우기
    user.value = null 
    router.push({ name: 'login' })
  }

  // ✅ [추가 4] return에 user 포함시키기
  return { API_URL, token, user, isLogin, logIn, logOut }
}, { persist: true })