"""공공데이터포털 전국재활용센터표준데이터를 받아 data/recycle_center.json으로 저장

fetch_data.py와 동일한 이유(api.data.go.kr가 GitHub Actions에서만 403)로
www.data.go.kr/download/standard.json 직접 다운로드 방식 사용.
"""
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "recycle_center.json"

PUBLIC_DATA_PK = "15021108"
SVC_TABLE_NM = "tn_pubr_public_ruse_cnter_svc"
DOWNLOAD_URL = "https://www.data.go.kr/download/standard.json"
COL_LIST = [
    "CNTER_NM", "CNTER_OPER_SE", "RDNMADR", "LNMADR", "LATITUDE", "LONGITUDE",
    "AR", "FOND_YM", "CAR_HOLD_CO", "TRTMNT_PRDLST",
    "OPER_INSTITUTION_NM", "OPER_PHONE_NUMBER", "RPRSNTV_NM",
    "WEEKDAY_OPER_OPEN_HHMM", "WEEKDAY_OPER_COLSE_HHMM",
    "HOLIDAY_OPER_OPEN_HHMM", "HOLIDAY_CLOSE_OPEN_HHMM",
    "RSTDE_INFO", "AS_SVC_IFO", "HOMEPAGE_URL",
    "PHONE_NUMBER", "INSTITUTION_NM", "REFERENCE_DATE",
]
PER_PAGE = 10000

FIELD_MAP = {
    "CNTER_NM": "재활용센터명",
    "CNTER_OPER_SE": "운영구분",
    "RDNMADR": "소재지도로명주소",
    "LNMADR": "소재지지번주소",
    "LATITUDE": "위도",
    "LONGITUDE": "경도",
    "AR": "면적",
    "FOND_YM": "설립연월",
    "CAR_HOLD_CO": "차량보유대수",
    "TRTMNT_PRDLST": "주요취급품목",
    "OPER_INSTITUTION_NM": "운영기관명",
    "OPER_PHONE_NUMBER": "운영기관전화번호",
    "RPRSNTV_NM": "운영기관대표자명",
    "WEEKDAY_OPER_OPEN_HHMM": "평일운영시작시각",
    "WEEKDAY_OPER_COLSE_HHMM": "평일운영종료시각",
    "HOLIDAY_OPER_OPEN_HHMM": "공휴일운영시작시각",
    "HOLIDAY_CLOSE_OPEN_HHMM": "공휴일운영종료시각",
    "RSTDE_INFO": "휴무일정보",
    "AS_SVC_IFO": "AS서비스정보",
    "HOMEPAGE_URL": "홈페이지주소",
    "PHONE_NUMBER": "관리기관전화번호",
    "INSTITUTION_NM": "관리기관명",
    "REFERENCE_DATE": "데이터기준일자",
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
    print("전국재활용센터 수집 시작...")
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
