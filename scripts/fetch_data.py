"""공공데이터포털 전국대형폐기물수거수수료정보표준데이터 API에서 전체 데이터를 받아 data/trash_fee.json으로 저장"""
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "trash_fee.json"

API_URL = "https://api.data.go.kr/openapi/tn_pubr_public_lar_was_fee_api"
SERVICE_KEY = os.environ.get("DATA_GO_KR_API_KEY", "")
NUM_OF_ROWS = 1000


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

        body = data.get("response", {}).get("body", {})
        items = body.get("items", [])
        if isinstance(items, dict):
            items = items.get("item", [])
        if isinstance(items, dict):
            items = [items]

        if not items:
            break

        all_records.extend(items)
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

    print("전국대형폐기물수거수수료정보 수집 시작...")
    records = fetch_all()
    print(f"총 {len(records)}건 수집 완료")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
