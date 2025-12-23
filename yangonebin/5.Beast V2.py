import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import yfinance as yf
import pandas as pd
import warnings
from sklearn.preprocessing import StandardScaler  # MinMaxScaler에서 변경
import numpy as np
import mlflow
import mlflow.keras
import tensorflow as tf 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

def get_log_return(series):
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

# ==============================================================================
# [Step 1] 데이터 수집 및 전처리 (StandardScaler 적용)
# ==============================================================================
def build_data_mart():
    print("="*50)
    print(" [Step 1] 고도화된 야수 모델용 데이터 구축")
    print("="*50)
    
    target_stock = "005930.KS" 
    macro_symbols = { "USD_KRW": "KRW=X", "Gold": "GC=F", "Interest_Rate": "^TNX" }

    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    for name, symbol in macro_symbols.items():
        macro = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        if isinstance(macro.columns, pd.MultiIndex):
            macro.columns = macro.columns.get_level_values(0)
        df[name] = macro['Close']

    df = df.ffill()

    # 로그 수익률 피처 생성
    cols_to_convert = ['Close', 'Open', 'High', 'Low', 'Volume']
    for col in cols_to_convert:
        df[f'Log_Ret_{col}'] = get_log_return(df[col] if col != 'Volume' else df[col].replace(0, 1))
    
    df['Log_Ret_USD']   = get_log_return(df['USD_KRW'])
    df['Log_Ret_Gold']  = get_log_return(df['Gold'])
    df['Log_Ret_Rate']  = get_log_return(df['Interest_Rate'])

    # 타겟: 내일 종가가 상승하면 1
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['actual_simple_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    df = df.dropna()
    
    feature_cols = [c for c in df.columns if 'Log_Ret' in c]
    
    # [변경] StandardScaler로 데이터의 변별력(해상도) 극대화
    scalers = {}
    for col in feature_cols:
        s = StandardScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s

    print(f"데이터 준비 완료: {len(df)}건 | 피처 수: {len(feature_cols)}")
    return df, feature_cols

# ==============================================================================
# [Step 2] 시퀀스 생성
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
# [Step 3] 고도화된 야수 모델 (Beast V2)
# ==============================================================================
def build_optimized_beast(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        # 1층 LSTM + BN
        LSTM(64, return_sequences=True),
        BatchNormalization(),
        Dropout(0.3),
        
        # 2층 LSTM + BN
        LSTM(32, return_sequences=False),
        BatchNormalization(),
        Dropout(0.3),
        
        # 가중치 초기화(He Normal)와 활성화 함수(ReLU)를 적용한 Dense 층
        Dense(32, activation='relu', kernel_initializer='he_normal'),
        BatchNormalization(),
        
        # 최종 출력
        Dense(1, activation='sigmoid') 
    ])
    
    # 학습률 최적화
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
    return model

# ==============================================================================
# [Main] 30회 독립 시행 (ROI 극대화 버전)
# ==============================================================================
if __name__ == "__main__":
    df_mart, feature_cols = build_data_mart()
    X, y_up, y_ret = create_sequences(df_mart, feature_cols, window_size=20)
    
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y_up[:split_index], y_up[split_index:]
    y_ret_test = y_ret[split_index:]

    experiment_name = "Samsung_Final_Beast_V2"
    mlflow.set_experiment(experiment_name)

    print(f"\n🔥 [Final Mission] 완성형 야수 30회 테스트 시작")
    roi_results = []
    
    for seed in range(30):
        run_name = f"FinalBeast_Seed_{seed}"
        with mlflow.start_run(run_name=run_name):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            model = build_optimized_beast((X_train.shape[1], X_train.shape[2]))
            
            # Epochs를 50으로 늘려 충분히 학습
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=50, batch_size=64, verbose=1, shuffle=False)
            
            # 예측
            pred_probs = model.predict(X_test, verbose=0).flatten()
            
            # 시뮬레이션
            balance = 10000000
            buy_count = 0
            
            for i in range(len(pred_probs)):
                prob = pred_probs[i]
                actual_ret = y_ret_test[i]
                if prob >= 0.5:
                    balance *= (1 + actual_ret)
                    buy_count += 1

            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            print(f"▶ Seed {seed} | ROI: {final_roi:6.2f}% | Trades: {buy_count}회 | Prob Max: {pred_probs.max():.4f}")

    print("="*60)
    print(f"💰 완성형 야수 평균 수익률: {np.mean(roi_results):.2f}%")
    print("="*60)