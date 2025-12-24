💰 FinMatch (핀매치)

스마트한 자산 관리부터 AI 주가 예측까지, All-in-One 금융 플랫폼

1. 👨‍💻 팀원 정보 및 역할 분담

👑 장영철 (Team Leader)

Full Stack Frontend Lead Core Backend

영역

상세 담당 업무

Frontend

• Vue 3 기반 전체 아키텍처 설계 및 공통 컴포넌트 개발



• Pinia 상태 관리 및 Axios 모듈화 구조 설계



• UI/UX: 메인, 프로필, 커뮤니티 페이지 반응형 디자인 구현

Backend

• Django 서버 초기 구축 및 DB ERD 설계



• JWT 기반 회원가입/로그인(Auth) 시스템 구현

Visualization

• Kakao Maps API 연동 (주변 은행 찾기, 마커 클러스터링)



• Chart.js 활용 포트폴리오 시각화

🧠 양한빈 (Team Member)

AI Researcher Backend Data Engineer

영역

상세 담당 업무

AI Modeling

• SOTA 주가 예측 모델(TFT-R) 개발 및 고도화



• 노이즈 제거를 위한 VSN(Variable Selection Network) 구현

MLOps

• FastAPI 기반 실시간 AI 추론(Inference) 마이크로서비스 구축



• MLflow를 활용한 실험 추적 및 모델 버전 관리

Data Eng.

• yfinance 대용량 시계열 데이터(20년치) 전처리 파이프라인 구축



• 금융감독원 예적금 API 및 환율 데이터 파싱 로직 구현

2. 🛠 기술 스택 (Tech Stack)

Frontend

Backend & Database

AI & MLOps

3. 🌟 핵심 기능 (Key Features)

📈 AI 주가 예측 (TFT-R Engine)

"단순한 예측을 넘어, 시장의 맥락을 읽다"

실시간 예측: 사용자가 조회하는 즉시 최신 데이터를 수집하여 향후 등락률 예측

직관적 시그널: 복잡한 수치 대신 강력 매수, 보유, 매도 등 명확한 액션 가이드 제공

근거 제시: 최근 20일간의 차트 흐름과 AI가 분석한 추세선 시각화

🏦 금융 상품 원스톱 관리

예적금 비교: 1금융권 및 저축은행의 모든 상품을 금리순/기간별로 비교

하이브리드 추천: 내 정보(나이, 자산)와 유사한 유저들이 선택한 상품 추천 (Collaborative Filtering)

AI 챗봇 상담: "사회초년생을 위한 공격적인 투자 상품 추천해줘"와 같은 자연어 질의 응답

🗺 위치 기반 은행 찾기

스마트 검색: 내 주변 은행 및 ATM 위치를 지도 위에 마커로 표시

경로 안내: 현재 위치에서 선택한 은행까지의 최적 이동 경로 시각화 (Kakao Mobility)

4. 🧠 AI 알고리즘 상세 (Technical Deep Dive)

본 프로젝트는 단순 시계열 모델(LSTM)의 한계를 넘어, Temporal Fusion Transformer (TFT) 아키텍처를 주가 예측에 도입했습니다.

🏗 모델 아키텍처

VSN (Variable Selection Network)

문제: 환율, 금리 등 14개의 거시경제 변수가 오히려 노이즈로 작용함.

해결: AI가 스스로 가격 결정에 중요한 **5개 핵심 피처(OHLCV)**만 선별하여 학습 효율 극대화.

Multi-Head Attention

기능: 과거 20일 데이터 중, 현재 주가 형성에 결정적인 영향을 미친 '골든 타임'을 포착하여 가중치 부여.

성과 (Simulation Result)

평균 ROI: 103.68%

최고 ROI: 292.45%

결론: 노이즈를 제거한 5-Feature 회귀 모델이 복잡한 모델보다 압도적인 성능 발휘.

5. 💬 프로젝트 회고 (Retrospective)

장영철 (팀장)

"프론트엔드부터 백엔드까지 전체 흐름을 주도하며 풀스택 개발자로서의 가능성을 확인했습니다. 특히 Vue 3의 컴포넌트 재사용성을 극대화하고, Django와의 비동기 통신을 최적화하는 과정에서 많은 성장을 이뤘습니다. 지도 API와 차트 라이브러리를 다루며 데이터 시각화의 중요성을 깊이 체감했습니다."

양한빈 (팀원) - [데이터 사이언티스트의 양심]

"초기에는 복잡한 모델이 무조건 좋을 것이라 믿고 수많은 변수를 넣었습니다. 하지만 우연한 실수로 돌려본 '단순한 모델'이 100% 이상의 수익률을 내는 것을 보고 충격을 받았습니다.

기존에 준비했던 보고서를 엎어야 했지만, **'기술적 고집보다 데이터가 보여주는 진실을 따르는 것이 엔지니어의 양심'**임을 깨닫고 과감히 모델을 피벗(Pivot)했습니다. 화려한 알고리즘보다 정제된 데이터의 힘이 강력함을 증명한 뜻깊은 프로젝트였습니다."

실행화면 ![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-5.png)
![alt text](image-6.png)
![alt text](image-7.png)
![alt text](image-8.png)
![alt text](image-9.png)