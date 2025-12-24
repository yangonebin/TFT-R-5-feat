import os
# 윈도우 환경 최적화
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

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# [Helper] 로그 수익률 계산 함수
# ---------------------------------------------------------
def get_log_return(series):
    # 0 나누기 방지용 엡실론 추가
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

# ==============================================================================
# [Step 1] 데이터 수집 및 전처리 (Log Return 적용)
# ==============================================================================
def build_data_mart():
    print("="*50)
    print(" [Step 1] 데이터 수집 (로그 수익률 변환)")
    print("="*50)
    
    target_stock = "005930.KS" 
    macro_symbols = { 
        "USD_KRW": "KRW=X", 
        "Gold": "GC=F", 
        "Interest_Rate": "^TNX" 
    }

    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    for name, symbol in macro_symbols.items():
        macro = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        if isinstance(macro.columns, pd.MultiIndex):
            macro.columns = macro.columns.get_level_values(0)
        df[name] = macro['Close']

    df = df.ffill()

    # 1. 모든 가격 데이터를 '로그 수익률'로 변환
    df['Log_Ret_Close'] = get_log_return(df['Close'])
    df['Log_Ret_Open']  = get_log_return(df['Open'])
    df['Log_Ret_High']  = get_log_return(df['High'])
    df['Log_Ret_Low']   = get_log_return(df['Low'])
    df['Log_Ret_Vol']   = get_log_return(df['Volume'].replace(0, 1))
    
    df['Log_Ret_USD']   = get_log_return(df['USD_KRW'])
    df['Log_Ret_Gold']  = get_log_return(df['Gold'])
    df['Log_Ret_Rate']  = get_log_return(df['Interest_Rate'])

    # ★ [Target 설정] : 내일의 '로그 수익률'을 맞춰라! (Regression)
    df['target_log_return'] = df['Log_Ret_Close'].shift(-1)
    
    # 시뮬레이션용 실제 수익률 (단순 수익률)
    df['actual_simple_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    df = df.dropna()
    
    # 학습에 쓸 피처들
    feature_cols = [
        'Log_Ret_Close', 'Log_Ret_Open', 'Log_Ret_High', 'Log_Ret_Low', 'Log_Ret_Vol',
        'Log_Ret_USD', 'Log_Ret_Gold', 'Log_Ret_Rate'
    ]
    
    # 스케일링
    scalers = {}
    for col in feature_cols + ['target_log_return']:
        s = MinMaxScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s

    print(f"데이터 준비 완료: {len(df)}건")
    return df, feature_cols, scalers

# ==============================================================================
# [Step 2] 시퀀스 생성
# ==============================================================================
def create_sequences(df, feature_cols, window_size=20):
    X = [] 
    y_target = []   
    y_actual = []   

    data_array = df[feature_cols].values
    target_array = df['target_log_return'].values
    actual_array = df['actual_simple_return'].values

    for i in range(len(df) - window_size):
        X.append(data_array[i : i + window_size])
        y_target.append(target_array[i + window_size - 1])
        y_actual.append(actual_array[i + window_size - 1])

    return np.array(X), np.array(y_target), np.array(y_actual)

# ==============================================================================
# [Step 3] LSTM 회귀 모델
# ==============================================================================
def build_lstm_regression(input_shape):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1) 
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# ==============================================================================
# [Main] 실행 (30회 반복 - Baseline2 데이터 확보용)
# ==============================================================================
if __name__ == "__main__":
    # 1. 데이터 준비
    df_mart, feature_cols, scalers = build_data_mart()
    
    # 2. 시퀀스 생성
    WINDOW_SIZE = 20
    X, y_target, y_actual = create_sequences(df_mart, feature_cols, window_size=WINDOW_SIZE)
    
    # 3. 분할
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y_target[:split_index], y_target[split_index:]
    y_actual_test = y_actual[split_index:]

    # 실험 이름 (나중에 분류 모델과 구분하기 쉽게 명확히!)
    experiment_name = "Samsung_Baseline_LogReturn_Regression"
    mlflow.set_experiment(experiment_name)

    print(f"\n🔥 [Experiment] {experiment_name} 30회 수행 시작")
    print("="*60)

    roi_results = []
    
    # ★ [핵심] 30번 돌려서 통계적 유의성 확보
    for seed in range(30):
        run_name = f"LogReg_Seed_{seed}"
        
        with mlflow.start_run(run_name=run_name):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            mlflow.log_param("seed", seed)
            mlflow.log_param("type", "Regression (Improved)")
            mlflow.log_param("feature", "Log Return")
            
            print(f"\n▶ [Run {seed}/29] 모델 학습 중...")
            
            # 모델 학습
            model = build_lstm_regression((X_train.shape[1], X_train.shape[2]))
            history = model.fit(X_train, y_train, 
                                validation_data=(X_test, y_test),
                                epochs=30, 
                                batch_size=32, 
                                verbose=1, # 진행바 표시
                                shuffle=False)
            
            # 예측
            pred_scaled = model.predict(X_test, verbose=0)
            target_scaler = scalers['target_log_return']
            pred_real = target_scaler.inverse_transform(pred_scaled).flatten()
            
            # 시뮬레이션
            initial_capital = 10000000
            balance = initial_capital
            is_holding = False
            buy_count = 0
            
            THRESHOLD = 0.0 
            
            for i in range(len(pred_real) - 1):
                predicted_log_ret = pred_real[i+1]
                actual_simp_ret = y_actual_test[i+1]
                
                if is_holding:
                    balance *= (1 + actual_simp_ret)
                
                if not is_holding:
                    if predicted_log_ret > THRESHOLD:
                        is_holding = True
                        buy_count += 1
                else:
                    if predicted_log_ret <= THRESHOLD:
                        is_holding = False
            
            final_roi = ((balance - initial_capital) / initial_capital) * 100
            roi_results.append(final_roi)
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            
            print(f"   ㄴ [Result] Seed {seed} | ROI: {final_roi:6.2f}% | Trades: {buy_count}회")

    print("="*60)
    print(f"💰 Baseline(Regression) 30회 평균 수익률: {np.mean(roi_results):.2f}%")
    print("="*60)