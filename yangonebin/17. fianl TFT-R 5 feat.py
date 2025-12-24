import os
import random
import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model, Input
from sklearn.preprocessing import StandardScaler
import joblib

# [환경 설정]
SEED = 22
os.environ['PYTHONHASHSEED'] = str(SEED)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# --- [ 아키텍처 정의 (호환성 패치 적용) ] ---

def variable_selection_network(x, units, num_features):
    feature_embeddings = []
    for i in range(num_features):
        # ✅ [핵심] i=i 대신 arguments를 사용해야 '원래 서버 코드'에서 에러 없이 로드됩니다.
        feat = layers.Lambda(
            lambda t, idx: t[:, :, idx:idx+1], 
            arguments={'idx': i}
        )(x)
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

# --- [ 학습 실행 ] ---

if __name__ == "__main__":
    print("🚀 [재학습] 파일 생성 시작 (beast_scaler.pkl, beast_tft_full.h5)...")
    
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
    joblib.dump(scaler, 'beast_scaler.pkl') # ✅ 여기서 스케일러 파일 생성
    
    X, y = [], []
    data, ret = df[feature_cols].values, df['actual_ret'].values
    for i in range(len(df) - 20):
        X.append(data[i:i+20])
        y.append(ret[i+20-1])
    X, y = np.array(X), np.array(y)

    model = build_beast_tft(X.shape[1], X.shape[2])
    model.fit(X, y, epochs=150, batch_size=128, verbose=1, shuffle=False)
    
    model.save('beast_tft_full.h5') # ✅ 여기서 모델 파일 생성
    print("\n✅ 파일 생성 완료! 이제 서버 코드를 실행하세요.")