<template>
  <div class="exchange-container">
    <div class="header-banner">
      <h1>현물 가격 변동</h1>
      <p class="subtitle">국제 금/은 시세 트렌드를 한눈에 확인하세요.</p>
    </div>

    <div class="control-panel">
      <div class="toggle-group">
        <button @click="changeAsset('gold')" :class="{ active: asset === 'gold', 'gold-btn': true }">
          <span>🟡 금 (Gold)</span>
        </button>
        <button @click="changeAsset('silver')" :class="{ active: asset === 'silver', 'silver-btn': true }">
          <span>⚪ 은 (Silver)</span>
        </button>
      </div>

      <div class="date-group">
        <div class="input-wrapper">
          <label>시작일</label>
          <input type="date" v-model="startDate" />
        </div>
        <span class="tilde">~</span>
        <div class="input-wrapper">
          <label>종료일</label>
          <input type="date" v-model="endDate" />
        </div>
        <button @click="fetchData" class="btn-search">조회</button>
      </div>
    </div>

    <div class="chart-card">
      <div class="chart-header">
        <h2>{{ asset === 'gold' ? '금' : '은' }} 가격 추이</h2>
        <span class="unit">(단위: USD/troi oz)</span>
      </div>
      <div class="chart-body">
        <Line v-if="loaded" :data="chartData" :options="chartOptions" />
        <div v-else class="loading-container">
          <div class="spinner"></div>
          <p>데이터를 불러오는 중입니다...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement, Filler } from 'chart.js'

// Filler 플러그인 추가 등록 (그라데이션 배경을 위해 필요)
ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement, Filler)

const store = useAuthStore()
const asset = ref('gold')
const startDate = ref('')
const endDate = ref('')
const loaded = ref(false)
const rawPrices = ref([])

// --- 🎨 디자인 설정 영역 ---

// 1. 색상 테마 정의
const theme = computed(() => asset.value === 'gold' ? ({
  borderColor: '#FFD700',    // 밝은 금색
  backgroundColor: '#FFD700', // 포인트 색상
  gradientStart: 'rgba(255, 215, 0, 0.5)', // 그라데이션 시작
  gradientEnd: 'rgba(255, 215, 0, 0.0)'   // 그라데이션 끝
}) : ({
  borderColor: '#C0C0C0',    // 밝은 은색
  backgroundColor: '#C0C0C0', // 포인트 색상
  gradientStart: 'rgba(192, 192, 192, 0.5)',
  gradientEnd: 'rgba(192, 192, 192, 0.0)'
}))

// 2. 차트 데이터 (그라데이션 함수 적용)
const chartData = computed(() => ({
  labels: rawPrices.value.map(item => item.date),
  datasets: [
    {
      label: `${asset.value === 'gold' ? 'Gold' : 'Silver'} Price`,
      data: rawPrices.value.map(item => item.price),
      borderColor: theme.value.borderColor,
      backgroundColor: (context) => {
        const chart = context.chart;
        const {ctx, chartArea} = chart;
        if (!chartArea) return null;
        const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
        gradient.addColorStop(0, theme.value.gradientEnd);
        gradient.addColorStop(1, theme.value.gradientStart);
        return gradient;
      },
      fill: true,           
      tension: 0.4,         
      borderWidth: 3,       
      pointRadius: 0,       // 평소에는 포인트 숨김 (깔끔하게)
      pointHoverRadius: 6,  // 마우스 올렸을 때만 표시
      pointBackgroundColor: theme.value.backgroundColor,
      pointBorderColor: '#fff', 
      pointBorderWidth: 2,
    }
  ]
}))

// 3. 차트 옵션
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',   
    intersect: false, 
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleFont: { size: 14 },
      bodyFont: { size: 14, weight: 'bold' },
      padding: 12,
      displayColors: false,
      callbacks: {
        label: (context) => ` $${Number(context.parsed.y).toLocaleString()}` 
      }
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        maxTicksLimit: 8, 
        color: '#888'
      }
    },
    y: {
      grid: { color: '#eee' },
      ticks: {
        color: '#888',
        callback: (value) => '$' + value.toLocaleString() 
      }
    }
  }
}

// --- 데이터 로직 ---
const fetchData = async () => {
  loaded.value = false
  try {
    const response = await axios.get(`${store.API_URL}/finlife/exchange/`, {
      params: { asset: asset.value, start_date: startDate.value, end_date: endDate.value }
    })
    rawPrices.value = response.data
    loaded.value = true
  } catch (err) {
    console.error(err)
    // alert('데이터 로드 실패') // 에러 메시지 너무 자주 뜨면 주석 처리
    loaded.value = true
  }
}

const changeAsset = (type) => {
  asset.value = type
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
/* 전체 컨테이너 */
.exchange-container {
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더 배너 */
.header-banner {
  text-align: center;
  margin-bottom: 40px;
}
.header-banner h1 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #2c3e50;
  margin-bottom: 10px;
}
.subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
}

/* 컨트롤 패널 */
.control-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 20px 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  margin-bottom: 30px;
  flex-wrap: wrap; 
  gap: 20px;
}

/* 토글 버튼 */
.toggle-group {
  display: flex;
  background: #f0f2f5;
  padding: 5px;
  border-radius: 12px;
}
.toggle-group button {
  border: none;
  background: none;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  color: #7f8c8d;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}
.toggle-group button.active {
  background: #fff;
  color: #2c3e50;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.gold-btn.active { color: #d4af37; }
.silver-btn.active { color: #7f8c8d; }

/* 날짜 그룹 */
.date-group {
  display: flex;
  align-items: flex-end;
  gap: 15px;
}
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.input-wrapper label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2c3e50;
  margin-left: 5px;
}
input[type="date"] {
  padding: 10px 15px;
  border: 2px solid #e0e6ed;
  border-radius: 10px;
  font-size: 1rem;
  color: #2c3e50;
  background: #f9fbfe;
  outline: none;
  transition: border-color 0.3s;
}
input[type="date"]:focus {
  border-color: #3498db;
}
.tilde {
  align-self: center;
  font-weight: bold;
  color: #95a5a6;
  margin-bottom: 5px;
}
.btn-search {
  padding: 12px 30px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  height: 46px; 
}
.btn-search:hover { background: #2980b9; }

/* 차트 카드 */
.chart-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  padding: 30px;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.chart-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}
.unit {
  font-size: 0.9rem;
  color: #95a5a6;
}
.chart-body {
  height: 500px;
  position: relative;
}

/* 로딩 스피너 */
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #95a5a6;
}
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .control-panel { flex-direction: column; align-items: stretch; }
  .toggle-group { justify-content: center; }
  .date-group { flex-direction: column; align-items: stretch; }
  .btn-search { width: 100%; }
  .chart-body { height: 350px; }
}
</style>