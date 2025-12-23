import os
# 윈도우 환경에서 텐서플로우 멈춤/충돌 방지용 환경변수 설정 (가장 먼저 실행)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import yfinance as yf
import pandas as pd
import warnings
from sklearn.preprocessing import MinMaxScaler  
import numpy as np
import mlflow
import mlflow.keras
import tensorflow as tf 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore', category=FutureWarning)

def build_data_mart():
    print("="*50)
    print(" [Step 1] 데이터 수집 및 마트 구축 시작...")
    print("="*50)
    
    target_stock = "005930.KS"  # 삼성전자 코드
    # 거시경제 지표를 딕셔너리에 담음.
    macro_symbols = { 
        "USD_KRW": "KRW=X", # 원/달러 환율
        "Gold": "GC=F", # 금 선물 가격
        "Interest_Rate": "^TNX" # 미국 10년 만기 국채 수익률
    }

    # AI가 학습할 때, 단순한 종가 정보뿐만 아니라 {환율, 금, 금리}가 이럴 때 종가가 어떻더라. 거시경제 피쳐를 추가하고자 했음.  

    # 1. 주가 데이터 다운로드 (period="max" 적용)
    # start/end 대신 period="max"를 사용하여 상장일부터 전 기간 수집
    # 하지만 온전한 상장일로부터 데이터를 제공받지 못하고 대한민국 주가 정보들은 yfinace에서 주로 2000년 초반부터 제공해줌. 하지만 5000거래일 이상이라 충분할 것이라 판단함. 
    # atuo_adjust는 액면분할이나 배당락 보정
    # progress는 yfinace의 진행상태 터미널에 표시 
    df_raw = yf.download(target_stock, period="max", auto_adjust=True, progress=False)

    # yfinace는 MultiIndex이기 때문에 level이 0인 값만 출력
    # 예 : (Level 0) | Date | Adj Close | Close | High | Low | Open | Volume | 
    #      (Level 1) | 005930.KS | 005930.KS | 005930.KS | 005930.KS | 005930.KS | 005930.KS |  <- 이 부분을 제거하고자 함.
    #      (value)   | 2024-12-18 | 55000 | 55000 | 55500 | 54000 | 54500 | 15000000 |
    if isinstance(df_raw.columns, pd.MultiIndex):
        df_raw.columns = df_raw.columns.get_level_values(0)
    
    # 상장일 확인 로그
    first_date = df_raw.index[0].strftime('%Y-%m-%d')
    print(f"({first_date})부터 데이터를 수집했습니다.")

    # 깊은 복사 True가 defalut임
    df = df_raw[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # 2. 거시 경제 데이터 통합 (주가 데이터 기간에 맞춤)
    for name, symbol in macro_symbols.items():
        print(f"📡 {name} 데이터 수집 중...")
        # 거시 데이터도 가급적 max로 가져온 뒤 주가 데이터와 Join
        macro_raw = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        
        if isinstance(macro_raw.columns, pd.MultiIndex):
            macro_raw.columns = macro_raw.columns.get_level_values(0)
            
        df[name] = macro_raw['Close']

    # 결측치 처리 (앞날의 데이터를 가져오는게 합리적이라 판단)
    df = df.ffill()

    print("="*50)
    print(" [Step 2] 일목균형표 피처 엔지니어링 시작...")
    print("="*50)

    # 전환선 (Tenkan-sen): (9일간 최고가 + 9일간 최저가) / 2
    # rolling은 슬라이딩 윈도우 기법
    nine_high = df['High'].rolling(window=9).max()
    nine_low = df['Low'].rolling(window=9).min()
    df['tenkan_sen'] = (nine_high + nine_low) / 2

    # 기준선 (Kijun-sen): (26일간 최고가 + 26일간 최저가) / 2
    twenty_six_high = df['High'].rolling(window=26).max()
    twenty_six_low = df['Low'].rolling(window=26).min()
    df['kijun_sen'] = (twenty_six_high + twenty_six_low) / 2

    # 선행스팬 A: (전환선 + 기준선) / 2 -> 26일 뒤로 보냄
    # 모델이 오늘 시점에서 '미래의 구름대'를 참조하기 위해 shift(26)
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

    # 선행스팬 B: (52일간 최고가 + 52일간 최저가) / 2 -> 26일 뒤로 보냄
    fifty_two_high = df['High'].rolling(window=52).max()
    fifty_two_low = df['Low'].rolling(window=52).min()
    df['senkou_span_b'] = ((fifty_two_high + fifty_two_low) / 2).shift(26)

    # 3. 파생 변수 (비즈니스 로직)
    # 구름대 두께 : 지금 벽이 얼마나 두꺼운지!
    df['cloud_thickness'] = df['senkou_span_a'] - df['senkou_span_b']
    # 기준선 이격도 : 현재 과매수/과매도 상태인가? 
    df['dist_from_kijun'] = df['Close'] - df['kijun_sen']

    # 4. Target(정답지) 생성: 회귀(Regression) 모델을 위한 다중 타겟 설정
    
    # [Target 1] 내일의 실제 종가 (Price Regression용)
    # shift(-1)을 사용하여 내일의 종가를 오늘 행으로 가져옴.
    df['target_price'] = df['Close'].shift(-1)

    # [Target 2] 내일의 등락률 (Return Regression용)
    # (내일 종가 / 오늘 종가) - 1 공식을 사용하여 변동 비율을 계산
    # 예: 오늘 100원 -> 내일 105원인 경우 0.05 (5%)가 기록됨
    df['target_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    # 결측치가 있는 행(초반 52일치 및 타겟값이 없는 마지막 행) 제거 후 저장
   # 결측치 제거 (스케일링 전에 깨끗한 데이터를 만듭니다)
    df = df.dropna()
    print('피처 엔지니어링 완료!')
    print("="*50)
    print(" [Step 3] 데이터 스케일링 시작 (MinMaxScaler)")
    print("="*50)

    # 1) 스케일링 대상 피처(X)와 정답지(y) 분리.
    # target_price와 target_return은 나중에 결과 확인을 위해 원본을 유지하거나 별도로 처리.
    feature_cols = [
        'Open', 'High', 'Low', 'Close', 'Volume', 
        'USD_KRW', 'Gold', 'Interest_Rate',
        'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b',
        'cloud_thickness', 'dist_from_kijun'
    ]

    target_col = ['target_price']
    all_cols = feature_cols + ['target_price']
    scalers = {}

    for col in all_cols:
        s = MinMaxScaler()
        # 각 컬럼을 독립적으로 피팅하고 변환
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s # 나중에 역산을 위해 보관

    print(f"총 {len(scalers)}개의 독립 스케일러 생성 및 적용 완료")
    
    # 5. 최종 데이터 저장
    df.to_csv("samsung.csv")
    
    print(f"스케일링 완료 및 데이터 마트 생성 완료! (총 {len(df)}개 행)")
    return df, scalers # 나중에 예측값을 복원하기 위해 scalers도 return
    

def create_sequences(df, window_size=20):
    print("="*50)
    print(f" [Step 4] 시퀀스 데이터 생성 시작 (Window Size: {window_size})")
    print("="*50)

    X = [] # 입력 데이터 (과거 20일치 피처들)
    y_price = [] # 정답지 1 (내일의 가격)
    y_return = [] # 정답지 2 (내일의 수익률)

    # 전체 데이터에서 window_size만큼씩 슬라이딩하며 덩어리 생성
    # 피처 컬럼들만 추출 (target_price, target_return 제외)
    feature_cols = [col for col in df.columns if 'target' not in col]
    data_array = df[feature_cols].values
    target_price_array = df['target_price'].values
    target_return_array = df['target_return'].values

    for i in range(len(df) - window_size):
        # i부터 i+window_size까지의 데이터를 하나의 묶음으로 생성
        X.append(data_array[i : i + window_size])
        # window_size번째 날의 정답(내일의 값)을 저장
        y_price.append(target_price_array[i + window_size - 1])
        y_return.append(target_return_array[i + window_size - 1])

    X = np.array(X)
    y_price = np.array(y_price)
    y_return = np.array(y_return)

    print(f"시퀀스 생성 완료: X 형태 {X.shape}, y_price 형태 {y_price.shape}")
    # 결과 해석: (전체 샘플 수, 20일, 피처 개수)
    return X, y_price, y_return

def build_lstm_model(input_shape):
    # (반복 시 로그가 너무 많아지므로 print문은 생략하거나 필요 시 주석 해제)
    # print("="*50)
    # print(" [Step 5] LSTM 모델 설계 및 컴파일 시작")
    # print("="*50)

    model = Sequential([
        # 1. 첫 번째 LSTM 레이어: 50개의 뉴런으로 시퀀스의 복잡한 패턴 추출
        # return_sequences=True는 다음 LSTM 층으로 기억을 넘겨주기 위함
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2), # 20%의 뉴런을 무작위로 꺼서 과적합(Overfitting) 방지

        # 2. 두 번째 LSTM 레이어: 추출된 패턴을 바탕으로 더 고차원적인 특징 학습
        LSTM(50, return_sequences=False),
        Dropout(0.2),

        # 3. Dense 레이어: 학습된 특징들을 하나로 모음
        Dense(25),

        # 4. 출력 레이어: 최종적으로 '내일의 수치' 1개를 출력 (회귀)
        Dense(1)
    ])

    # 로스 펑션은 MSE(Mean Squared Error) 사용
    # 옵티마이저는 Adam 사용
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    return model

if __name__ == "__main__":
    # 0. 피처 리스트 정의
    feature_cols = [
        'Open', 'High', 'Low', 'Close', 'Volume', 
        'USD_KRW', 'Gold', 'Interest_Rate',
        'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b',
        'cloud_thickness', 'dist_from_kijun'
    ]

    # 1. 데이터 마트 구축
    df_mart, scalers = build_data_mart()
    
    # 2. 시퀀스 생성
    WINDOW_SIZE = 20
    X, y_price, y_return = create_sequences(df_mart, window_size=WINDOW_SIZE)
    
    # 3. 데이터 분할
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_price_train, y_price_test = y_price[:split_index], y_price[split_index:]

    # =================================================================================
    # [Step 6~8] 30회 반복 실험 (Vault Strategy: 수익금 저장 & 긴급 수혈)
    # =================================================================================
    
    experiment_name = "Samsung_Vault_Strategy_30Runs"
    mlflow.set_experiment(experiment_name)

    print(f"\n🔥 [Experiment Start] {experiment_name}")
    print("="*60)

    roi_results = [] 

    for seed in range(30):
        run_name = f"Vault_Strategy_Seed_{seed}"
        
        with mlflow.start_run(run_name=run_name):
            # A. 시드 고정
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            # B. 파라미터 로깅
            mlflow.log_param("seed", seed)
            mlflow.log_param("model_type", "Regression (Vault)")
            mlflow.log_param("threshold", "1.0%")
            mlflow.log_param("strategy", "Profit Vault") # 금고 전략 명시
            
            # C. 모델 학습 
            print(f"\n▶ [Run {seed}/29] 모델 학습 시작! (진행 상황 표시됨)")
            model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
            
            # verbose = 1 :  터미널 표시
            history = model.fit(X_train, y_price_train, 
                                validation_data=(X_test, y_price_test),
                                epochs=50, 
                                batch_size=32, 
                                verbose=1,
                                shuffle=False) 
            
            # D. 시뮬레이션 준비
            pred_scaled = model.predict(X_test, verbose=0)
            target_scaler = scalers['target_price']
            predictions_real = target_scaler.inverse_transform(pred_scaled).flatten()
            y_test_real = target_scaler.inverse_transform(y_price_test.reshape(-1, 1)).flatten()

            INITIAL_CAPITAL = 10000000
            balance = INITIAL_CAPITAL
            
            is_holding = False  # 현재 주식을 들고 있나?
            buy_count = 0 
            sell_count = 0 
            
            THRESHOLD = 0.01 
            
            for i in range(len(predictions_real) - 1):
                today_price = y_test_real[i]
                predicted_tomorrow = predictions_real[i+1]
                actual_tomorrow = y_test_real[i+1]
                
                # 실제 변동률 (오늘 -> 내일)
                actual_change = (actual_tomorrow - today_price) / today_price
                
                # 모델 예측 수익률
                expected_return = (predicted_tomorrow - today_price) / today_price
                
                # ==========================================================
                # 1. [Accounting] 자산 가치 업데이트 (일일 정산)
                # ==========================================================
                # 어제 사서 오늘까지 들고 있었다면, 변동폭 반영
                if is_holding:
                    balance *= (1 + actual_change)
                
               # ==========================================================
                # 2. [Decision] 내일 행동 결정 (매수 / 매도 / 홀딩)
                # ==========================================================
                
                # ★ [수정] 문턱을 1%(0.01)에서 0%(0)으로 낮춤!
                # "조금이라도 오를 것 같으면(양수면) 일단 진입해라."
                BUY_THRESHOLD = 0.000  # 0%
                
                # 1. 매수 조건 (진입)
                if not is_holding:
                    if expected_return > BUY_THRESHOLD: 
                        is_holding = True
                        buy_count += 1

                # 2. 매도 조건 (청산)
                else:
                    # 떨어질 것 같으면(음수면) 판다
                    if expected_return <= 0: 
                        is_holding = False
                        sell_count += 1

            final_roi = ((balance - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
            roi_results.append(final_roi)
            
            mlflow.log_metric("final_roi", final_roi)
            
            trade_ratio = (buy_count / (len(predictions_real) - 1)) * 100

            print(f"   ㄴ [Result] Seed {seed} | ROI: {final_roi:6.2f}% | Buy: {buy_count}회 / Sell: {sell_count}회")
            # AI가 예측한 수익률들의 평균과 최대값을 확인해보자
            avg_pred = np.mean([ (predictions_real[i+1]-y_test_real[i])/y_test_real[i] for i in range(len(predictions_real)-1)])
            max_pred = np.max([ (predictions_real[i+1]-y_test_real[i])/y_test_real[i] for i in range(len(predictions_real)-1)])
            
            print(f"   ㄴ [Debug] 평균 예측 수익률: {avg_pred*100:.4f}% | 최대 예측 수익률: {max_pred*100:.4f}%")
    # 회고 포인트  
    # 일목균형표를 만든 '이치모쿠 산진'은 시장의 주기를 연구하여 9, 26, 52라는 숫자의 의미 
    # 과거 일본 주식 시장은 토요일에도 열렸기 때문에, 26일은 대략 일요일을 제외한 한 달의 영업일을 의미합니다. 
    # 즉, "한 달 전의 에너지가 한 달 뒤의 주가에 영향을 미친다"는 철학이 담겨 있습니다.
    # 하지만 한국 시장은 5영업일이 기준이기 때문에 더욱 적합한 숫자가 있을 것으로 기대
    # 추후, 파라미터 실험을 통해 더욱 정교한 모델을 만들기로 다짐 