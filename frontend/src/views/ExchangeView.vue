<template>
  <div class="container">
    <h1 class="page-title">환율 및 현물 자산</h1>
    
    <div class="tabs">
      <button 
        :class="{ active: currentTab === 'currency' }" 
        @click="currentTab = 'currency'"
      >
        💱 환율 계산기
      </button>
      <button 
        :class="{ active: currentTab === 'metal' }" 
        @click="currentTab = 'metal'"
      >
        🥇 금/은 시세
      </button>
    </div>

    <div v-if="currentTab === 'currency'" class="content-box">
      <h2>환율 계산기</h2>
      <div class="calculator">
        <div class="input-group">
          <label>대한민국 원 (KRW)</label>
          <input type="number" v-model="krwAmount" placeholder="금액 입력">
        </div>
        <div class="icon">=</div>
        <div class="input-group">
          <label>미국 달러 (USD)</label>
          <input type="text" :value="usdAmount" readonly>
        </div>
      </div>
      <p class="info-text">* 현재 환율: 1 USD = 1,350 KRW (예시 데이터)</p>
    </div>

    <div v-if="currentTab === 'metal'" class="content-box">
      <h2>국제 금/은 시세</h2>
      <div class="metal-grid">
        <div class="metal-card gold">
          <div class="metal-icon">👑</div>
          <h3>Gold (금)</h3>
          <p class="price">$2,050.50 <span>/ oz</span></p>
          <p class="change up">▲ 1.2%</p>
        </div>
        <div class="metal-card silver">
          <div class="metal-icon">🥈</div>
          <h3>Silver (은)</h3>
          <p class="price">$24.80 <span>/ oz</span></p>
          <p class="change down">▼ 0.5%</p>
        </div>
      </div>
      <p class="info-text">* 백엔드 데이터 연동 후 실시간 차트가 표시될 영역입니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const currentTab = ref('currency')
const krwAmount = ref(0)
const exchangeRate = 1350 // 임시 환율

const usdAmount = computed(() => {
  return (krwAmount.value / exchangeRate).toFixed(2)
})
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: #154580;
  margin-bottom: 40px;
}

/* 탭 스타일 */
.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
}

.tabs button {
  padding: 12px 30px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.tabs button.active {
  background-color: #154580;
  color: white;
  border-color: #154580;
}

/* 박스 스타일 */
.content-box {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}

.content-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

/* 계산기 스타일 */
.calculator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.input-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1.2rem;
  width: 150px;
  text-align: right;
}

.icon {
  font-size: 2rem;
  color: #999;
}

/* 금/은 카드 스타일 */
.metal-grid {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.metal-card {
  flex: 1;
  max-width: 250px;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  background: #f8f9fa;
  border: 1px solid #eee;
}

.metal-card.gold { background: #fffbf0; border-color: #fceeb5; }
.metal-card.silver { background: #f5f7fa; border-color: #e2e8f0; }

.metal-icon { font-size: 3rem; margin-bottom: 10px; }
.price { font-size: 1.5rem; font-weight: 700; margin: 10px 0; }
.price span { font-size: 0.9rem; font-weight: 400; color: #777; }

.change.up { color: #e11d48; font-weight: 600; }
.change.down { color: #3b82f6; font-weight: 600; }

.info-text {
  text-align: center;
  color: #999;
  font-size: 0.9rem;
  margin-top: 30px;
}
</style>