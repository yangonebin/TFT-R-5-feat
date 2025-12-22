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

          <button class="btn-confirm" @click="resetFilters">확인</button>
        </div>
      </aside>

      <main class="main-content">
        <div class="tab-menu">
          <span class="active-tab">정기예금</span>
          <span class="separator">|</span>
          <span class="inactive-tab">정기적금</span>
        </div>

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
              <tr v-for="group in sortedProducts" :key="group.id" @click="goDetail(group.representativeId)">
                <td class="cell-month">202504</td>
                <td class="cell-bank">{{ group.kor_co_nm }}</td>
                <td class="cell-product">{{ group.fin_prdt_nm }}</td>
                <td class="cell-rate">{{ group.rates['6'] || '-' }}</td>
                <td class="cell-rate">{{ group.rates['12'] || '-' }}</td>
                <td class="cell-rate">{{ group.rates['24'] || '-' }}</td>
                <td class="cell-rate">{{ group.rates['36'] || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="sortedProducts.length === 0" class="no-data">
            조건에 맞는 상품이 없습니다.
          </div>
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

const getProducts = () => {
  axios.get(`${store.API_URL}/finlife/deposit/`).then(res => { rawProducts.value = res.data })
}

const bankList = computed(() => [...new Set(rawProducts.value.map(p => p.kor_co_nm))])

const sortedProducts = computed(() => {
  const groups = {}
  let filtered = rawProducts.value.filter(p => 
    (selectedBank.value === 'all' || p.kor_co_nm === selectedBank.value) &&
    (p.fin_prdt_nm.toLowerCase().includes(searchText.value.toLowerCase()))
  )

  filtered.forEach(p => {
    const key = p.kor_co_nm + p.fin_prdt_nm
    if (!groups[key]) {
      groups[key] = { representativeId: p.id, kor_co_nm: p.kor_co_nm, fin_prdt_nm: p.fin_prdt_nm, rates: {} }
    }
    groups[key].rates[p.save_trm] = p.intr_rate2
  })

  let result = Object.values(groups)
  if (selectedPeriod.value !== 'all') {
    result = result.filter(g => g.rates[selectedPeriod.value] !== undefined)
  }
  return result.sort((a, b) => a.kor_co_nm.localeCompare(b.kor_co_nm))
})

const goDetail = (id) => router.push({ name: 'deposit-detail', params: { id } })
const resetFilters = () => { selectedBank.value = 'all'; selectedPeriod.value = 'all'; searchText.value = ''; }
onMounted(getProducts)
</script>

<style scoped>
/* 레이아웃 */
.view-container { max-width: 1300px; margin: 0 auto; padding: 20px; font-family: 'Noto Sans KR', sans-serif; }
.header-banner { background-color: #7aa7d6; color: white; padding: 30px; text-align: center; margin-bottom: 30px; border-radius: 4px; }
.content-wrapper { display: flex; gap: 40px; align-items: flex-start; }

/* 사이드바 스타일 (image_09810a.png) */
.sidebar { width: 260px; flex-shrink: 0; background: white; }
.sidebar-title { font-size: 1.2rem; color: #4a7ab5; margin-bottom: 5px; font-weight: bold; }
.sidebar-subtitle { font-size: 0.9rem; color: #888; margin-bottom: 15px; }
.divider { border: 0; border-top: 1.5px solid #4a7ab5; margin-bottom: 20px; }
.filter-group { margin-bottom: 20px; }
.filter-group label { display: block; font-size: 0.85rem; color: #333; margin-bottom: 8px; font-weight: 500; }
.styled-select, .styled-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 0.9rem; background-color: #fff; }
.btn-confirm { width: 100%; padding: 12px; background-color: #7aa7d6; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-confirm:hover { background-color: #5d8fbf; }

/* 메인 테이블 스타일 (image_0980e8.png) */
.main-content { flex-grow: 1; overflow-x: auto; }
.tab-menu { margin-bottom: 15px; font-size: 1.1rem; }
.active-tab { color: #333; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 2px; }
.inactive-tab { color: #bbb; cursor: pointer; }
.separator { margin: 0 10px; color: #eee; }

table { width: 100%; border-collapse: collapse; min-width: 800px; }
thead th { background-color: #dae8f9; color: #333; padding: 12px; font-size: 0.85rem; border: 1px solid #c8d9ed; }
tbody td { padding: 12px; border: 1px solid #eee; font-size: 0.85rem; text-align: center; color: #555; }
.cell-bank { color: #666; }
.cell-product { text-align: left; padding-left: 20px; color: #333; font-weight: 500; }
.cell-rate { font-weight: bold; color: #444; }
tbody tr:hover { background-color: #f8fbff; cursor: pointer; }
.no-data { padding: 100px; text-align: center; color: #999; }
</style>