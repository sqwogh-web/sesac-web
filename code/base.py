import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'seoul-apt-latest.csv')

# seoul-apt-latest.csv 원본 컬럼 -> 요청 컬럼명 매핑
# 건축년도는 원본 CSV에 없는 컬럼이라 빈 값으로 채움
COLUMN_MAP = {
    '자치구명': 'gu',
    '법정동명': 'dong',
    '건물명': 'complex',
    '계약일': 'contract_date',
    '물건금액(만원)': 'price',
    '건물면적': 'area_m2',
    '층': 'floor',
    '건축년도': None,
}


def read_rows(path=CSV_PATH):
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = [
            {col: (row[src] if src else '') for col, src in COLUMN_MAP.items()}
            for row in reader
        ]
    return rows


if __name__ == '__main__':
    rows = read_rows()
    print(f"전체 행 수: {len(rows):,}건")
    for row in rows[:5]:
        print(row)
