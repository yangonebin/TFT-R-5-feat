import os
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import mlflow
import mlflow.keras
import tensorflow as tf
from tensorflow.keras import layers, Model, Input
from sklearn.preprocessing import StandardScaler
import time

# 최적화 및 경고 무시
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

# --- TFT를 위한 핵심 커스텀 블록 ---
def gated_residual_network(x, units, dropout_rate=0.1):
    """불필요한 비선형성을 제어하는 TFT의 핵심 GRN 블록"""
    h = layers.Dense(units, activation='elu')(x)
    h = layers.Dense(units)(h)
    h = layers.Dropout(dropout_rate)(h)
    
    # Gated Linear Unit (GLU)
    gate = layers.Dense(units, activation='sigmoid')(x)
    x = layers.Add()([x, layers.Multiply()([gate, h])])
    return layers.LayerNormalization()(x)

# --- [수정된 VSN 함수] ---
def variable_selection_network(x, units, num_features):
    feature_embeddings = []
    for i in range(num_features):
        feat = layers.Lambda(lambda x, i=i: x[:, :, i:i+1])(x)
        feature_embeddings.append(layers.Dense(units)(feat))
        
    combined = layers.Concatenate()(feature_embeddings)
    weights = layers.Dense(num_features, activation='softmax')(combined)
    
    # tf.stack을 Lambda로 감싸서 사용
    stacked_features = layers.Lambda(lambda x: tf.stack(x, axis=2))(feature_embeddings)
    expanded_weights = layers.Reshape((-1, num_features, 1))(weights)
    weighted_features = layers.Multiply()([stacked_features, expanded_weights])
    
    return layers.Lambda(lambda x: tf.reduce_sum(x, axis=2))(weighted_features)

# --- 데이터 빌더 (5-Feature 전용) ---
def build_tft_data():
    target_stock = "005930.KS"
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()
    feature_cols = []
    for col in df.columns:
        new_name = f'Log_Ret_{col}'
        df[new_name] = np.log((df[col] + 1e-9) / (df[col].shift(1) + 1e-9))
        feature_cols.append(new_name)
    
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['actual_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()
    
    for col in feature_cols:
        df[col] = StandardScaler().fit_transform(df[[col]])
    return df, feature_cols

def create_sequences(df, features, window=20):
    X, y, r = [], [], []
    data, target, ret = df[features].values, df['target_up'].values, df['actual_ret'].values
    for i in range(len(df) - window):
        X.append(data[i:i+window])
        y.append(target[i+window-1])
        r.append(ret[i+window-1])
    return np.array(X), np.array(y), np.array(r)

def build_beast_tft(window_size, num_features, units=64):
    inputs = Input(shape=(window_size, num_features))
    
    # 1. Variable Selection (어떤 가격 지표가 중요한가?)
    vsn = variable_selection_network(inputs, units, num_features)
    
    # 2. LSTM 기반의 Temporal Context 추출
    lstm = layers.LSTM(units, return_sequences=True)(vsn)
    lstm = layers.LayerNormalization()(lstm)
    
    # 3. Multi-Head Attention (시계열의 장단기 맥락 파악)
    attn = layers.MultiHeadAttention(num_heads=4, key_dim=units)(lstm, lstm)
    attn = layers.Add()([lstm, attn])
    attn = layers.LayerNormalization()(attn)
    
    # 4. Gated Residual Network (최종 출력 제어)
    grn = gated_residual_network(attn[:, -1, :], units)
    
    # 5. Output (Regressor: 수익률 강도 예측)
    outputs = layers.Dense(1)(grn) # V1처럼 회귀 모델로 설정
    
    model = Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss='mse')
    return model

# build_beast_tft 아키텍처는 기존과 동일하게 유지하되 위 vsn 함수를 사용합니다.

if __name__ == "__main__":
    df, features = build_tft_data()
    X, y, r = create_sequences(df, features)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    # V1 계승: 실제 수익률(r)로 학습하는 Regressor
    y_train, y_test = r[:split], r[split:] 
    r_test = r[split:]

    mlflow.set_experiment("Samsung_SOTA_TFT_5Features_Final")
    
    roi_results = []
    buy_counts = [] # <--- 매매 횟수 저장을 위한 리스트 추가
    
    print(f"\n🚀 [SOTA] TFT 5-Feature 모델 학습 및 검증 시작")
    print("="*60)

    for seed in range(30):
        with mlflow.start_run(run_name=f"TFT_Seed_{seed}"):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            mlflow.log_param("seed", seed)
            
            model = build_beast_tft(X.shape[1], X.shape[2])
            es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
            
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=150, batch_size=128, verbose=0, callbacks=[es])
            
            preds = model.predict(X_test, verbose=0).flatten()
            
            # 시뮬레이션
            balance = 10000000
            buy_count = 0
            for i in range(len(preds)):
                if preds[i] > 0: 
                    balance *= (1 + r_test[i])
                    buy_count += 1
            
            final_roi = ((balance - 10000000) / 10000000) * 100
            
            # 결과 저장
            roi_results.append(final_roi)
            buy_counts.append(buy_count) # <--- 리스트에 추가
            
            mlflow.log_metric("final_roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            
            print(f"[{time.strftime('%H:%M:%S')}] Seed {seed:2d} | ROI: {final_roi:8.2f}% | Buy: {buy_count:4d}")

    # --- 최종 결과 출력 섹션 ---
    print("\n" + "="*60)
    print(f"🏆 [TFT SOTA 최종 리포트]")
    print(f" - 30회 평균 ROI: {np.mean(roi_results):.4f}%")
    print(f" - 30회 평균 매매 횟수: {np.mean(buy_counts):.2f}회") # <--- 요청하신 부분
    print(f" - 최고 ROI (Seed {np.argmax(roi_results)}): {np.max(roi_results):.2f}%")
    print("="*60)