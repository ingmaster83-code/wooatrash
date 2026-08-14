"""공공데이터포털 전국종량제봉투가격표준데이터 API에서 전체 데이터를 받아 data/envlp_price.json으로 저장"""
import json
import os
import time
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "envlp_price.json"

API_URL = "https://api.data.go.kr/openapi/tn_pubr_public_weighted_envlp_api"
SERVICE_KEY = os.environ.get("DATA_GO_KR_API_KEY", "")
NUM_OF_ROWS = 1000

SIZE_FIELDS = [
    ("price1", "1L"), ("price1Half", "1.5L"), ("price2", "2L"), ("price2Half", "2.5L"),
    ("price3", "3L"), ("price5", "5L"), ("price10", "10L"), ("price20", "20L"),
    ("price30", "30L"), ("price50", "50L"), ("price60", "60L"), ("price75", "75L"),
    ("price100", "100L"), ("price120", "120L"), ("price125", "125L"),
]

FIELD_MAP = {
    "ctprvnNm": "시도명",
    "signguNm": "시군구명",
    "weightedEnvlpType": "봉투종류",
    "weightedEnvlpMthd": "처리방식",
    "weightedEnvlpPrpos": "용도",
    "weightedEnvlpTrget": "사용대상",
    "chrgDeptNm": "관리부서명",
    "phoneNumber": "관리부서전화번호",
    "referenceDate": "데이터기준일자",
    "insttCode": "제공기관코드",
    "insttNm": "제공기관명",
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
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": page,
            "numOfRows": NUM_OF_ROWS,
            "type": "json",
        }
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        header = data.get("header", {})
        if header.get("resultCode") not in (None, "00"):
            raise SystemExit(f"API 오류: {header}")

        body = data.get("body", {})
        items = body.get("items", [])
        if isinstance(items, dict):
            items = items.get("item", [])
        if isinstance(items, dict):
            items = [items]

        if not items:
            break

        all_records.extend(normalize(it) for it in items)
        print(f"  {page}페이지 완료 (누적 {len(all_records)}건)")

        total = int(body.get("totalCount", 0))
        if len(all_records) >= total or len(items) < NUM_OF_ROWS:
            break
        page += 1
        time.sleep(0.2)

    return all_records


def main():
    if not SERVICE_KEY:
        raise SystemExit("DATA_GO_KR_API_KEY 환경변수가 설정되지 않았습니다.")

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
