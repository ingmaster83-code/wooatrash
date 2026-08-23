"""공공데이터포털 전국종량제봉투가격표준데이터를 받아 data/envlp_price.json으로 저장

fetch_data.py와 동일한 이유(api.data.go.kr가 GitHub Actions에서만 403)로
www.data.go.kr/download/standard.json 직접 다운로드 방식으로 전환.
"""
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "envlp_price.json"

PUBLIC_DATA_PK = "15025538"
SVC_TABLE_NM = "tn_pubr_public_weighted_envlp_svc"
DOWNLOAD_URL = "https://www.data.go.kr/download/standard.json"
COL_LIST = [
    "CTPRVN_NM", "SIGNGU_NM", "WEIGHTED_ENVLP_TYPE", "WEIGHTED_ENVLP_MTHD",
    "WEIGHTED_ENVLP_PRPOS", "WEIGHTED_ENVLP_TRGET",
    "PRICE_1", "PRICE_1_HALF", "PRICE_2", "PRICE_2_HALF", "PRICE_3", "PRICE_5",
    "PRICE_10", "PRICE_20", "PRICE_30", "PRICE_50", "PRICE_60", "PRICE_75",
    "PRICE_100", "PRICE_120", "PRICE_125",
    "CHRG_DEPT_NM", "PHONE_NUMBER", "REFERENCE_DATE",
]
PER_PAGE = 10000

SIZE_FIELDS = [
    ("PRICE_1", "1L"), ("PRICE_1_HALF", "1.5L"), ("PRICE_2", "2L"), ("PRICE_2_HALF", "2.5L"),
    ("PRICE_3", "3L"), ("PRICE_5", "5L"), ("PRICE_10", "10L"), ("PRICE_20", "20L"),
    ("PRICE_30", "30L"), ("PRICE_50", "50L"), ("PRICE_60", "60L"), ("PRICE_75", "75L"),
    ("PRICE_100", "100L"), ("PRICE_120", "120L"), ("PRICE_125", "125L"),
]

FIELD_MAP = {
    "CTPRVN_NM": "시도명",
    "SIGNGU_NM": "시군구명",
    "WEIGHTED_ENVLP_TYPE": "봉투종류",
    "WEIGHTED_ENVLP_MTHD": "처리방식",
    "WEIGHTED_ENVLP_PRPOS": "용도",
    "WEIGHTED_ENVLP_TRGET": "사용대상",
    "CHRG_DEPT_NM": "관리부서명",
    "PHONE_NUMBER": "관리부서전화번호",
    "REFERENCE_DATE": "데이터기준일자",
}


def normalize(item):
    out = {}
    for api_key, kor_key in FIELD_MAP.items():
        v = item.get(api_key, "")
        if v is None or v == "null":
            v = ""
        out[kor_key] = v
    prices = {}
    for api_key, label in SIZE_FIELDS:
        v = item.get(api_key, "0")
        try:
            n = int(str(v).replace(",", "") or "0")
        except ValueError:
            n = 0
        if n > 0:
            prices[label] = n
    out["가격"] = prices
    return out


def fetch_all():
    all_records = []
    page = 1
    while True:
        params = [("publicDataPk", PUBLIC_DATA_PK)]
        params += [("colNmList", c) for c in COL_LIST]
        params += [
            ("perPage", PER_PAGE),
            ("page", page),
            ("svcTableNm", SVC_TABLE_NM),
            ("totalCount", "999999"),
        ]
        resp = requests.get(DOWNLOAD_URL, params=params, timeout=30)
        resp.raise_for_status()
        items = resp.json()

        if not items:
            break

        all_records.extend(normalize(it) for it in items)
        print(f"  {page}페이지 완료 (누적 {len(all_records)}건)")

        if len(items) < PER_PAGE:
            break
        page += 1
        time.sleep(0.3)

    return all_records


def main():
    print("전국종량제봉투가격 수집 시작...")
    records = fetch_all()
    print(f"총 {len(records)}건 수집 완료")

    if OUT_PATH.exists():
        existing = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        if len(records) < len(existing) * 0.5:
            raise SystemExit(
                f"수집 건수({len(records)}건)가 기존 데이터({len(existing)}건)의 절반 미만입니다. "
                "API 오류로 판단하여 저장을 중단합니다."
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
