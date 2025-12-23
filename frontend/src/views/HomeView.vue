<template>
  <div class="home-view">
    <section class="hero-section">
      <div class="container hero-content">
        <h1 class="hero-title">
          금융의 모든 것,<br />
          <span class="highlight">FinMatch</span>에서 시작하세요.
        </h1>
        <p class="hero-desc">
          예적금 금리 비교부터 AI 맞춤 자산 관리까지.<br />
          당신의 자산을 가장 똑똑하게 불리는 방법.
        </p>
        <div class="hero-buttons">
          <button class="btn-primary" @click="goToRecommendation">내게 맞는 상품 찾기</button>
          <button class="btn-secondary">서비스 소개</button>
        </div>
      </div>
    </section>

    <section class="container services-section">
      <div class="section-header">
        <h2>주요 서비스</h2>
        <p>FinMatch이 제공하는 핵심 기능을 만나보세요</p>
      </div>

      <div class="grid-container">
        <div class="service-card" @click="$router.push({ name: 'deposit' })">
          <div class="icon-box">💰</div>
          <div class="card-text">
            <h3>예적금 비교</h3>
            <p>1금융권부터 저축은행까지<br>최고 금리를 한눈에 비교</p>
          </div>
        </div>

        <div class="service-card" @click="$router.push({ name: 'exchange' })">
          <div class="icon-box">🥇</div>
          <div class="card-text">
            <h3>현물 자산 시세</h3>
            <p>금, 은, 원자재 등<br>실시간 시세 트렌드 확인</p>
          </div>
        </div>

        <div class="service-card" @click="$router.push({ name: 'map' })">
          <div class="icon-box">📍</div>
          <div class="card-text">
            <h3>내 근처 은행</h3>
            <p>위치 기반으로 가장 가까운<br>은행 지점과 ATM 찾기</p>
          </div>
        </div>

        <div class="service-card" @click="$router.push({ name: 'stock' })">
          <div class="icon-box">📈</div>
          <div class="card-text">
            <h3>투자 인사이트</h3>
            <p>관심 종목 뉴스부터<br>전문가 분석 영상까지</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const goToRecommendation = () => {
  console.log('추천 페이지 이동')
}
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.hero-section {

  background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
  
  
  color: white;
  padding: 100px 0;
  margin-bottom: 80px;
}

.hero-content {
  text-align: left; 
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
}

.hero-title .highlight {
  color: #64b5f6; 
}

.hero-desc {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 40px;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 16px;
}

.btn-primary {
  background-color: #3182f6;
  color: white;
  padding: 16px 32px;
  border-radius: 12px;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: #1c6cdb;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  padding: 16px 32px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.services-section {
  padding-bottom: 100px;
}

.section-header {
  margin-bottom: 40px;
  text-align: center;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #111;
  margin-bottom: 10px;
}

.section-header p {
  color: #666;
  font-size: 1.1rem;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr); 
  gap: 24px;
}

/* 반응형 처리 */
@media (max-width: 992px) {
  .grid-container { grid-template-columns: repeat(2, 1fr); }
  .hero-title { font-size: 2.5rem; }
}
@media (max-width: 576px) {
  .grid-container { grid-template-columns: 1fr; }
  .hero-content { text-align: center; }
  .hero-buttons { justify-content: center; }
}

/* Service Card */
.service-card {
  background: white;
  padding: 32px 24px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); 
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  display: flex;
  flex-direction: column;
  align-items: flex-start; 
}

.service-card:hover {
  transform: translateY(-8px); 
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  border-color: #e5e8eb;
}

.icon-box {
  font-size: 2.5rem;
  margin-bottom: 20px;
  background-color: #f0f7ff;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
}

.card-text h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #111;
}

.card-text p {
  font-size: 0.95rem;
  color: #767676;
  line-height: 1.5;
}
</style>