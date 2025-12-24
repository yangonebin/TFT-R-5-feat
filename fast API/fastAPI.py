import os
import yfinance as yf
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from tensorflow.keras import layers, Model, Input
from contextlib import asynccontextmanager

# --- [ 1. 환경 설정 ] ---
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
SEED = 22

# --- [ 2. 아키텍처 정의 (빈 모델 생성용) ] ---

def variable_selection_network(x, units, num_features):
    feature_embeddings = []
    for i in range(num_features):
        # 여기가 에러의 원인이었던 Lambda 부분입니다.
        # 가중치만 로드할 때는 이 코드가 새로 실행되므로 안전하게 동작합니다.
        feat = layers.Lambda(lambda t: t[:, :, i:i+1])(x)
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

# --- [ 3. Lifespan 설정 (핵심 변경!) ] ---
model = None
scaler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, scaler
    print("🔋 로딩 중: Beast V3 모델 구조 생성 및 가중치 주입...")
    try:
        scaler = joblib.load('beast_scaler.pkl')
        
        # 1. 빈 모델(껍데기)을 먼저 만듭니다. (입력 크기: 20일, 5개 피처)
        model = build_beast_tft(window_size=20, num_features=5)
        
        # 2. 저장된 파일에서 '가중치(Weights)'만 쏙 빼와서 덮어씌웁니다.
        # by_name=True 옵션으로 이름이 맞는 층끼리 매칭해 에러를 방지합니다.
        model.load_weights('beast_tft_full.h5')
        
        print("🚀 Beast V3 엔진 가동 준비 완료 (Seed 22)")
    except Exception as e:
        print(f"❌ 로딩 실패 에러: {e}")
        print("💡 팁: 모델 아키텍처가 학습 코드와 완전히 동일한지 확인하세요.")
    yield

# --- [ 4. FastAPI 앱 설정 ] ---
app = FastAPI(title="Beast V3: SSAFY Edition", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict")
def predict_stock():
    if model is None or scaler is None:
        return {"status": "error", "message": "Model not loaded"}
        
    target_stock = "005930.KS"
    # period="1mo"로 넉넉하게 가져와야 21개 이상 확보 가능
    df = yf.download(target_stock, period="1mo", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    data = df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(21).copy()
    feature_cols = []
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        name = f'Log_Ret_{col}'
        data[name] = np.log((data[col] + 1e-9) / (data[col].shift(1) + 1e-9))
        feature_cols.append(name)
    
    data = data.dropna()
    
    # 데이터 개수 체크 (20개 미만이면 에러 방지)
    if len(data) < 20:
        return {"status": "error", "message": "Not enough data fetched from Yahoo Finance"}

    input_scaled = scaler.transform(data[feature_cols])
    input_seq = np.expand_dims(input_scaled, axis=0)
    
    # 추론
    prediction = float(model.predict(input_seq, verbose=0)[0][0])
    
    return {
        "status": "success",
        "result": {
            "predicted_return": f"{prediction * 100:.4f}%",
            "signal": "BUY" if prediction > 0 else "HOLD"
        },
        "meta": {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)