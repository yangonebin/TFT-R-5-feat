import os
import django
import sqlite3
import sys


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "final_pjt.settings") # ⚠️ 프로젝트명 확인 (final_pjt가 맞는지)
django.setup()

from finlife.models import Product
from django.conf import settings

base_dir = settings.BASE_DIR


root_dir = os.path.dirname(base_dir)

source_db_path = os.path.join(root_dir, 'service_data.db')

print(f"📂 Django DB 위치: {settings.DATABASES['default']['NAME']}")
print(f"📂 원본 데이터 위치: {source_db_path}")

def load_data():
    if not os.path.exists(source_db_path):
        print(f"❌ 에러: {source_db_path} 경로에서 파일을 찾을 수 없습니다.")
        print("👉 파일이 FINAL-PJT(최상위) 폴더에 있는지 확인해주세요.")
        return

    try:

        conn = sqlite3.connect(source_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        
        print(f"🚀 {len(rows)}개의 데이터를 발견했습니다! 저장을 시작합니다...")

    
        for row in rows:
       
            try:
                Product.objects.get_or_create(
                    fin_prdt_nm=row[0],
                    defaults={
                        'kor_co_nm': row[1],
                        'intr_rate': row[2],
                        'intr_rate2': row[3],
                        'save_trm': row[4]
                    }
                )
            except Exception as e:
                print(f"⚠️ 데이터 저장 건너뜀 ({row[0]}): {e}")
        
        print("✅ 데이터 이동 완료! 이제 서버를 켜서 확인해보세요.")

    except Exception as e:
        print("❌ 에러 발생:", e)
        print("힌트: models.py에 db_table='products'가 있는지 확인해보세요.")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    load_data()