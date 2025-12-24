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

# 🏆 검증 최고 수익률 시드 (15) 적용
SEED = 15
os.environ['PYTHONHASHSEED'] = str(SEED)
tf.random.set_seed(SEED)
np.random.seed(SEED)

# --- TFT를 위한 핵심 커스텀 블록 ---
def gated_residual_network(x, units, dropout_rate=0.1):
    h = layers.Dense(units, activation='elu')(x)
    h = layers.Dense(units)(h)
    h = layers.Dropout(dropout_rate)(h)
    gate = layers.Dense(units, activation='sigmoid')(x)
    x = layers.Add()([x, layers.Multiply()([gate, h])])
    return layers.LayerNormalization()(x)

# --- [VSN 함수] ---
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

# --- 데이터 빌더 (Bitcoin 전용) ---
def build_tft_data():
    target_stock = "BTC-USD"
    print(f"📥 {target_stock} 데이터 다운로드 중...")
    
    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill().dropna()
    feature_cols = []
    
    # 나중에 최신 데이터 추론을 위해 원본 데이터 보존
    global df_raw
    df_raw = df.copy()

    for col in df.columns:
        new_name = f'Log_Ret_{col}'
        df[new_name] = np.log((df[col] + 1e-9) / (df[col].shift(1) + 1e-9))
        feature_cols.append(new_name)
    
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    df['actual_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()
    
    scaler = StandardScaler()
    # feature_cols 전체에 대해 fit_transform
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    # 스케일러를 나중에 쓰기 위해 전역 변수나 리턴값으로 저장
    global trained_scaler
    trained_scaler = scaler
    
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

if __name__ == "__main__":
    # 1. 데이터 준비
    df, features = build_tft_data()
    X, y, r = create_sequences(df, features)
    
    # 2. 한빈님이 원하신 그대로 Split 및 파라미터 유지
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = r[:split], r[split:] 
    
    print(f"\n🚀 [Beast V3] 비트코인 학습 시작 (Epochs: 150, ES: 15)...")
    
    # 3. 모델 빌드 및 학습 (Validation Data 포함 유지)
    model = build_beast_tft(X.shape[1], X.shape[2])
    es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    
    model.fit(X_train, y_train, validation_data=(X_test, y_test), 
              epochs=150, batch_size=128, verbose=1, callbacks=[es])
    
    print("✅ 학습 완료. 내일 예측을 시작합니다.")

    # --- [실전 예측: 내일 비트코인 살까 말까?] ---
    
    # 1. 가장 최신 20일치 데이터 가져오기 (df_raw 사용)
    last_20_days = df_raw.tail(21).copy() # shift 계산 위해 21개 필요
    
    recent_features = pd.DataFrame()
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        new_name = f'Log_Ret_{col}'
        recent_features[new_name] = np.log((last_20_days[col] + 1e-9) / (last_20_days[col].shift(1) + 1e-9))
    
    # NaN 제거 후 마지막 20개만 남김
    recent_features = recent_features.dropna().tail(20)
    
    # 2. 학습 때 쓴 스케일러로 변환
    input_data = trained_scaler.transform(recent_features)
    input_seq = np.expand_dims(input_data, axis=0) # (1, 20, 5)
    
    # 3. 예측
    prediction = float(model.predict(input_seq, verbose=0)[0][0])
    pred_percent = prediction * 100
    
    # 4. 결과 출력 (심플하게)
    current_price = df_raw['Close'].iloc[-1]
    
    print("\n" + "="*40)
    print(f"💰 현재 비트코인 가격: ${current_price:,.2f}")
    print(f"🎯 내일 예상 수익률 : {pred_percent:+.4f}%")
    print("-" * 40)
    
    if prediction > 0:
        print("🔥 [결론] : 사라 (BUY)")
    else:
        print("❄️ [결론] : 팔아라 (SELL/HOLD)")
    print("="*40)