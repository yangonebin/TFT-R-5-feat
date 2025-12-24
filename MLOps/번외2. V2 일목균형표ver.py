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
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import regularizers
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

def get_log_return(series):
    return np.log((series + 1e-9) / (series.shift(1) + 1e-9))

def build_data_mart_v2():
    print("="*60)
    print(" [Step 1] Beast V2.5용 14개 피처 데이터 마트 구축")
    print("="*60)
    target_stock = "005930.KS"
    macro_symbols = {"USD_KRW": "KRW=X", "Gold": "GC=F", "Interest_Rate": "^TNX"}
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    for name, symbol in macro_symbols.items():
        macro = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        if isinstance(macro.columns, pd.MultiIndex): macro.columns = macro.columns.get_level_values(0)
        df[name] = macro['Close']
    df = df.ffill()

    # 일목균형표 계산
    df['tenkan'] = (df['High'].rolling(9).max() + df['Low'].rolling(9).min()) / 2
    df['kijun'] = (df['High'].rolling(26).max() + df['Low'].rolling(26).min()) / 2
    df['span_a'] = ((df['tenkan'] + df['kijun']) / 2).shift(26)
    df['span_b'] = ((df['High'].rolling(52).max() + df['Low'].rolling(52).min()) / 2).shift(26)
    df['cloud_thick'] = df['span_a'] - df['span_b']
    df['dist_kijun'] = df['Close'] - df['kijun']

    feature_cols = []
    price_cols = ['Open','High','Low','Close','Volume','USD_KRW','Gold','Interest_Rate','tenkan','kijun','span_a','span_b']
    for col in price_cols:
        df[f'Log_Ret_{col}'] = get_log_return(df[col] if 'Volume' not in col else df[col].replace(0, 1))
        feature_cols.append(f'Log_Ret_{col}')
    feature_cols.extend(['cloud_thick', 'dist_kijun'])

    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['actual_simple_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()

    for col in feature_cols:
        s = StandardScaler()
        df[col] = s.fit_transform(df[[col]])
    return df, feature_cols

def create_sequences_v2(df, feature_cols, window_size=20):
    X, y, y_ret = [], [], []
    data_array = df[feature_cols].values
    target_array = df['target_up'].values
    ret_array = df['actual_simple_ret'].values
    for i in range(len(df) - window_size):
        X.append(data_array[i : i + window_size])
        y.append(target_array[i + window_size - 1])
        y_ret.append(ret_array[i + window_size - 1])
    return np.array(X), np.array(y), np.array(y_ret)

def build_refined_beast(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64, return_sequences=True, kernel_regularizer=regularizers.l2(0.01)),
        BatchNormalization(),
        Dropout(0.4),
        LSTM(32, kernel_regularizer=regularizers.l2(0.01)),
        BatchNormalization(),
        Dropout(0.4),
        Dense(16, activation='relu', kernel_regularizer=regularizers.l2(0.01)),
        BatchNormalization(),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005), 
                  loss='binary_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    df_mart, feature_cols = build_data_mart_v2()
    X, y_up, y_ret = create_sequences_v2(df_mart, feature_cols)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y_up[:split], y_up[split:]
    y_ret_test = y_ret[split:]

    mlflow.set_experiment("Samsung_Final_Beast_V2_14Features")
    roi_results = []
    trade_results = []

    for seed in range(30):
        with mlflow.start_run(run_name=f"Beast2.5_Seed_{seed}"):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            mlflow.log_param("seed", seed)

            model = build_refined_beast((X_train.shape[1], X_train.shape[2]))
            early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=100, batch_size=64, verbose=1, shuffle=False, callbacks=[early_stop])

            pred_probs = model.predict(X_test, verbose=0).flatten()
            balance = 10000000
            buy_count = 0
            for i in range(len(pred_probs)):
                if pred_probs[i] >= 0.55:
                    balance *= (1 + y_ret_test[i])
                    buy_count += 1

            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            trade_results.append(buy_count)
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            print(f"▶ Seed {seed:2d} | ROI: {final_roi:6.2f}% | Trades: {buy_count}회")

    print("\n" + "="*60)
    print(f"💰 Beast V2.5 평균 ROI: {np.mean(roi_results):.2f}% | 평균 거래: {np.mean(trade_results):.1f}회")
    print("="*60)