import csv
import json
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'seoul-apt-latest.csv')
OUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dashboard_data.json')

BUCKET_SIZE = 10   # m^2
BUCKET_CAP = 200   # anything >= this goes into the "200+" bucket


def area_bucket(area_m2):
    b = int(area_m2 // BUCKET_SIZE * BUCKET_SIZE)
    return min(b, BUCKET_CAP)


def empty_cell():
    return {'count': 0, 'sum_price': 0.0, 'sum_area': 0.0, 'sum_rent': 0.0}


def build():
    # data[gu][deal_type][ym][bucket] = {count, sum_price, sum_area, sum_rent}
    # sum_price holds the up-front capital: 매매가(price) for 매매, 보증금(deposit) for 전세/월세
    # sum_rent holds monthly_rent and is only ever non-zero for 월세
    data = {}
    months = set()

    with open(CSV_PATH, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            deal_type = row['deal_type']
            if deal_type not in ('매매', '전세', '월세'):
                continue
            if not row['area_m2']:
                continue

            gu = row['gu']
            ym = row['contract_ym']
            area = float(row['area_m2'])
            bucket = area_bucket(area)

            if deal_type == '매매':
                if not row['price']:
                    continue
                amount = float(row['price'])
                rent = 0.0
            else:
                if not row['deposit']:
                    continue
                amount = float(row['deposit'])
                rent = float(row['monthly_rent']) if row['monthly_rent'] else 0.0

            months.add(ym)

            gu_slot = data.setdefault(gu, {'매매': {}, '전세': {}, '월세': {}})
            ym_slot = gu_slot[deal_type].setdefault(ym, {})
            cell = ym_slot.setdefault(str(bucket), empty_cell())
            cell['count'] += 1
            cell['sum_price'] += amount
            cell['sum_area'] += area
            cell['sum_rent'] += rent

    result = {
        'meta': {
            'months': sorted(months),
            'bucket_size': BUCKET_SIZE,
            'bucket_cap': BUCKET_CAP,
            'gu_list': sorted(data.keys()),
        },
        'data': data,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))

    return result


if __name__ == '__main__':
    result = build()
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"자치구 수: {len(result['meta']['gu_list'])}")
    print(f"기간: {result['meta']['months'][0]} ~ {result['meta']['months'][-1]}")
    print(f"출력 파일: {OUT_PATH} ({size_kb:.1f} KB)")
