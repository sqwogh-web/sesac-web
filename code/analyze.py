import csv
import os
from collections import defaultdict

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'seoul-apt-latest.csv')


def load_gu_stats(path=CSV_PATH):
    sale_prices = defaultdict(list)     # gu -> [매매가(만원), ...]
    jeonse_deposits = defaultdict(list)  # gu -> [전세보증금(만원), ...]

    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gu = row['gu']
            if row['deal_type'] == '매매' and row['price']:
                sale_prices[gu].append(float(row['price']))
            elif row['deal_type'] == '전세' and row['deposit']:
                jeonse_deposits[gu].append(float(row['deposit']))

    stats = {}
    for gu in set(sale_prices) & set(jeonse_deposits):
        avg_sale = sum(sale_prices[gu]) / len(sale_prices[gu])
        avg_jeonse = sum(jeonse_deposits[gu]) / len(jeonse_deposits[gu])
        stats[gu] = {
            'avg_sale_eok': avg_sale / 10000,
            'avg_jeonse_eok': avg_jeonse / 10000,
            'diff_eok': (avg_sale - avg_jeonse) / 10000,
        }
    return stats


def print_table(rows):
    header = f"{'자치구':<8}{'평균 매매가(억)':>16}{'평균 전세보증금(억)':>18}{'매매-전세(억)':>16}"
    print(header)
    print('-' * len(header))
    for gu, s in rows:
        print(f"{gu:<8}{s['avg_sale_eok']:>16.2f}{s['avg_jeonse_eok']:>18.2f}{s['diff_eok']:>16.2f}")


if __name__ == '__main__':
    stats = load_gu_stats()

    ranked = sorted(stats.items(), key=lambda kv: kv[1]['diff_eok'], reverse=True)

    print("[매매-전세 차이 Top 5 자치구]")
    print_table(ranked[:5])

    print()
    print("[중랑구]")
    print_table([('중랑구', stats['중랑구'])])
