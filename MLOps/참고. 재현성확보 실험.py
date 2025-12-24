import os
import random
import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model, Input
from sklearn.preprocessing import StandardScaler
import joblib

# --- [ 1. 환경 설정 및 시드 고정 함수 ] ---
def setup_deterministic_env(seed=42):
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['TF_CUDNN_DETERMINISTIC'] = '1'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)

# --- [ 2. 한빈님의 Beast V3 아키텍처 그대로 구현 ] ---

def variable_selection_network(x, units, num_features):
    feature_embeddings = []
    for i in range(num_features):
        feat = layers.Lambda(lambda x, i=i: x[:, :, i:i+1])(x)
        feature_embeddings.append(layers.Dense(units)(feat))
    combined = layers.Concatenate()(feature_embeddings)
    weights = layers.Dense(num_features, activation='softmax')(combined)
    stacked_features = layers.Lambda(lambda x: tf.stack(x, axis=2))(feature_embeddings)
    expanded_weights = layers.Reshape((-1, num_features, 1))(weights)
    weighted_features = layers.Multiply()([stacked_features, expanded_weights])
    return layers.Lambda(lambda x: tf.reduce_sum(x, axis=2))(weighted_features)

def gated_residual_network(x, units, dropout_rate=0.1):
    h = layers.Dense(units, activation='elu')(x)
    h = layers.Dense(units)(h)
    h = layers.Dropout(dropout_rate)(h)
    gate = layers.Dense(units, activation='sigmoid')(x)
    x = layers.Add()([x, layers.Multiply()([gate, h])])
    return layers.LayerNormalization()(x)

def build_beast_tft(window_size, num_features, units=64):
    inputs = Input(shape=(window_size, num_features))
    vsn = variable_selection_network(inputs, units, num_features)
    lstm = layers.LSTM(units, return_sequences=True)(vsn)
    lstm = layers.LayerNormalization()(lstm)
    attn = layers.MultiHeadAttention(num_heads=4, key_dim=units)(lstm, lstm)
    attn = layers.Add()([lstm, attn])
    attn = layers.LayerNormalization()(attn)
    grn = gated_residual_network(attn[:, -1, :], units)
    outputs = layers.Dense(1)(grn) 
    model = Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss='mse')
    return model

# --- [ 3. 데이터 준비 함수 ] ---
def get_test_data():
    df = yf.download("005930.KS", period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()
    
    feature_cols = []
    for col in df.columns:
        new_name = f'Log_Ret_{col}'
        df[new_name] = np.log((df[col] + 1e-9) / (df[col].shift(1) + 1e-9))
        feature_cols.append(new_name)
    
    df['actual_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()
    
    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    X, y = [], []
    data, ret = df[feature_cols].values, df['actual_ret'].values
    for i in range(len(df) - 20):
        X.append(data[i:i+20])
        y.append(ret[i+20-1])
    return np.array(X), np.array(y)

# --- [ 4. 메인 테스트 루프 ] ---
def run_full_beast_test():
    print("🔬 Beast V3 실전 모델 재현성 테스트 시작...")
    X, y = get_test_data()
    
    results = []
    for i in range(1, 3):
        print(f"\n▶ Trial {i}: 150 에폭 학습 중...")
        setup_deterministic_env(42) # 매 학습 시작 전 시드 강제 고정
        
        model = build_beast_tft(X.shape[1], X.shape[2])
        # shuffle=False는 재현성 테스트의 핵심입니다.
        model.fit(X, y, epochs=150, batch_size=128, verbose=0, shuffle=False)
        
        # 마지막 데이터에 대한 예측값 저장
        last_input = np.expand_dims(X[-1], axis=0)
        pred = model.predict(last_input, verbose=0)[0][0]
        results.append(pred)
        print(f"Trial {i} 예측 결과: {pred:.10f}")

    # 최종 결과 비교
    print("\n" + "="*50)
    print(f"Trial 1: {results[0]:.10f}")
    print(f"Trial 2: {results[1]:.10f}")
    
    # 소수점 7자리까지 일치하는지 확인
    if np.allclose(results[0], results[1], atol=1e-7):
        print("✅ 결과: Beast V3 재현성 검증 성공!")
    else:
        print("❌ 결과: 재현성 실패. 환경 변수나 연산 엔진을 확인해야 합니다.")
    print("="*50)

if __name__ == "__main__":
    run_full_beast_test()