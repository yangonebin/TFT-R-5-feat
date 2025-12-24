import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import yfinance as yf
import pandas as pd
import warnings
from sklearn.preprocessing import StandardScaler
import numpy as np
import mlflow
import mlflow.keras
import tensorflow as tf 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# [Helper] 로그 수익률 계산 함수
def get_log_return(series):
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

# ==============================================================================
# [Step 1] 데이터 수집 및 전처리 (순수 OHLCV 5개 피처 체제)
# ==============================================================================
def build_data_mart_5_v3():
    print("="*60)
    print(" [Step 1] Beast V3 순수 5개 피처 데이터 마트 구축")
    print("="*60)
    
    target_stock = "005930.KS" 
    # 거시 경제 지표를 배제하고 주가 본연의 움직임만 추출
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()

    # 로그 수익률 피처 생성
    feature_cols = []
    for col in df.columns:
        new_name = f'Log_Ret_{col}'
        df[new_name] = get_log_return(df[col] if col != 'Volume' else df[col].replace(0, 1))
        feature_cols.append(new_name)

    # 타겟 설정
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['actual_simple_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    df = df.dropna()
    
    # StandardScaler 적용
    scalers = {}
    for col in feature_cols:
        s = StandardScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s

    print(f"✅ 데이터 준비 완료: {len(df)}건 | 사용 피처: {feature_cols}")
    return df, feature_cols

# ==============================================================================
# [Step 2] 시퀀스 생성 (Window 20 고정)
# ==============================================================================
def create_sequences(df, feature_cols, window_size=20):
    X, y_up, y_ret = [], [], []
    data_array = df[feature_cols].values
    target_up_array = df['target_up'].values
    actual_ret_array = df['actual_simple_return'].values

    for i in range(len(df) - window_size):
        X.append(data_array[i : i + window_size])
        y_up.append(target_up_array[i + window_size - 1])
        y_ret.append(actual_ret_array[i + window_size - 1])

    return np.array(X), np.array(y_up), np.array(y_ret)

# ==============================================================================
# [Step 3] Beast V2 엔진 아키텍처 (V3의 기반 엔진)
# ==============================================================================
def build_optimized_beast(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64, return_sequences=True),
        BatchNormalization(),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        BatchNormalization(),
        Dropout(0.3),
        Dense(32, activation='relu', kernel_initializer='he_normal'),
        BatchNormalization(),
        Dense(1, activation='sigmoid') 
    ])
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

# ==============================================================================
# [Main] V3 지능형 금고 전략 30회 독립 시행 (5-Feature)
# ==============================================================================
if __name__ == "__main__":
    df_mart, feature_cols = build_data_mart_5_v3()
    X, y_up, y_ret = create_sequences(df_mart, feature_cols, window_size=20)
    
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y_up[:split_index], y_up[split_index:]
    y_ret_test = y_ret[split_index:]

    mlflow.set_experiment("Samsung_Beast_V3_5Features_Vault")

    print(f"\n🚀 [Final Mission] 5피처 지능형 금고(V3) 30회 테스트 시작")
    roi_results = []
    
    for seed in range(30):
        run_name = f"V3_5Feat_Seed_{seed}"
        with mlflow.start_run(run_name=run_name):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            model = build_optimized_beast((X_train.shape[1], X_train.shape[2]))
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=50, batch_size=64, verbose=1, shuffle=False)
            
            pred_probs = model.predict(X_test, verbose=0).flatten()
            
            # --- V3 Simulation Logic ---
            initial_seed = 10000000
            current_seed = initial_seed
            trading_balance = initial_seed
            vault = 0
            buy_count = 0
            step_up_count = 0
            
            for i in range(len(pred_probs)):
                prob = pred_probs[i]
                actual_ret = y_ret_test[i]
                
                if prob >= 0.5:
                    trading_balance *= (1 + actual_ret)
                    buy_count += 1
                
                # 1. Vaulting: 수익 발생 시 즉시 금고로 격리
                if trading_balance > current_seed:
                    vault += (trading_balance - current_seed)
                    trading_balance = current_seed
                
                # 2. Refill: 손실 발생 시 금고에서 원금 수혈
                elif trading_balance < current_seed:
                    loss = current_seed - trading_balance
                    if vault >= loss:
                        vault -= loss
                        trading_balance = current_seed
                    else:
                        trading_balance += vault
                        vault = 0
                
                # 3. Step-up: 금고가 원금의 50%를 넘으면 운용 원금 상향
                if vault >= (initial_seed * 0.5):
                    current_seed += (initial_seed * 0.5)
                    vault -= (initial_seed * 0.5)
                    trading_balance = current_seed
                    step_up_count += 1

            final_total = trading_balance + vault
            final_roi = ((final_total - initial_seed) / initial_seed) * 100
            roi_results.append(final_roi)
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            mlflow.log_metric("step_up_count", step_up_count)
            
            print(f"▶ Seed {seed:2d} | ROI: {final_roi:6.2f}% | Final Cap: {current_seed/1e6:.1f}M | Steps: {step_up_count}")

    print("\n" + "="*60)
    print(f"💰 [5피처 V3] 30회 평균 수익률: {np.mean(roi_results):.2f}%")
    print("="*60)