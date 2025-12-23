import pandas as pd
import os

# 파일 경로 설정 (backend/data 폴더 안에 있다고 가정)
base_dir = 'data' # 만약 backend/data라면 'backend/data'로 수정하세요
files = {
    'Gold': 'Gold_prices.xlsx',
    'Silver': 'Silver_prices.xlsx'
}

def clean_file(name, filename):
    path = os.path.join(base_dir, filename)
    
    if not os.path.exists(path):
        print(f"❌ {filename} 파일을 찾을 수 없습니다.")
        return

    print(f"🔄 {name} 데이터 정리 중...")
    
    try:
        # 엑셀 읽기
        df = pd.read_excel(path)
        
        # 1. 날짜 컬럼 통일 (Date -> date)
        # 컬럼 중에 'date'가 포함된 것이 있으면 그것을 'date'로 변경
        date_col = next((c for c in df.columns if 'date' in str(c).lower()), None)
        if date_col:
            df = df.rename(columns={date_col: 'date'})
            # 날짜 포맷 통일 (YYYY-MM-DD)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # 2. 가격 컬럼 통일 (Close/Last 등 -> price)
        # 'Close'나 'USD'가 들어간 컬럼을 찾거나, 두 번째 컬럼을 가격으로 가정
        price_col = next((c for c in df.columns if 'close' in str(c).lower() or 'usd' in str(c).lower()), df.columns[1])
        df = df.rename(columns={price_col: 'price'})

        # 3. 쉼표 제거 및 숫자 변환 (가장 중요한 부분!)
        if df['price'].dtype == 'object':
            df['price'] = df['price'].astype(str).str.replace(',', '').astype(float)
            
        # 4. 필요한 컬럼만 남기고 저장
        final_df = df[['date', 'price']]
        final_df.to_excel(path, index=False)
        print(f"✅ {name} 완료! (쉼표 제거 및 컬럼명 통일됨)")
        print(final_df.head())
        print("-" * 30)
        
    except Exception as e:
        print(f"⚠️ 에러 발생 ({filename}): {e}")

# 실행
if __name__ == '__main__':
    # 폴더가 없으면 생성 (혹시 모르니)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"매뉴얼: {base_dir} 폴더 안에 엑셀 파일들을 넣어주세요.")
    else:
        clean_file('Gold', files['Gold'])
        clean_file('Silver', files['Silver'])