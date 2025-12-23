<template>
  <div class="profile-bg">
    <div class="profile-container">
      <h1 class="page-title">내 프로필</h1>

      <div class="profile-grid">
        <aside class="info-sidebar">
          <div class="card user-card">
            <div class="user-avatar">
              <span class="avatar-text">{{ store.user?.username?.charAt(0).toUpperCase() }}</span>
            </div>
            <h2 class="section-title">기본 정보</h2>
            
            <div v-if="!isEditing" class="info-content">
              <div class="info-group">
                <label>아이디</label>
                <div class="info-value">{{ store.user?.username }}</div>
              </div>
              <div class="info-group">
                <label>이메일</label>
                <div class="info-value">{{ store.user?.email || '등록 안 됨' }}</div>
              </div>
              <div class="info-group">
                <label>이름</label>
                <div class="info-value">
                  <template v-if="store.user?.last_name || store.user?.first_name">
                    {{ store.user?.last_name }}{{ store.user?.first_name }}
                  </template>
                  <template v-else>정보 없음</template>
                </div>
              </div>
              <button @click="startEdit" class="btn btn-outline">정보 수정</button>
            </div>

            <div v-else class="info-edit-form">
              <div class="input-group">
                <label>이메일</label>
                <input v-model="editData.email" type="email" placeholder="example@mail.com" />
              </div>
              <div class="input-group-row">
                <div class="input-group">
                  <label>성</label>
                  <input v-model="editData.last_name" type="text" />
                </div>
                <div class="input-group">
                  <label>이름</label>
                  <input v-model="editData.first_name" type="text" />
                </div>
              </div>
              <div class="edit-actions">
                <button @click="updateProfile" class="btn btn-primary">저장하기</button>
                <button @click="isEditing = false" class="btn btn-cancel">취소</button>
              </div>
            </div>
          </div>
        </aside>

        <main class="main-dashboard">
          <div class="card chart-card">
            <h2 class="section-title">가입 상품 금리 분석</h2>
            <div class="chart-wrapper" v-if="joinedProducts.length > 0">
              <Bar :data="chartData" :options="chartOptions" />
            </div>
            <div v-else class="empty-state">
              <p>분석할 금융 상품 데이터가 없습니다.</p>
            </div>
          </div>

          <div class="card list-card">
            <h2 class="section-title inline-title">
              가입한 금융 상품 <span class="count">{{ joinedProducts.length }}</span>
            </h2>
            <div v-if="joinedProducts.length > 0" class="product-grid">
              <div v-for="product in joinedProducts" :key="product.id" class="product-card" @click="goDetail(product.fin_prdt_cd)">
                <div class="bank-info">
                  <span class="bank-tag">{{ product.kor_co_nm }}</span>
                  <h3 class="product-name">{{ product.fin_prdt_nm }}</h3>
                </div>
                <div class="view-detail">상세보기 ➔</div>
              </div>
            </div>
            <div v-else class="empty-list">
              <p>가입한 상품이 없습니다. 나에게 맞는 상품을 찾아보세요.</p>
              <button @click="router.push({ name: 'deposit' })" class="btn btn-primary">상품 보러가기</button>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const store = useAuthStore()
const router = useRouter()
const isEditing = ref(false)
const joinedProducts = ref([])
const editData = ref({ email: '', first_name: '', last_name: '' })

// 유저 정보 변경 감시
watch(() => store.user, (u) => {
  if (u) {
    editData.value = { email: u.email || '', first_name: u.first_name || '', last_name: u.last_name || '' }
  }
}, { immediate: true })

const startEdit = () => { isEditing.value = true }

const updateProfile = () => {
  axios({
    method: 'put',
    url: `${store.API_URL}/accounts/user/`,
    headers: { Authorization: `Bearer ${store.token}` },
    data: editData.value
  })
  .then(res => {
    alert('회원 정보가 수정되었습니다.')
    store.user = res.data 
    isEditing.value = false
  })
  .catch(err => console.error(err))
}

const fetchJoinedProducts = () => {
  axios({
    method: 'get',
    url: `${store.API_URL}/finlife/users/joined-products/`,
    headers: { Authorization: `Bearer ${store.token}` }
  })
  .then(res => joinedProducts.value = res.data)
  .catch(err => console.error(err))
}

const chartData = computed(() => ({
  labels: joinedProducts.value.map(p => p.fin_prdt_nm),
  datasets: [{
    label: '최고 우대 금리(%)',
    backgroundColor: '#339af0',
    borderRadius: 8,
    data: joinedProducts.value.map(p => {
      if (!p.options || p.options.length === 0) return 0
      return Math.max(...p.options.map(o => o.intr_rate2 || 0))
    })
  }]
}))

