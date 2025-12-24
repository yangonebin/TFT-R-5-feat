import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# [Helper] 로그 수익률 계산 함수
# ---------------------------------------------------------
def get_log_return(series):
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

# ==============================================================================
# [Step 1] 데이터 수집 및 14개 피처 마트 구축 (로그 수익률 기반)
# ==============================================================================
def build_data_mart_v4():
    print("="*60)
    print(" [Step 1] 14개 피처 복원 및 로그 수익률 변환")
    print("="*60)
    
    target_stock = "005930.KS" 
    macro_symbols = { "USD_KRW": "KRW=X", "Gold": "GC=F", "Interest_Rate": "^TNX" }

    # 1. 주가 데이터 다운로드
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 2. 거시 경제 데이터 통합
    for name, symbol in macro_symbols.items():
        macro = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        if isinstance(macro.columns, pd.MultiIndex):
            macro.columns = macro.columns.get_level_values(0)
        df[name] = macro['Close']

    df = df.ffill()

    # 3. 일목균형표 피처 생성 (로그 변환 전 원본 가격 기준 계산)
    nine_high = df['High'].rolling(window=9).max()
    nine_low = df['Low'].rolling(window=9).min()
    df['tenkan_sen'] = (nine_high + nine_low) / 2

    twenty_six_high = df['High'].rolling(window=26).max()
    twenty_six_low = df['Low'].rolling(window=26).min()
    df['kijun_sen'] = (twenty_six_high + twenty_six_low) / 2

    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    fifty_two_high = df['High'].rolling(window=52).max()
    fifty_two_low = df['Low'].rolling(window=52).min()
    df['senkou_span_b'] = ((fifty_two_high + fifty_two_low) / 2).shift(26)

    # 파생 변수: 구름대 두께 및 기준선 이격도
    df['cloud_thickness'] = df['senkou_span_a'] - df['senkou_span_b']
    df['dist_from_kijun'] = df['Close'] - df['kijun_sen']

    # 4. 모든 가격/지표 데이터를 '로그 수익률' 및 '상대 지표'로 변환
    feature_cols = []
    
    # 가격 기반 지표들 로그 수익률화
    price_based_cols = [
        'Close', 'Open', 'High', 'Low', 'Volume', 
        'USD_KRW', 'Gold', 'Interest_Rate',
        'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b'
    ]
    
    for col in price_based_cols:
        new_name = f'Log_Ret_{col}'
        df[new_name] = get_log_return(df[col] if 'Volume' not in col else df[col].replace(0, 1))
        feature_cols.append(new_name)
    
    # 두께와 이격도는 이미 차이값이므로 그대로 사용 (명칭만 추가)
    feature_cols.extend(['cloud_thickness', 'dist_from_kijun'])

    # ★ [Target] 내일의 로그 수익률
    df['target_log_return'] = df['Log_Ret_Close'].shift(-1)
    df['actual_simple_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    df = df.dropna()
    
    # 5. 스케일링 (MinMaxScaler)
    scalers = {}
    for col in feature_cols + ['target_log_return']:
        s = MinMaxScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s

    print(f"✅ 데이터 준비 완료: {len(df)}건 | 사용 피처: {len(feature_cols)}개")
    return df, feature_cols, scalers

# ==============================================================================
# [Step 2] 시퀀스 생성 및 모델 구축
# ==============================================================================
def create_sequences(df, feature_cols, window_size=20):
    X, y_target, y_actual = [], [], []
    data_array = df[feature_cols].values
    target_array = df['target_log_return'].values
    actual_array = df['actual_simple_return'].values

    for i in range(len(df) - window_size):
        X.append(data_array[i : i + window_size])
        y_target.append(target_array[i + window_size - 1])
        y_actual.append(actual_array[i + window_size - 1])

    return np.array(X), np.array(y_target), np.array(y_actual)

def build_lstm_regression(input_shape):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1) 
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# ==============================================================================
# [Main] 30회 독립 시행 (Baseline용 데이터 확보)
# ==============================================================================
if __name__ == "__main__":
    df_mart, feature_cols, scalers = build_data_mart_v4()
    X, y_target, y_actual = create_sequences(df_mart, feature_cols)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y_target[:split], y_target[split:]
    y_actual_test = y_actual[split:]

    experiment_name = "Samsung_Baseline_Improved_Regression"
    mlflow.set_experiment(experiment_name)

    print(f"\n🚀 {experiment_name} 30회 반복 실험 시작")
    
    roi_results = []
    trade_counts = [] # 거래 횟수를 담을 리스트 추가

    for seed in range(30):
        with mlflow.start_run(run_name=f"LogReg_Seed_{seed}"):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            mlflow.log_param("seed", seed)
            
            model = build_lstm_regression((X_train.shape[1], X_train.shape[2]))
            model.fit(X_train, y_train, epochs=30, batch_size=32, verbose=1, shuffle=False)
            
            pred_scaled = model.predict(X_test, verbose=1)
            pred_real = scalers['target_log_return'].inverse_transform(pred_scaled).flatten()
            
            # 시뮬레이션
            balance = 10000000
            is_holding = False
            buy_count = 0 # 매수 횟수 초기화

            for i in range(len(pred_real) - 1):
                if is_holding: balance *= (1 + y_actual_test[i+1])
                
                if pred_real[i+1] > 0: # 내일 상승 예측 시
                    if not is_holding:
                        is_holding = True
                        buy_count += 1 # 매수 카운트 증가
                else:
                    is_holding = False
            
            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            trade_counts.append(buy_count) # 결과 리스트에 추가
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count) # MLflow 기록
            
            print(f"▶ Seed {seed:2d} | ROI: {final_roi:6.2f}% | Trades: {buy_count:3d}회")

    # [최종 요약 출력]
    print("\n" + "="*60)
    print(f"💰 Baseline 30회 평균 수익률 : {np.mean(roi_results):.2f}%")
    print(f"📈 Baseline 30회 평균 거래 횟수: {np.mean(trade_counts):.1f}회")
    print("="*60)