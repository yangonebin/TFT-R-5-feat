import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import yfinance as yf
import pandas as pd
import numpy as np
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import warnings

warnings.filterwarnings('ignore')

# [Helper] 로그 수익률 계산
def get_log_return(series):
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

# [Step 1] 순수 OHLCV 5개 피처 데이터 구축
def build_data_mart_5():
    print("="*60)
    print(" [Step 1] 순수 OHLCV 5개 피처 데이터 마트 구축 (Regressor)")
    print("="*60)
    target_stock = "005930.KS"
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = df.columns.get_level_values(0)
    
    # 순수 5개 피처만 선택
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()

    feature_cols = []
    # 로그 수익률 변환
    for col in df.columns:
        new_col = f'LR_{col}'
        df[new_col] = get_log_return(df[col] if col != 'Volume' else df[col].replace(0, 1))
        feature_cols.append(new_col)

    # 타겟: 내일의 로그 수익률 (Regression)
    df['target'] = df['LR_Close'].shift(-1)
    # 시뮬레이션용 실제 변동률
    df['actual_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()

    scalers = {}
    for col in feature_cols + ['target']:
        s = MinMaxScaler()
        df[col] = s.fit_transform(df[[col]])
        scalers[col] = s
    
    print(f"✅ 데이터 준비 완료: {len(df)}건 | 사용 피처: {feature_cols}")
    return df, feature_cols, scalers

# [Step 2] 시퀀스 생성 함수
def create_sequences(df, feature_cols, window_size=20):
    X, y, y_actual = [], [], []
    data_array = df[feature_cols].values
    target_array = df['target'].values
    actual_array = df['actual_ret'].values

    for i in range(len(df) - window_size):
        X.append(data_array[i : i + window_size])
        y.append(target_array[i + window_size - 1])
        y_actual.append(actual_array[i + window_size - 1])

    return np.array(X), np.array(y), np.array(y_actual)

# [Step 3] LSTM Regressor 모델 구축
def build_lstm_regressor(input_shape):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1) # 수치 예측이므로 활성화 함수 없음
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# ==============================================================================
# [Main] 30회 독립 시행
# ==============================================================================
if __name__ == "__main__":
    # 함수 이름 수정 완료
    df_mart, feature_cols, scalers = build_data_mart_5()
    
    WINDOW_SIZE = 20
    X, y_target, y_actual = create_sequences(df_mart, feature_cols, window_size=WINDOW_SIZE)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y_target[:split], y_target[split:]
    y_actual_test = y_actual[split:]

    mlflow.set_experiment("Samsung_Regressor_5Features_Test")
    
    roi_results = []
    trade_results = []

    print(f"\n🚀 [Experiment] 순수 5피처 Regressor 30회 테스트 시작")

    for seed in range(30):
        with mlflow.start_run(run_name=f"Reg5_Seed_{seed}"):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            mlflow.log_param("seed", seed)

            model = build_lstm_regressor((X_train.shape[1], X_train.shape[2]))
            
            # 학습 (Regressor는 보통 에포크가 너무 길면 상수로 수렴할 위험이 있어 30으로 설정)
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=30, batch_size=32, verbose=1, shuffle=False)

            # 예측 및 역스케일링
            pred_scaled = model.predict(X_test, verbose=0)
            pred_real = scalers['target'].inverse_transform(pred_scaled).flatten()

            # 수익률 시뮬레이션
            balance = 10000000
            is_holding = False
            buy_count = 0
            
            for i in range(len(pred_real) - 1):
                if is_holding:
                    balance *= (1 + y_actual_test[i+1])
                
                # 예측 로그 수익률이 0보다 크면 매수/홀딩
                if pred_real[i+1] > 0:
                    if not is_holding:
                        is_holding = True
                        buy_count += 1
                else:
                    is_holding = False

            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            trade_results.append(buy_count)
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            print(f"▶ Seed {seed:2d} | ROI: {final_roi:6.2f}% | Trades: {buy_count}회")

    print("\n" + "="*60)
    print(f"💰 5피처 Regressor 평균 ROI: {np.mean(roi_results):.2f}% | 평균 거래: {np.mean(trade_results):.1f}회")
    print("="*60)