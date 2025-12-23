<template>
  <div class="view-container">
    <div class="header-banner">
      <h1>예금 비교</h1>
    </div>

    <div class="content-wrapper">
      <aside class="sidebar">
        <div class="search-section">
          <h2 class="sidebar-title">정기예금</h2>
          <p class="sidebar-subtitle">검색 조건을 입력하세요</p>
          <hr class="divider" />
          <div class="filter-group">
            <label>은행을 선택하세요</label>
            <select v-model="selectedBank" class="styled-select">
              <option value="all">전체</option>
              <option v-for="bank in bankList" :key="bank" :value="bank">{{ bank }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>예치기간</label>
            <select v-model="selectedPeriod" class="styled-select">
              <option value="all">전체기간</option>
              <option v-for="period in [6, 12, 24, 36]" :key="period" :value="period">{{ period }}개월</option>
            </select>
          </div>
          <div class="filter-group">
            <label>상품명 검색</label>
            <input type="text" v-model="searchText" class="styled-input" placeholder="상품명을 입력하세요" />
          </div>
          <button class="btn-confirm" @click="resetFilters">초기화</button>
        </div>
      </aside>

      <main class="main-content">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>공시 제출월</th>
                <th>금융회사명</th>
                <th>상품명</th>
                <th>6개월</th>
                <th>12개월</th>
                <th>24개월</th>
                <th>36개월</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in sortedProducts" :key="product.fin_prdt_cd" @click="goDetail(product.fin_prdt_cd)">
                <td>{{ product.dcls_month || '202411' }}</td>
                <td class="cell-bank">{{ product.kor_co_nm }}</td>
                <td class="cell-product">{{ product.fin_prdt_nm }}</td>
                <td class="cell-rate">{{ getRate(product.options, 6) }}</td>
                <td class="cell-rate">{{ getRate(product.options, 12) }}</td>
                <td class="cell-rate">{{ getRate(product.options, 24) }}</td>
                <td class="cell-rate">{{ getRate(product.options, 36) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const store = useAuthStore()
const rawProducts = ref([])
const selectedBank = ref('all')
const selectedPeriod = ref('all')
const searchText = ref('')

const getRate = (options, month) => {
  if (!options || !Array.isArray(options)) return '-'
  const target = options.find(opt => Number(opt.save_trm) === month)
  return target ? target.intr_rate : '-'
}

const getProducts = () => {
  const BASE_URL = store.API_URL || 'http://127.0.0.1:8000'
  axios.get(`${BASE_URL}/finlife/deposit-products/`)
    .then(res => rawProducts.value = res.data)
    .catch(err => console.error(err))
}

const bankList = computed(() => [...new Set(rawProducts.value.map(p => p.kor_co_nm))])

const sortedProducts = computed(() => {
  let filtered = rawProducts.value.filter(p => {
    const isBankMatch = selectedBank.value === 'all' || p.kor_co_nm === selectedBank.value
    const isSearchMatch = p.fin_prdt_nm.toLowerCase().includes(searchText.value.toLowerCase())
    const isPeriodMatch = selectedPeriod.value === 'all' || p.options.some(opt => opt.save_trm === Number(selectedPeriod.value))
    return isBankMatch && isSearchMatch && isPeriodMatch
  })
  return filtered.sort((a, b) => a.kor_co_nm.localeCompare(b.kor_co_nm))
})

// ★★★ [핵심 수정] 상세 이동 함수
const goDetail = (product_cd) => {
  // 값이 없는 경우 차단
  if (!product_cd) {
    alert('상품 코드가 없습니다.')
    return
  }
  
  // 라우터로 이동 (파라미터 이름: fin_prdt_cd)
  router.push({ 
    name: 'deposit-detail', 
    params: { fin_prdt_cd: product_cd } 
  })
}

const resetFilters = () => {
  selectedBank.value = 'all'
  selectedPeriod.value = 'all'
  searchText.value = ''
}

onMounted(getProducts)
</script>

<style scoped>
/* 기존 스타일 유지 */
.view-container { max-width: 1300px; margin: 0 auto; padding: 20px; font-family: 'Noto Sans KR', sans-serif; }
.header-banner { background-color: #7aa7d6; color: white; padding: 30px; text-align: center; margin-bottom: 30px; border-radius: 4px; }
.content-wrapper { display: flex; gap: 40px; align-items: flex-start; }
.sidebar { width: 260px; flex-shrink: 0; background: white; }
.sidebar-title { font-size: 1.2rem; color: #4a7ab5; margin-bottom: 5px; font-weight: bold; }
.sidebar-subtitle { font-size: 0.9rem; color: #888; margin-bottom: 15px; }
.divider { border: 0; border-top: 1.5px solid #4a7ab5; margin-bottom: 20px; }
.filter-group { margin-bottom: 20px; }
.filter-group label { display: block; font-size: 0.85rem; color: #333; margin-bottom: 8px; font-weight: 500; }
.styled-select, .styled-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem; background-color: #fff; }
.btn-confirm { width: 100%; padding: 12px; background-color: #7aa7d6; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.main-content { flex-grow: 1; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 800px; border: 1px solid #ddd; }
thead th { background-color: #dae8f9; color: #333; padding: 12px; font-size: 0.85rem; border: 1px solid #c8d9ed; }
tbody td { padding: 12px; border: 1px solid #eee; font-size: 0.85rem; text-align: center; color: #555; }
tbody tr:hover { background-color: #f8fbff; cursor: pointer; }
.cell-bank { color: #666; font-weight: bold; }
.cell-product { text-align: left; padding-left: 20px; color: #333; font-weight: 500; }
.cell-rate { font-weight: bold; color: #4a7ab5; }
</style>