// ★ 차트 하단 텍스트 정렬 및 말줄임표 처리 옵션
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { display: false },
    tooltip: {
      callbacks: {
        // 툴팁에서는 잘리지 않은 전체 상품명을 보여줌
        title: (items) => joinedProducts.value[items[0].dataIndex].fin_prdt_nm
      }
    }
  },
  scales: { 
    y: { 
      beginAtZero: true, 
      ticks: {
        stepSize: 0.5,
        callback: (value) => value.toFixed(1) + '%'
      },
      grid: { color: '#f0f0f0' } 
    }, 
    x: { 
      grid: { display: false },
      ticks: {
        maxRotation: 0, // 대각선 회전 방지 (0도로 고정)
        minRotation: 0,
        font: { size: 11 },
        // 긴 상품명은 8글자에서 자르고 '...' 추가
        callback: function(value, index) {
          const label = this.getLabelForValue(value);
          return label.length > 8 ? label.substr(0, 8) + '...' : label;
        }
      }
    } 
  }
}

const goDetail = (code) => router.push({ name: 'deposit-detail', params: { fin_prdt_cd: code }})

onMounted(() => {
  if (!store.token) router.push({ name: 'login' })
  else {
    axios.get(`${store.API_URL}/accounts/user/`, {
      headers: { Authorization: `Bearer ${store.token}` }
    }).then(res => store.user = res.data)
    fetchJoinedProducts()
  }
})
</script>

<style scoped>
.profile-bg { background-color: #f8f9fb; min-height: 100vh; padding: 40px 20px; }
.profile-container { max-width: 1200px; margin: 0 auto; }
.page-title { font-size: 2rem; font-weight: 800; color: #1a1a1a; margin-bottom: 40px; }
.profile-grid { display: grid; grid-template-columns: 350px 1fr; gap: 30px; align-items: start; }
.card { background: #fff; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; }

.section-title { font-size: 1.25rem; font-weight: 700; color: #333; margin-bottom: 25px; }
.inline-title { display: flex; align-items: center; gap: 12px; white-space: nowrap; } /* 줄바꿈 방지 */
.section-title .count { font-size: 0.9rem; background: #e7f5ff; color: #339af0; padding: 2px 12px; border-radius: 20px; }

.user-avatar { width: 80px; height: 80px; background: #339af0; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
.avatar-text { font-size: 2rem; color: #fff; font-weight: bold; }
.info-group { margin-bottom: 20px; }
.info-group label { font-size: 0.85rem; color: #888; display: block; margin-bottom: 5px; }
.info-value { font-size: 1.1rem; font-weight: 600; color: #333; }

.input-group { margin-bottom: 15px; }
.input-group label { display: block; font-size: 0.85rem; margin-bottom: 5px; font-weight: bold; }
.input-group input { width: 100%; padding: 12px; border: 1.5px solid #eee; border-radius: 10px; }
.input-group-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.btn { width: 100%; padding: 12px; border-radius: 10px; font-weight: 700; cursor: pointer; border: none; transition: 0.2s; }
.btn-outline { background: transparent; border: 1.5px solid #339af0; color: #339af0; }
.btn-primary { background: #339af0; color: #fff; }
.btn-cancel { background: #f1f3f5; color: #868e96; margin-top: 5px; }

.main-dashboard { display: flex; flex-direction: column; gap: 30px; }
.chart-wrapper { height: 350px; } /* 차트 높이 상향 */

.product-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.product-card { 
  background: #fbfcfe; 
  border: 1.5px solid #f1f3f5; 
  padding: 20px; 
  border-radius: 15px; 
  cursor: pointer; 
  display: flex; 
  flex-direction: column; 
  justify-content: space-between; 
  min-height: 140px; /* 카드 높이 균일화 */
}
.product-card:hover { border-color: #339af0; background: #fff; }
.bank-tag { font-size: 0.75rem; background: #fff; border: 1px solid #ddd; padding: 2px 8px; border-radius: 5px; color: #666; font-weight: bold; align-self: flex-start; }
.product-name { font-size: 1rem; margin-top: 10px; color: #333; font-weight: 600; }
.view-detail { font-size: 0.8rem; color: #339af0; font-weight: bold; margin-top: 15px; }

.empty-state, .empty-list { text-align: center; padding: 40px; color: #adb5bd; }

@media (max-width: 900px) {
  .profile-grid { grid-template-columns: 1fr; }
  .product-grid { grid-template-columns: 1fr; }
}
</style>