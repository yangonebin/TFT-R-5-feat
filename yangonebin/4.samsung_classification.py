import os
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
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

# ==============================================================================
# [Step 1] 데이터 수집 및 전처리 (A군과 동일)
# ==============================================================================
def build_data_mart():
    print("="*50)
    print(" [Step 1] 데이터 수집 (야수 모델용 분류 데이터)")
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

    # 로그 수익률 변환
    df['Log_Ret_Close'] = get_log_return(df['Close'])
    df['Log_Ret_Open']  = get_log_return(df['Open'])
    df['Log_Ret_High']  = get_log_return(df['High'])
    df['Log_Ret_Low']   = get_log_return(df['Low'])
    df['Log_Ret_Vol']   = get_log_return(df['Volume'].replace(0, 1))
    df['Log_Ret_USD']   = get_log_return(df['USD_KRW'])
    df['Log_Ret_Gold']  = get_log_return(df['Gold'])
    df['Log_Ret_Rate']  = get_log_return(df['Interest_Rate'])

    # ★ [분류 타겟] : 내일 종가가 오늘보다 높으면 1, 아니면 0
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    
    # 실제 수익률 (ROI 계산용)
    df['actual_simple_return'] = (df['Close'].shift(-1) / df['Close']) - 1

    df = df.dropna()
    
    feature_cols = ['Log_Ret_Close', 'Log_Ret_Open', 'Log_Ret_High', 'Log_Ret_Low', 'Log_Ret_Vol', 'Log_Ret_USD', 'Log_Ret_Gold', 'Log_Ret_Rate']
    
    scalers = {}
    for col in feature_cols:
        s = MinMaxScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s

    print(f"데이터 준비 완료: {len(df)}건")
    return df, feature_cols

# ==============================================================================
# [Step 2] 시퀀스 생성 (A군과 동일)
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
# [Step 3] 야수 모델 (A군과 완벽히 동일한 구조 + 출력층만 Sigmoid)
# ==============================================================================
def build_lstm_classification(input_shape):
    model = Sequential([
        # A군과 동일: LSTM 50 Units (True) -> Dropout(0.2) -> LSTM 50 Units (False) -> Dropout(0.2) -> Dense(25)
        tf.keras.layers.LSTM(50, return_sequences=True, input_shape=input_shape),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(50, return_sequences=False),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(25),
        # 최종 출력만 분류용 Sigmoid로 변경
        tf.keras.layers.Dense(1, activation='sigmoid') 
    ])
    # 손실 함수만 이진 분류용으로 변경
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# ==============================================================================
# [Main] 30회 독립 시행
# ==============================================================================
if __name__ == "__main__":
    df_mart, feature_cols = build_data_mart()
    WINDOW_SIZE = 20
    X, y_up, y_ret = create_sequences(df_mart, feature_cols, window_size=WINDOW_SIZE)
    
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y_up[:split_index], y_up[split_index:]
    y_ret_test = y_ret[split_index:]

    experiment_name = "Samsung_Challenger_Classification"
    mlflow.set_experiment(experiment_name)

    print(f"\n🔥 [Experiment] {experiment_name} 30회 승부 시작")
    print("="*60)

    roi_results = []
    
    for seed in range(30):
        run_name = f"Classification_Seed_{seed}"
        with mlflow.start_run(run_name=run_name):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            model = build_lstm_classification((X_train.shape[1], X_train.shape[2]))
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=30, batch_size=32, verbose=1, shuffle=False)
            
            pred_probs = model.predict(X_test, verbose=0).flatten()
            
            # -------------------------------------------------------
            # [Trading Simulation: Daily Alpha Strategy]
            # -------------------------------------------------------
            # 거래 횟수를 늘리기 위해 "매일 확률이 0.5가 넘으면 그날의 수익을 취한다"는 로직 적용
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
            print(f"   ㄴ [Result] Seed {seed} | ROI: {final_roi:6.2f}% | Trades: {buy_count}회")

    print("="*60)
    print(f"💰 야수(Classification) 평균 수익률: {np.mean(roi_results):.2f}%")
    print("="*60)