<template>
  <div class="view-container">
    <div class="header-banner">
     
    </div>

    <div class="detail-wrapper" v-if="product">
      <h2 class="detail-title">정기예금 상세</h2>
      
      <table class="detail-table">
        <tbody>
          <tr><th>공시 제출월</th><td>{{ product.dcls_month || '202504' }}</td></tr>
          <tr><th>금융회사명</th><td>{{ product.kor_co_nm }}</td></tr>
          <tr><th>상품명</th><td>{{ product.fin_prdt_nm }}</td></tr>
          <tr><th>가입제한</th><td>{{ product.join_deny === '1' ? '제한없음' : '제한있음' }}</td></tr>
          <tr><th>가입방법</th><td>{{ product.join_way }}</td></tr>
          <tr><th>우대조건</th><td>{{ product.spcl_cnd }}</td></tr>
          <tr>
            <th>이자율</th>
            <td>
              <div v-for="opt in product.options" :key="opt.save_trm" class="rate-item">
                {{ opt.intr_rate_type_nm }} - 저축기간: {{ opt.save_trm }}개월 / 금리: {{ opt.intr_rate }}% / 최고 우대금리: {{ opt.intr_rate2 }}%
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="action-section" v-if="store.isLogin">
        <button class="btn-join" @click="joinProduct">가입하기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const store = useAuthStore()
const product = ref(null)

// 1. 상세 데이터 가져오기 (목록에서 넘겨받은 ID 사용)
onMounted(() => {
  axios.get(`${store.API_URL}/finlife/deposit/`)
    .then(res => {
      // 전체 리스트 중 현재 ID와 일치하는 상품 검색
      product.value = res.data.find(p => p.fin_prdt_cd === route.params.id)
    })
})

// 2. 가입하기 로직 (F03-3)
const joinProduct = () => {
  axios({
    method: 'post',
    url: `${store.API_URL}/finlife/join/${product.value.fin_prdt_cd}/`,
    headers: {
      Authorization: `Token ${store.token}`
    }
  })
  .then(() => alert('가입 목록에 추가되었습니다.'))
  .catch(err => alert(err.response.data.message || '이미 가입된 상품입니다.'))
}
</script>

<style scoped>
.detail-wrapper { max-width: 900px; margin: 0 auto; background: white; padding: 20px; }
.detail-title { text-align: center; margin-bottom: 20px; font-weight: bold; }
.detail-table { width: 100%; border-collapse: collapse; border-top: 2px solid #7aa7d6; }
.detail-table th { width: 20%; background: #f9fbfd; padding: 15px; border-bottom: 1px solid #eee; text-align: left; }
.detail-table td { padding: 15px; border-bottom: 1px solid #eee; line-height: 1.6; }
.rate-item { margin-bottom: 5px; font-size: 0.9rem; }
.action-section { text-align: center; margin-top: 30px; }
.btn-join { padding: 12px 40px; background: #7aa7d6; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
</style>