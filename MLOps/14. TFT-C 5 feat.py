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

# 환경 설정 및 로그 제어
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

# --- [1. TFT 커스텀 블록 정의] ---
def gated_residual_network(x, units, dropout_rate=0.1):
    h = layers.Dense(units, activation='elu')(x)
    h = layers.Dense(units)(h)
    h = layers.Dropout(dropout_rate)(h)
    gate = layers.Dense(units, activation='sigmoid')(x)
    x = layers.Add()([x, layers.Multiply()([gate, h])])
    return layers.LayerNormalization()(x)

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

# --- [2. TFT Classifier 아키텍처] ---
def build_beast_tft_classifier(window_size, num_features, units=64):
    inputs = Input(shape=(window_size, num_features))
    vsn = variable_selection_network(inputs, units, num_features)
    
    lstm = layers.LSTM(units, return_sequences=True)(vsn)
    attn = layers.MultiHeadAttention(num_heads=4, key_dim=units)(lstm, lstm)
    attn = layers.Add()([lstm, attn])
    attn = layers.LayerNormalization()(attn)
    
    grn = gated_residual_network(attn[:, -1, :], units)
    # 분류 모델: Sigmoid 활성화 함수
    outputs = layers.Dense(1, activation='sigmoid')(grn)
    
    model = Model(inputs, outputs)
    # 분류 모델: Binary Crossentropy 손실 함수
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss='binary_crossentropy', metrics=['accuracy'])
    return model

# --- [3. 데이터 로드 및 전처리] ---
def load_beast_data():
    print("\n>>> [1/3] 데이터 다운로드 시작 (삼성전자)...")
    df = yf.download("005930.KS", period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].ffill()
    
    print(">>> [2/3] 피처 엔지니어링 및 로그 변환 수행 중...")
    features = []
    for col in df.columns:
        name = f'LR_{col}'
        df[name] = np.log((df[col] + 1e-9) / (df[col].shift(1) + 1e-9))
        features.append(name)
    
    # 분류 타겟: 내일 상승 여부
    df['target_up'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    # ROI 계산용 실제 수익률
    df['actual_ret'] = df['Close'].shift(-1) / df['Close'] - 1
    
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    
    for col in features:
        df[col] = StandardScaler().fit_transform(df[[col]])
    
    print(f">>> [3/3] 전처리 완료: 총 {len(df)}개의 데이터 포인트를 확보했습니다.")
    return df, features

def create_sequences(df, features, window=20):
    X, y, r = [], [], []
    data_values = df[features].values
    target_values = df['target_up'].values
    ret_values = df['actual_ret'].values
    for i in range(len(df) - window):
        X.append(data_values[i:i+window])
        y.append(target_values[i+window-1])
        r.append(ret_values[i+window-1])
    return np.array(X), np.array(y), np.array(r)

# --- [4. 메인 실행 루프] ---
if __name__ == "__main__":
    df, features = load_beast_data()
    X, y, r = create_sequences(df, features)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    r_test = r[split:]
    
    mlflow.set_experiment("Beast_TFT_Classifier_5Feat_Final")
    
    roi_results, buy_counts = [], []

    print(f"\n🚀 [SOTA] TFT 5-Feature Classifier 30회 실험 시작")
    print("="*80)

    for seed in range(30):
        start_time = time.time()
        with mlflow.start_run(run_name=f"TFT_Class_Seed_{seed}"):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            print(f"\n[Seed {seed:2d}] 모델 빌드 및 학습 준비...")
            model = build_beast_tft_classifier(X.shape[1], X.shape[2])
            es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
            
            # verbose=1로 설정하여 터미널에 학습 과정 출력
            print(f"[Seed {seed:2d}] 학습 중 (Max 150 Epochs)...")
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=150, batch_size=128, verbose=1, callbacks=[es])
            
            # 예측 및 시뮬레이션
            preds = model.predict(X_test, verbose=0).flatten()
            balance = 10000000
            buy_count = 0
            for i in range(len(preds)):
                if preds[i] > 0.5: # 50% 확률 이상 시 매수
                    balance *= (1 + r_test[i])
                    buy_count += 1
            
            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            buy_counts.append(buy_count)
            
            mlflow.log_metric("roi", final_roi)
            mlflow.log_metric("buy_count", buy_count)
            
            duration = time.time() - start_time
            print(f"\n✅ [Seed {seed:2d} 완료] ROI: {final_roi:8.2f}% | Buy: {buy_count:4d}회 | 소요시간: {duration:.1f}s")
            print("-" * 80)

    # --- 최종 결과 요약 리포트 ---
    print("\n" + "🏆" * 10 + " [TFT Classifier SOTA 최종 리포트] " + "🏆" * 10)
    print(f" 📊 분석 대상: 30회 독립 시행 (Seed 0~29)")
    print(f" 📈 평균 ROI: {np.mean(roi_results):.4f}%")
    print(f" 🔄 평균 매매 횟수: {np.mean(buy_counts):.2f}회")
    print("-" * 65)
    print(f" 🔥 최고 ROI (Seed {np.argmax(roi_results)}): {np.max(roi_results):.2f}%")
    print(f" ❄️ 최저 ROI (Seed {np.argmin(roi_results)}): {np.min(roi_results):.2f}%")
    print("=" * 65)