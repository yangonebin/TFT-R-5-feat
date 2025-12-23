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

# 환경 설정
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

# --- [1. TFT 커스텀 블록] ---
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

# --- [2. TFT Regressor 아키텍처] ---
def build_beast_tft(window_size, num_features, units=64):
    inputs = Input(shape=(window_size, num_features))
    vsn = variable_selection_network(inputs, units, num_features)
    lstm = layers.LSTM(units, return_sequences=True)(vsn)
    attn = layers.MultiHeadAttention(num_heads=4, key_dim=units)(lstm, lstm)
    attn = layers.Add()([lstm, attn])
    attn = layers.LayerNormalization()(attn)
    grn = gated_residual_network(attn[:, -1, :], units)
    outputs = layers.Dense(1)(grn)
    model = Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss='mse')
    return model

# --- [3. 데이터 마트 (Simple Return 타겟)] ---
def build_data_mart_v4_tft():
    print(">>> [Step 1] 14개 피처(일목균형표 포함) 마트 구축 시작")
    target_stock = "005930.KS" 
    macro_symbols = { "USD_KRW": "KRW=X", "Gold": "GC=F", "Interest_Rate": "^TNX" }

    df = yf.download(target_stock, period="max", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    for name, symbol in macro_symbols.items():
        macro = yf.download(symbol, period="max", auto_adjust=True, progress=False)
        if isinstance(macro.columns, pd.MultiIndex): macro.columns = macro.columns.get_level_values(0)
        df[name] = macro['Close']
    df = df.ffill()

    # 일목균형표 피처 생성
    nine_high, nine_low = df['High'].rolling(9).max(), df['Low'].rolling(9).min()
    df['tenkan_sen'] = (nine_high + nine_low) / 2
    twenty_six_high, twenty_six_low = df['High'].rolling(26).max(), df['Low'].rolling(26).min()
    df['kijun_sen'] = (twenty_six_high + twenty_six_low) / 2
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    fifty_two_high, fifty_two_low = df['High'].rolling(52).max(), df['Low'].rolling(52).min()
    df['senkou_span_b'] = ((fifty_two_high + fifty_two_low) / 2).shift(26)
    df['cloud_thickness'] = df['senkou_span_a'] - df['senkou_span_b']
    df['dist_from_kijun'] = df['Close'] - df['kijun_sen']

    feature_cols = []
    # 모든 지표를 로그 수익률화 하여 피처로 사용
    price_cols = ['Close', 'Open', 'High', 'Low', 'Volume', 'USD_KRW', 'Gold', 'Interest_Rate', 
                  'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b']
    for col in price_cols:
        new_name = f'Log_Ret_{col}'
        df[new_name] = np.log((df[col] + 1e-9) / (df[col].shift(1) + 1e-9))
        feature_cols.append(new_name)
    
    feature_cols.extend(['cloud_thickness', 'dist_from_kijun'])
    
    # ★ [Target] 로그가 아닌 단순 수익률(Actual Return)
    df['target_simple_ret'] = (df['Close'].shift(-1) / df['Close']) - 1
    df = df.dropna()
    
    for col in feature_cols:
        df[col] = StandardScaler().fit_transform(df[[col]])
    return df, feature_cols

def create_sequences(df, feature_cols, window_size=20):
    X, y = [], []
    data_array, target_array = df[feature_cols].values, df['target_simple_ret'].values
    for i in range(len(df) - window_size):
        X.append(data_array[i : i + window_size])
        y.append(target_array[i + window_size - 1])
    return np.array(X), np.array(y)

# --- [4. 메인 실행] ---
if __name__ == "__main__":
    df, features = build_data_mart_v4_tft()
    X, y = create_sequences(df, features)
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:] # 단순 수익률로 학습

    mlflow.set_experiment("Samsung_SOTA_TFT_14Feat_SimpleReturn_Final")
    roi_results, buy_counts = [], []

    print(f"\n🚀 [SOTA] TFT 14-Feature (Simple Return 타겟) 실험 시작")
    print("="*70)

    for seed in range(30):
        start_t = time.time()
        with mlflow.start_run(run_name=f"TFT_14F_Simple_Seed_{seed}"):
            tf.random.set_seed(seed)
            np.random.seed(seed)
            
            model = build_beast_tft(X_train.shape[1], X_train.shape[2])
            es = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
            
            print(f"\n[Seed {seed:2d}] 학습 중 (Max 150 Epochs, Batch 128)")
            model.fit(X_train, y_train, validation_data=(X_test, y_test), 
                      epochs=150, batch_size=128, verbose=1, shuffle=False, callbacks=[es])
            
            preds = model.predict(X_test, verbose=0).flatten()
            
            # 292% 모델과 동일한 시뮬레이션 로직 (상승 예측 시 무조건 매수)
            balance, buy_count = 10000000, 0
            for i in range(len(preds)):
                if preds[i] > 0:
                    balance *= (1 + y_test[i])
                    buy_count += 1
            
            final_roi = ((balance - 10000000) / 10000000) * 100
            roi_results.append(final_roi)
            buy_counts.append(buy_count)
            
            mlflow.log_metric("final_roi", final_roi)
            print(f"✨ Seed {seed:2d} | ROI: {final_roi:8.2f}% | Buy: {buy_count:4d}")

    # --- 최종 결과 출력 ---
    print("\n" + "="*60)
    print(f"🏆 [TFT 14-Feat Simple-Return 리포트]")
    print(f" - 30회 평균 ROI: {np.mean(roi_results):.4f}%")
    print(f" - 30회 평균 매매 횟수: {np.mean(buy_counts):.2f}회")
    print("-" * 60)
    print(f" 🔥 최고 ROI (Seed {np.argmax(roi_results)}): {np.max(roi_results):.2f}%")
    print(f" ❄️ 최저 ROI (Seed {np.argmin(roi_results)}): {np.min(roi_results):.2f}%")
    print("="*60)