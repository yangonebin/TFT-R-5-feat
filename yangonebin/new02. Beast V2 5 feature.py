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
# [Step 1] 데이터 수집 및 전처리 (순수 OHLCV 5개 피처만 사용)
# ==============================================================================
def build_data_mart_5_v2():
    print("="*60)
    print(" [Step 1] 순수 5개 피처 기반 Beast V2 데이터 구축")
    print("="*60)
    
    target_stock = "005930.KS" 
    # 거시 지표를 제외하고 삼성전자 데이터만 다운로드
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # 순수 5개 가격 데이터 복사
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()

    # 로그 수익률 피처 생성
    feature_cols = []
    for col in df.columns:
        new_name = f'Log_Ret_{col}'
        df[new_name] = get_log_return(df[col] if col != 'Volume' else df[col].replace(0, 1))
        feature_cols.append(new_name)

    # 타겟: 내일 종가가 오늘보다 높으면 1
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['actual_simple_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    df = df.dropna()
    
    # [V2 정석] StandardScaler 적용
    scalers = {}
    for col in feature_cols:
        s = StandardScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s

    print(f"✅ 데이터 준비 완료: {len(df)}건 | 사용 피처: {feature_cols}")
    return df, feature_cols

# ==============================================================================
# [Step 2] 시퀀스 생성 (V2 동일)
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
# [Step 3] 고도화된 야수 모델 (Beast V2 아키텍처 100% 동일)
# ==============================================================================
def build_optimized_beast(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        # 1층 LSTM + BN + Dropout 0.3
        LSTM(64, return_sequences=True),
        BatchNormalization(),
        Dropout(0.3),
        
        # 2층 LSTM + BN + Dropout 0.3
        LSTM(32, return_sequences=False),
        BatchNormalization(),
        Dropout(0.3),
        
        # Dense 층 (He Normal + ReLU)
        Dense(32, activation='relu', kernel_initializer='he_normal'),
        BatchNormalization(),
        
        # 최종 출력
        Dense(1, activation='sigmoid') 
    ])
    
    # 학습률 0.001 (V2 오리지널)
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

# ==============================================================================
# [Main] 30회 독립 시행 (V2 로직 100% 동일)
# ==============================================================================
if __name__ == "__main__":
    df_mart, feature_cols = build_data_mart_5_v2()
    X, y_up, y_ret = create_sequences(df_mart, feature_cols, window_size=20)
    
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y_up[:split_index], y_up[split_index:]
    y_ret_test = y_ret[split_index:]

    # 실험 이름 변경
    experiment_name = "Samsung_Beast_V2_5Feature_Original"
    mlflow.set_experiment(experiment_name)

    print(f"\n🚀 [Run] V2 아키텍처 그대로 5피처 테스트 시작")
    roi_results = []
    
    for seed in range(30):
        run_name = f"V2_5Feat_Seed_{seed}"
        with mlflow.start_run(run_name=run_name):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            mlflow.log_param("seed", seed)
            
            model = build_optimized_beast((X_train.shape[1], X_train.shape[2]))
            
            # V2 설정 그대로: 50 Epochs, No EarlyStopping
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=50, batch_size=64, verbose=1, shuffle=False)
            
            # 예측
            pred_probs = model.predict(X_test, verbose=0).flatten()
            
            # 시뮬레이션 (V2 로직: prob >= 0.5)
            balance = 10000000
            buy_count = 0
            
            for i in range(len(pred_probs)):
                if pred_probs[i] >= 0.5:
                    balance *= (1 + y_ret_test[i])
                    buy_count += 1

            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            print(f"▶ Seed {seed:2d} | ROI: {final_roi:6.2f}% | Trades: {buy_count}회 | Prob Max: {pred_probs.max():.4f}")

    print("\n" + "="*60)
    print(f"💰 [5피처 V2] 평균 ROI: {np.mean(roi_results):.2f}%")
    print(f"📈 [5피처 V2] 평균 거래 횟수: {np.mean(trade_results) if 'trade_results' in locals() else '계산됨'}회")
    print("="*60)