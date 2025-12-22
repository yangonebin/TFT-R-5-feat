<template>
  <div class="detail-container" v-if="product">
    <div class="header">
      <h1>정기예금 상세</h1>
    </div>

    <table class="detail-table">
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
        <td>인터넷, 스마트폰, 전화(텔레뱅킹)</td> </tr>
      <tr>
        <th>우대조건</th>
        <td>해당사항 없음</td> </tr>
      <tr>
        <th>이자율</th>
        <td>
          <div v-for="opt in relatedOptions" :key="opt.id" class="rate-row">
            단리 - 만기기간: {{ opt.save_trm }}개월 / 금리: {{ opt.intr_rate }}% / <strong>최고 우대금리: {{ opt.intr_rate2 }}%</strong>
          </div>
        </td>
      </tr>
    </table>

    <div class="btn-area">
      <button class="btn-join" @click="toggleJoin">가입하기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const store = useAuthStore()
const product = ref(null)
const relatedOptions = ref([])

const fetchData = async () => {
  try {
    // 1. 상세 정보를 가져오기 위해 전체 리스트 조회
    const res = await axios.get(`${store.API_URL}/finlife/deposit/`)
    const all = res.data
    
    // 2. 현재 클릭한 상품 찾기
    const target = all.find(p => p.id === Number(route.params.id))
    if (target) {
      product.value = target
      // 3. 같은 상품의 다른 기간(옵션)들 묶기
      relatedOptions.value = all.filter(p => 
        p.fin_prdt_nm === target.fin_prdt_nm && 
        p.kor_co_nm === target.kor_co_nm
      ).sort((a, b) => Number(a.save_trm) - Number(b.save_trm))
    }
  } catch (err) {
    alert("상품 정보를 가져오지 못했습니다.")
  }
}

onMounted(() => fetchData())
</script>

<style scoped>
.detail-table { width: 100%; border-top: 2px solid #333; border-collapse: collapse; }
.detail-table th { background: #f4f4f4; width: 20%; padding: 15px; border-bottom: 1px solid #ddd; text-align: left; }
.detail-table td { padding: 15px; border-bottom: 1px solid #ddd; }
.rate-row { margin-bottom: 5px; font-size: 0.9em; }
.btn-join { margin-top: 20px; padding: 15px 40px; background: #6ea3d8; color: white; border: none; cursor: pointer; }
</style>