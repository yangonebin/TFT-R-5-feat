<template>
  <div class="container">
    <h1 class="page-title">삼성전자 AI 주가 예측</h1>
    
    <div class="prediction-wrapper">
      <div class="card">
        <div class="card-header">
          <div class="stock-info">
            <span class="stock-code">005930.KS</span>
            <h2>삼성전자</h2>
          </div>
          <div class="badge">실시간 분석 중</div>
        </div>

        <div class="card-body">
          <p class="description">
            최근 20일간의 시가/고가/저가/종가/거래량 데이터를 분석하여<br>
            <strong>내일의 종가 등락</strong>을 예측합니다.
          </p>

          <div v-if="prediction" class="result-box" :class="prediction.signal">
            <div class="signal-icon">
              {{ prediction.signal === 'BUY' ? '🔥' : '❄️' }}
            </div>
            <div class="signal-text">
              {{ prediction.signal === 'BUY' ? '매수 추천 (BUY)' : '관망 추천 (HOLD)' }}
            </div>
            <div class="return-rate">
              예상 수익률 <span class="percent">{{ prediction.predicted_return }}</span>
            </div>
            <p class="timestamp">분석 기준: {{ new Date().toLocaleString() }}</p>
          </div>

          <div v-else-if="isLoading" class="loading-box">
            <div class="spinner"></div>
            <p>Yahoo Finance에서 데이터를 수집하고 분석 중입니다...</p>
          </div>

          <div v-else class="empty-box">
            <p>아래 버튼을 눌러 AI 분석을 시작하세요.</p>
          </div>

          <p v-if="errorMsg" class="error-msg">⚠️ {{ errorMsg }}</p>
        </div>

        <div class="card-footer">
          <button @click="fetchPrediction" :disabled="isLoading" class="predict-btn">
            {{ isLoading ? 'AI 분석 중...' : '예측 실행하기' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 상태 변수
const prediction = ref(null)
const isLoading = ref(false)
const errorMsg = ref('')

// API 호출 함수
const fetchPrediction = async () => {
  isLoading.value = true
  errorMsg.value = ''
  prediction.value = null

  try {
    // FastAPI 서버 주소 (포트 8000번 확인)
    const response = await axios.get('http://localhost:8001/predict')
    
    if (response.data.status === 'success') {
      prediction.value = response.data.result
    } else {
      errorMsg.value = '예측 데이터를 가져오지 못했습니다.'
    }
  } catch (error) {
    console.error(error)
    errorMsg.value = '서버 연결 실패: 백엔드(FastAPI)가 켜져 있는지 확인해주세요.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 기존 스타일 변수 및 레이아웃 상속 */
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary, #154580);
  margin-bottom: 40px;
}

.prediction-wrapper {
  display: flex;
  justify-content: center;
}

.card {
  background: white;
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  overflow: hidden;
  border: 1px solid #eee;
}

.card-header {
  background: var(--color-primary, #154580);
  color: white;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-info h2 {
  margin: 0;
  font-size: 1.8rem;
}

.stock-code {
  opacity: 0.8;
  font-size: 0.9rem;
  display: block;
  margin-bottom: 4px;
}

.badge {
  background: rgba(255,255,255,0.2);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.card-body {
  padding: 40px;
  text-align: center;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 30px;
}

/* 결과 박스 스타일 */
.result-box {
  background: #f8f9fa;
  width: 100%;
  padding: 30px;
  border-radius: 16px;
  animation: fadeIn 0.5s ease;
}

.result-box.BUY {
  background: #fff0f0;
  border: 2px solid #ff6b6b;
  color: #d63031;
}

.result-box.HOLD {
  background: #f0f8ff;
  border: 2px solid #3182f6;
  color: #154580;
}

.signal-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.signal-text {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.percent {
  font-size: 1.4rem;
  font-weight: 800;
}

.timestamp {
  margin-top: 15px;
  font-size: 0.8rem;
  color: #999;
}

/* 로딩 애니메이션 */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--color-primary-light, #3182f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-msg {
  color: #e74c3c;
  margin-top: 10px;
  font-weight: 600;
}

.card-footer {
  padding: 20px 40px 40px;
}

.predict-btn {
  width: 100%;
  padding: 18px;
  background-color: var(--color-primary-light, #3182f6);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.predict-btn:hover:not(:disabled) {
  background-color: #1b64da;
  transform: translateY(-2px);
}

.predict-btn:disabled {
  background-color: #a0c0f0;
  cursor: not-allowed;
}
</style>