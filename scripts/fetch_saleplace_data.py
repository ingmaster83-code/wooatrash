# -*- coding: utf-8 -*-
"""공공데이터포털 전국종량제봉투판매소표준데이터를 받아 data/saleplace.json으로 저장

fetch_data.py와 동일한 이유(api.data.go.kr가 GitHub Actions에서만 403)로
www.data.go.kr/download/standard.json 직접 다운로드 방식으로 전환.
"""
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "saleplace.json"

PUBLIC_DATA_PK = "15114144"
SVC_TABLE_NM = "tn_pubr_public_std_gar_bag_svc"
DOWNLOAD_URL = "https://www.data.go.kr/download/standard.json"
COL_LIST = [
    "STO_NM", "CTPV_NM", "SGG_NM", "LCTN_ROAD_NM_ADDR", "LCTN_LOTNO_ADDR",
    "LAT", "LOT", "LAR_WAS_STI_YN", "BUSI_COD_NM", "TELNO", "MNG_INST_NM", "CRTR_YMD",
]
PER_PAGE = 10000

FIELD_MAP = {
    "STO_NM": "판매소명",
    "CTPV_NM": "시도명",
    "SGG_NM": "시군구명",
    "LCTN_ROAD_NM_ADDR": "도로명주소",
    "LCTN_LOTNO_ADDR": "지번주소",
    "LAT": "위도",
    "LOT": "경도",
    "LAR_WAS_STI_YN": "대형폐기물스티커판매여부",
    "BUSI_COD_NM": "영업상태명",
    "TELNO": "전화번호",
    "MNG_INST_NM": "관리기관명",
    "CRTR_YMD": "데이터기준일자",
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
