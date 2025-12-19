<template>
  <div class="product-container">
    <h1>💰 예적금 금리 비교</h1>
    
    <div class="filter-section">
      <label for="bank-select">은행 선택: </label>
      <select id="bank-select" v-model="selectedBank" class="bank-select">
        <option value="all">전체 보기</option>
        <option v-for="bank in bankList" :key="bank" :value="bank">
          {{ bank }}
        </option> </select>
    </div>

    <div class="product-list">
      <table>
        <thead>
          <tr>
            <th>공시 제출월</th>
            <th>금융 회사명</th>
            <th>상품명</th>
            <th>기본 금리</th>
            <th>최고 우대 금리</th>
            <th>기간</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in filteredProducts" :key="product.id">
            <td>2024.05</td>
            <td>{{ product.kor_co_nm }}</td>
            <td class="product-name">{{ product.fin_prdt_nm }}</td>
            <td class="rate">{{ product.intr_rate }}%</td>
            <td class="max-rate">{{ product.intr_rate2 }}%</td>
            <td>{{ product.save_trm }}개월</td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredProducts.length === 0" class="no-data">
        해당하는 상품이 없습니다.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const products = ref([]) // 전체 상품 리스트
const selectedBank = ref('all') // 선택된 은행 이름

// 1. Django에서 데이터 가져오기
const getProducts = () => {
  axios({
    method: 'get',
    // ⚠️ 중요: 백엔드 URL이 정확한지 확인하세요! (finlife 앱을 만들었다면 아래가 맞습니다)
    url: 'http://127.0.0.1:8000/finlife/products/' 
  })
  .then((res) => {
    products.value = res.data
  })
  .catch((err) => console.log(err))
}

// 2. 은행 목록 추출 (중복 제거)
const bankList = computed(() => {
  const banks = products.value.map(product => product.kor_co_nm)
  return [...new Set(banks)] // Set을 이용해 중복 제거
})

// 3. 필터링된 상품 리스트 계산
const filteredProducts = computed(() => {
  if (selectedBank.value === 'all') {
    return products.value
  }
  return products.value.filter(product => product.kor_co_nm === selectedBank.value)
})

onMounted(() => {
  getProducts()
})
</script>

<style scoped>
.product-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.filter-section {
  margin-bottom: 20px;
  text-align: right;
}

.bank-select {
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #ddd;
}

table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  background-color: white; /* 배경색 추가 */
}

th, td {
  padding: 12px 15px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #495057;
}

.product-name {
  font-weight: bold;
  color: #333;
}

.rate {
  color: #3182f6;
}

.max-rate {
  color: #e03131;
  font-weight: bold;
}

tr:hover {
  background-color: #f1f3f5;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #888;
}
</style>