<template>
  <div class="detail-container">
    <h1>상품 상세 정보</h1>
    
    <div v-if="product">
      <div class="product-info">
        <div class="info-row">
          <span class="label">금융회사명</span>
          <span class="value">{{ product.kor_co_nm }}</span>
        </div>
        <div class="info-row">
          <span class="label">상품명</span>
          <span class="value">{{ product.fin_prdt_nm }}</span>
        </div>
        <div class="info-row">
          <span class="label">가입방법</span>
          <span class="value">{{ product.join_way || '영업점 방문' }}</span>
        </div>
        <div class="info-row">
          <span class="label">우대조건</span>
          <span class="value pre-line">{{ product.spcl_cnd || '없음' }}</span>
        </div>
      </div>

      <hr class="divider">

      <div class="options-area">
        <h3>금리 정보</h3>
        <table>
          <thead>
            <tr>
              <th>저축 기간</th>
              <th>저축 금리 유형</th>
              <th>기본 금리</th>
              <th>최고 우대 금리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="opt in product.options" :key="opt.id">
              <td>{{ opt.save_trm }}개월</td>
              <td>{{ opt.intr_rate_type_nm }}</td>
              <td>{{ opt.intr_rate }}%</td>
              <td>{{ opt.intr_rate2 }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="btn-area">
        <button v-if="store.isLogin" @click="joinDeposit" class="join-btn">가입하기</button>
        <p v-else class="login-msg">가입하려면 로그인이 필요합니다.</p>
      </div>

      <div class="back-btn-area">
        <button @click="router.go(-1)" class="back-btn">목록으로 돌아가기</button>
      </div>
    </div>

    <div v-else class="loading">
      <p>상품 정보를 불러오는 중입니다...</p>
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
const product = ref(null)

// 1. 상세 정보 가져오기
const fetchProduct = () => {
  const BASE_URL = store.API_URL || 'http://127.0.0.1:8000'
  const productCode = route.params.fin_prdt_cd
  
  axios.get(`${BASE_URL}/finlife/deposit-products/${productCode}/`)
    .then(res => {
      product.value = res.data
    })
    .catch(err => {
      console.error(err)
      alert('상품 정보를 불러오지 못했습니다.')
    })
}

// 2. 가입하기
const joinDeposit = () => {
  if (!confirm('이 상품에 가입하시겠습니까?')) return

  const BASE_URL = store.API_URL || 'http://127.0.0.1:8000'
  const productCode = route.params.fin_prdt_cd

  // 토큰이 없으면 로그인 페이지로
  if (!store.token) {
    alert('로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }

  axios({
    method: 'post',
    url: `${BASE_URL}/finlife/join/${productCode}/`,
    headers: {
      // ★★★ [수정 완료] Token -> Bearer로 변경했습니다!
      Authorization: `Bearer ${store.token}`
    }
  })
    .then(() => {
      alert('상품 가입이 완료되었습니다!')
    })
    .catch(err => {
      console.error(err)
      if (err.response && err.response.status === 400) {
        alert('이미 가입된 상품입니다.')
      } else if (err.response && err.response.status === 401) {
        // 토큰 방식이 안 맞거나 진짜 만료된 경우
        alert('로그인 정보가 만료되었습니다. 로그아웃 후 다시 로그인해주세요.')
      } else {
        alert('가입 처리 중 오류가 발생했습니다.')
      }
    })
}

onMounted(() => {
  fetchProduct()
})
</script>

<style scoped>
.detail-container { max-width: 900px; margin: 40px auto; padding: 20px; font-family: 'Noto Sans KR', sans-serif; }
.product-info { background: #f8f9fa; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
.info-row { display: flex; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.label { width: 120px; font-weight: bold; color: #555; }
.options-area h3 { margin-bottom: 15px; color: #333; }
table { width: 100%; border-collapse: collapse; border: 1px solid #ddd; text-align: center; }
th { background: #e9ecef; padding: 10px; }
td { padding: 10px; border-top: 1px solid #ddd; }
.btn-area, .back-btn-area { margin-top: 30px; text-align: center; }
.join-btn { background-color: #339af0; color: white; border: none; padding: 15px 40px; border-radius: 8px; font-size: 1.1rem; cursor: pointer; }
.back-btn { background-color: #868e96; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 10px; }
.loading { text-align: center; margin-top: 50px; color: #888; }
</style>