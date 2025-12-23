# datapull/make_fixtures.py
import requests
import json
import os

def run():
    API_KEY = "2fa1b84249e34622ee6cd8fa16c7d6fd"
    URL = "https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
    params = {'auth': API_KEY, 'topFinGrpNo': '020000', 'pageNo': '1'}
    
    response = requests.get(URL, params=params).json()
    result = []

    # 상품 정보 (DepositProducts)
    for base in response['result']['baseList']:
        result.append({
            "model": "finlife.depositproducts",
            "pk": base['fin_prdt_cd'],
            "fields": {
                "fin_prdt_cd": base['fin_prdt_cd'],
                "kor_co_nm": base['kor_co_nm'],
                "fin_prdt_nm": base['fin_prdt_nm'],
                "etc_note": base.get('etc_note'),
                "join_way": base.get('join_way'),
                "spcl_cnd": base.get('spcl_cnd'),
            }
        })

    # 금리 옵션 정보 (DepositOptions)
    for idx, opt in enumerate(response['result']['optionList']):
        result.append({
            "model": "finlife.depositoptions",
            "pk": idx + 1,
            "fields": {
                "product": opt['fin_prdt_cd'], # 외래키 연결
                "fin_prdt_cd": opt['fin_prdt_cd'],
                "save_trm": opt['save_trm'],
                "intr_rate": opt.get('intr_rate'),
                "intr_rate2": opt.get('intr_rate2'),
            }
        })

    # 저장 경로: finlife/fixtures/
    path = '../finlife/fixtures/finlife_data.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print("✅ Fixture 생성 완료!")

if __name__ == "__main__":
    run()