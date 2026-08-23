"""공공데이터포털 전국대형폐기물수거수수료정보표준데이터를 받아 data/trash_fee.json으로 저장

기존에는 api.data.go.kr(구버전 오픈API, serviceKey 인증)를 썼는데 GitHub Actions에서만
403 Forbidden이 발생해(로컬/다른 환경에서는 동일 키로 정상 동작 확인, 2026-08-23) 데이터가
7/9부터 갱신이 안 되고 있었음. IP 차단으로 추정되어, data.go.kr 포털 자체가 제공하는
표준데이터셋 다운로드 엔드포인트(www.data.go.kr/download/standard.json, 인증키 불필요)로
전환. 이 방식은 wooasports의 전국공공시설개방정보표준데이터 병합 때도 사용해 검증됨.
"""
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
OUT_PATH = ROOT / "data" / "trash_fee.json"

PUBLIC_DATA_PK = "15114146"
SVC_TABLE_NM = "tn_pubr_public_lar_was_fee_svc"
DOWNLOAD_URL = "https://www.data.go.kr/download/standard.json"
COL_LIST = [
    "CTPV_NM", "SGG_NM", "LAR_WAS_NM", "LAR_WAS_SE_NM", "LAR_WAS_SPCFCT",
    "PAID_FREE_YN", "FEE", "MNG_INST_NM", "CRTR_YMD",
]
PER_PAGE = 5000

FIELD_MAP = {
    "CTPV_NM": "시도명",
    "SGG_NM": "시군구명",
    "LAR_WAS_NM": "대형폐기물명",
    "LAR_WAS_SE_NM": "대형폐기물구분명",
    "LAR_WAS_SPCFCT": "대형폐기물규격",
    "PAID_FREE_YN": "유무료여부",
    "FEE": "수수료",
    "MNG_INST_NM": "관리기관명",
    "CRTR_YMD": "데이터기준일자",
    "INSTT_CODE": "제공기관코드",
    "INSTT_NM": "제공기관명",
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
            ("totalCount", "999999"),  # 실제 값은 무시되고 페이지네이션에만 쓰이는 파라미터
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
    print("전국대형폐기물수거수수료정보 수집 시작...")
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
