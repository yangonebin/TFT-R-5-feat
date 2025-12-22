<template>
  <div class="view-container">
    <div class="header-banner">
      <h1>예금비교</h1>
    </div>

    <div class="content-wrapper" v-if="product">
      <h2 class="detail-title">정기예금 상세</h2>
      
      <div class="info-card">
        <table class="detail-table">
          <tbody>
            <tr>
              <th>공시제출월</th>
              <td>202504</td>
            </tr>
            <tr>
              <th>금융회사명</th>
              <td>{{ product.kor_co_nm }}</td>
            </tr>
            <tr>
              <th>상품명</th>
              <td>{{ product.fin_prdt_nm }}</td>
            </tr>
            <tr>
              <th>가입방법</th>
              <td>인터넷, 스마트폰, 전화(텔레뱅킹)</td>
            </tr>
            <tr>
              <th>우대조건</th>
              <td>해당사항 없음</td>
            </tr>
            <tr>
              <th>이자율</th>
              <td class="rates-column">
                <div v-for="opt in relatedOptions" :key="opt.id" class="rate-row">
                  단리 - 만료기간: <strong>{{ opt.save_trm }}개월</strong> / 
                  금리: {{ opt.intr_rate }}% / 
                  최고 우대금리: <span class="highlight">{{ opt.intr_rate2 }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="action-bar" v-if="store.token">
        <button class="btn-join" @click="joinProduct">가입하기</button>
      </div>
    </div>

    <div v-else class="status-message">
      <p>정보를 불러오는 중입니다...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const store = useAuthStore()
const product = ref(null)
const relatedOptions = ref([])

const getDetailData = async () => {
  try {
    // 1. 전체 리스트를 가져와서 필터링 (가장 안전한 방법)
    const res = await axios.get(`${store.API_URL}/finlife/deposit/`)
    const allData = res.data
    
    // 2. 현재 URL 파라미터로 넘어온 ID와 일치하는 상품 찾기
    const targetId = Number(route.params.id)
    const targetProduct = allData.find(p => p.id === targetId)
    
    if (targetProduct) {
      product.value = targetProduct
      // 3. 동일한 은행명과 상품명을 가진 모든 옵션(기간별)을 찾아서 기간순 정렬
      relatedOptions.value = allData.filter(p => 
        p.kor_co_nm === targetProduct.kor_co_nm && 
        p.fin_prdt_nm === targetProduct.fin_prdt_nm
      ).sort((a, b) => Number(a.save_trm) - Number(b.save_trm))
    } else {
      console.error("해당 상품을 찾을 수 없습니다.")
    }
  } catch (err) {
    console.error("데이터 로드 실패:", err)
  }
}

// 가입하기 버튼 클릭 시
const joinProduct = () => {
  axios({
    method: 'post',
    url: `${store.API_URL}/finlife/deposit/${product.value.id}/join/`,
    headers: { Authorization: `Token ${store.token}` }
  })
  .then(res => {
    alert(res.data.message)
  })
  .catch(err => {
    alert("가입 처리에 실패했습니다.")
  })
}

onMounted(() => {
  getDetailData()
})
</script>

<style scoped>
.view-container { max-width: 1200px; margin: 0 auto; padding-bottom: 50px; font-family: 'Noto Sans KR', sans-serif; }
.header-banner { background-color: #7aa7d6; color: white; padding: 30px; text-align: center; margin-bottom: 30px; }
.content-wrapper { padding: 0 40px; }
.detail-title { text-align: center; margin-bottom: 30px; font-weight: bold; font-size: 1.5rem; }

.detail-table { width: 100%; border-collapse: collapse; border-top: 2px solid #eee; }
.detail-table th { background-color: #f9f9f9; width: 20%; padding: 15px; text-align: left; border-bottom: 1px solid #eee; color: #333; font-weight: bold; }
.detail-table td { padding: 15px; border-bottom: 1px solid #eee; color: #555; font-size: 0.95rem; line-height: 1.6; }

.rates-column { padding-top: 10px; padding-bottom: 10px; }
.rate-row { margin-bottom: 8px; }
.highlight { color: #d32f2f; font-weight: bold; }

.action-bar { margin-top: 40px; text-align: center; }
.btn-join { background-color: #7aa7d6; color: white; border: none; padding: 15px 60px; font-size: 1.1rem; border-radius: 4px; cursor: pointer; transition: 0.2s; }
.btn-join:hover { background-color: #5d8fbf; }

.status-message { text-align: center; padding: 100px; color: #999; }
</style>