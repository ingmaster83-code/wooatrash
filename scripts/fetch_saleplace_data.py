# -*- coding: utf-8 -*-
"""공공데이터포털 전국종량제봉투판매소표준데이터 API에서 전체 데이터를 받아 data/saleplace.json으로 저장"""
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
OUT_PATH = ROOT / "data" / "saleplace.json"

API_URL = "https://api.data.go.kr/openapi/tn_pubr_public_std_gar_bag_api"
SERVICE_KEY = os.environ.get("DATA_GO_KR_API_KEY", "")
NUM_OF_ROWS = 1000

FIELD_MAP = {
    "stoNm": "판매소명",
    "ctpvNm": "시도명",
    "sggNm": "시군구명",
    "lctnRoadNmAddr": "도로명주소",
    "lctnLotnoAddr": "지번주소",
    "lat": "위도",
    "lot": "경도",
    "larWasStiYn": "대형폐기물스티커판매여부",
    "busiCodNm": "영업상태명",
    "telno": "전화번호",
    "mngInstNm": "관리기관명",
    "crtrYmd": "데이터기준일자",
}


def normalize(item):
    out = {}
    for api_key, kor_key in FIELD_MAP.items():
        v = item.get(api_key, "")
        if v is None or v == "null":
            v = ""
        out[kor_key] = v
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

    print("전국종량제봉투판매소 수집 시작...")
    records = fetch_all()
    print(f"총 {len(records)}건 수집 완료")

    # 영업중인 곳만 유지 (영업상태명이 "폐업" 등인 경우 제외)
    active = [r for r in records if r.get("영업상태명", "") in ("", "영업", "정상")]
    print(f"영업중 {len(active)}건 (전체 {len(records)}건 중)")

    if OUT_PATH.exists():
        existing = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        if len(active) < len(existing) * 0.5:
            raise SystemExit(
                f"수집 건수({len(active)}건)가 기존 데이터({len(existing)}건)의 절반 미만입니다. "
                "API 오류로 판단하여 저장을 중단합니다."
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(active, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
