# -*- coding: utf-8 -*-
"""전국대형폐기물수거수수료정보 -> HTML 페이지 생성"""
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "trash_fee.json"
SAMPLE_PATH = ROOT / "data" / "trash_fee_sample.json"
DOCS_DIR = ROOT / "docs"
REGION_DIR = DOCS_DIR / "지역"
BASE_URL = "https://wooatrash.wooahouse.com"
TODAY = date.today().isoformat()

POPULAR_ITEMS = ["냉장고", "세탁기", "침대", "소파", "옷장", "에어컨", "책상"]

SIDO_INFO = {
    "서울특별시": "서울특별시는 25개 자치구별로 대형폐기물 배출 방법과 수수료가 다릅니다. 각 구청 홈페이지 또는 해당 구의 생활폐기물 처리업체에 신청하거나, 서울시 공공서비스예약(yeyak.seoul.go.kr)을 통해 온라인 신청이 가능한 구도 있습니다. 냉장고, 세탁기, 에어컨 같은 대형 가전제품은 무상 방문 수거 서비스(가전제품 무상방문수거 서비스)를 이용하면 비용 없이 처리할 수 있습니다.",
    "부산광역시": "부산광역시는 16개 구·군별로 대형폐기물 수수료가 다르게 책정됩니다. 부산시 전자민원서비스나 각 구청 홈페이지를 통해 인터넷 신청이 가능하며, 스티커를 구입해 폐기물에 부착한 후 지정 장소에 배출하는 방식을 사용합니다. 에어컨, 냉장고, 세탁기 등 가전제품은 한국전자제품자원순환공제조합을 통해 무상 수거가 가능합니다.",
    "대구광역시": "대구광역시는 8개 구·군별로 대형폐기물 처리 절차와 수수료가 상이합니다. 대구시 민원포털 또는 각 구청 민원 전화를 통해 수거 신청을 할 수 있으며, 납부필증(스티커)을 구입해 배출하는 방식이 일반적입니다. 가전제품 무상수거 서비스도 병행 운영되고 있습니다.",
    "인천광역시": "인천광역시는 10개 구·군별로 대형폐기물 수수료와 배출 방법이 다릅니다. 각 군·구청 홈페이지나 앱을 통해 온라인 신청이 가능하며, 납부필증을 폐기물에 부착하여 배출하는 방식을 사용합니다. 냉장고·에어컨·세탁기 등은 제조사 무상수거 서비스를 이용하면 비용 없이 처리할 수 있습니다.",
    "광주광역시": "광주광역시는 5개 자치구별로 대형폐기물 수수료 체계가 다릅니다. 광주시 스마트민원포털 또는 각 구청 생활폐기물 담당 부서에 신청할 수 있으며, 납부필증을 구입해 폐기물에 부착한 후 배출하는 방식을 따릅니다.",
    "대전광역시": "대전광역시는 5개 자치구별로 대형폐기물 수수료가 다르게 적용됩니다. 대전시 민원포털 또는 각 구청 홈페이지를 통해 신청하거나 편의점에서 납부필증을 구입해 폐기물에 부착하여 배출합니다.",
    "울산광역시": "울산광역시는 4개 구와 1개 군별로 대형폐기물 수수료와 처리 방식이 다릅니다. 각 구·군청 홈페이지에서 인터넷 신청이 가능하며, 납부필증을 부착해 지정 장소에 배출하는 방식을 사용합니다.",
    "세종특별자치시": "세종특별자치시는 단일 행정구역으로, 세종시 민원포털을 통해 대형폐기물 수거 신청을 할 수 있습니다. 납부필증을 구입해 폐기물에 부착한 후 지정된 장소에 배출하는 방식이며, 아파트의 경우 단지 내 별도 배출 방법이 있을 수 있습니다.",
    "경기도": "경기도는 31개 시·군별로 대형폐기물 수수료와 배출 방법이 크게 다릅니다. 대부분의 시·군에서 인터넷 또는 모바일 앱을 통한 신청이 가능하며, 납부필증을 인쇄하거나 가까운 편의점에서 구입해 폐기물에 부착한 후 배출합니다. 경기도는 전국에서 대형폐기물 발생량이 가장 많은 지역으로, 각 시·군마다 처리 업체와 수수료 체계가 다르니 거주 지역의 정확한 정보를 확인하세요.",
    "강원특별자치도": "강원특별자치도는 18개 시·군별로 대형폐기물 수수료와 배출 방법이 다릅니다. 청정 자연환경을 보전하기 위해 폐기물 적법 처리가 강조되며, 각 시·군청 홈페이지나 콜센터를 통해 수거를 신청할 수 있습니다. 납부필증을 구입해 배출하는 방식이 일반적이며, 일부 지역은 앱 신청도 가능합니다.",
    "충청북도": "충청북도는 11개 시·군별로 대형폐기물 처리 절차와 수수료가 상이합니다. 내륙 지역 특성상 배출 장소와 수거 일정이 지역마다 다르므로, 각 시·군청 홈페이지에서 정확한 안내를 확인하시기 바랍니다. 납부필증 구입 후 부착하여 배출하는 방식이 일반적입니다.",
    "충청남도": "충청남도는 15개 시·군별로 대형폐기물 수수료와 배출 방법이 다릅니다. 서해안 인접 지역의 특성을 반영하여 일부 지역에서는 특수 폐기물 처리 규정이 있으며, 각 시·군청 홈페이지를 통해 정확한 정보를 확인하세요.",
    "전북특별자치도": "전북특별자치도는 14개 시·군별로 대형폐기물 수수료가 다르게 책정됩니다. 각 시·군청 홈페이지 또는 민원실에서 납부필증을 구입해 배출하는 방식을 사용하며, 일부 지역에서는 전화 신청 후 수거하는 방식도 운영됩니다.",
    "전라남도": "전라남도는 22개 시·군별로 대형폐기물 처리 방식과 수수료가 상이합니다. 도서 지역의 경우 본토와 다른 처리 방식이 적용될 수 있으며, 각 시·군청을 통해 정확한 안내를 받으시기 바랍니다.",
    "경상북도": "경상북도는 23개 시·군별로 대형폐기물 수수료와 배출 방법이 다릅니다. 일부 시·군에서는 온라인 신청 시스템을 운영하며, 납부필증 구입 후 부착하여 배출하는 방식이 일반적입니다. 농촌 지역의 경우 수거 일정이 제한될 수 있으니 사전에 확인하세요.",
    "경상남도": "경상남도는 18개 시·군별로 대형폐기물 처리 방식과 수수료가 다릅니다. 각 시·군청 홈페이지나 콜센터를 통해 수거 신청이 가능하며, 납부필증 구입 후 지정 장소에 배출하는 방식을 사용합니다.",
    "제주특별자치도": "제주특별자치도는 제주시와 서귀포시 2개 행정시로 구성되어 있습니다. 제주도의 청정 환경 보전을 위해 대형폐기물 처리 규정이 엄격하게 적용되며, 제주특별자치도 홈페이지 또는 각 행정시 민원실을 통해 신청할 수 있습니다.",
}

SIDO_SHORT = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
    "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
    "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
    "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라남도": "전남", "경상북도": "경북",
    "경상남도": "경남", "제주특별자치도": "제주",
}


def short_name(name):
    """'구로구' -> '구로', '가평군' -> '가평', '수원시' -> '수원'"""
    if len(name) > 2 and name[-1] in "구군시":
        return name[:-1]
    return name

HEAD_COMMON = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9ZGENFSXWC"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-9ZGENFSXWC');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6464921081676309" crossorigin="anonymous"></script>
"""

HEADER_TMPL = """<header class="site-header">
  <div class="header-inner">
    <a href="{root}index.html" class="site-logo">
      <span class="logo-icon">\U0001f5d1️</span>
      <span class="logo-text">우아트래시</span>
    </a>
    <nav class="header-nav">
      <a href="{root}index.html">홈</a>
      <a href="{root}index.html#region">지역별</a>
      <a href="https://wooahouse.com" target="_blank" rel="noopener">WooaHouse &rarr;</a>
    </nav>
    <button class="mobile-menu-btn" aria-label="메뉴">☰</button>
  </div>
</header>

<script src="{root}js/wooa-sites-bar.js"></script>
"""

AD_BANNER = '<div class="ad-banner ad-mid"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6464921081676309" data-ad-slot="7080296704" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>'
AD_SIDEBAR = '<div class="ad-banner ad-side" style="position:sticky;top:76px;"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-6464921081676309" data-ad-slot="1419180025" data-full-width-responsive="false"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>'

FOOTER_TMPL = """<footer style="background:#111827;color:#9CA3AF;padding:32px 20px;text-align:center;font-size:.85rem;margin-top:40px;">
  <p>우아트래시 · 전국 대형폐기물 수수료 조회</p>
  <p style="margin-top:8px;"><a href="{root}privacy.html" style="color:#9CA3AF;">개인정보처리방침</a> · <a href="https://wooahouse.com" target="_blank" rel="noopener" style="color:#9CA3AF;">WooaHouse</a></p>
  <p style="margin-top:12px;color:#6B7280;">데이터 출처: 공공데이터포털 전국대형폐기물수거수수료정보표준데이터 (기준일 {today})</p>
</footer>
"""


def load_records():
    path = DATA_PATH if DATA_PATH.exists() else SAMPLE_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    return data


def page_shell(title, description, canonical, root, body, extra_head="", keywords=""):
    keywords_tag = f'\n  <meta name="keywords" content="{keywords}">' if keywords else ""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
{HEAD_COMMON}
  <title>{title}</title>
  <meta name="description" content="{description}">{keywords_tag}
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <link rel="stylesheet" href="{root}css/style.css">
{extra_head}
</head>
<body>
{HEADER_TMPL.format(root=root)}
{body}
{FOOTER_TMPL.format(root=root, today=TODAY)}
</body>
</html>
"""


def fee_display(item):
    if item.get("유무료여부") == "무료":
        return "무료"
    fee = item.get("수수료", "")
    if not fee or fee == "0":
        return "무료"
    try:
        return f"{int(fee):,}원"
    except (ValueError, TypeError):
        return f"{fee}원"


def gen_sigungu_page(sido, sigungu, items):
    slug_sido = sido
    by_cat = defaultdict(list)
    for it in items:
        by_cat[it.get("대형폐기물구분명", "기타")].append(it)

    sections = []
    for cat in sorted(by_cat.keys()):
        rows = "".join(
            f"""<tr>
              <td>{it.get('대형폐기물명','')}</td>
              <td>{it.get('대형폐기물규격','') or '-'}</td>
              <td style="text-align:right;font-weight:700;color:var(--primary);">{fee_display(it)}</td>
            </tr>"""
            for it in sorted(by_cat[cat], key=lambda x: x.get("대형폐기물명", ""))
        )
        sections.append(f"""
        <div class="fee-card" style="background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:20px;margin-bottom:16px;">
          <h2 style="font-size:1.05rem;margin-bottom:12px;">{cat}</h2>
          <table style="width:100%;border-collapse:collapse;font-size:.9rem;">
            <thead><tr style="border-bottom:2px solid var(--border);">
              <th style="text-align:left;padding:8px 4px;">품목</th>
              <th style="text-align:left;padding:8px 4px;">규격</th>
              <th style="text-align:right;padding:8px 4px;">수수료</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        {AD_BANNER}""")

    manage_org = items[0].get("관리기관명", "") if items else ""
    body = f"""
<div style="max-width:1200px;margin:0 auto;padding:24px 20px 40px;display:flex;gap:24px;align-items:flex-start;">
  <div style="flex:1;min-width:0;">
  <nav style="font-size:.8rem;color:var(--text-muted);margin-bottom:16px;">
    <a href="../index.html">홈</a> &rsaquo; <a href="{slug_sido}.html">{sido}</a> &rsaquo; <span>{sigungu}</span>
  </nav>
  <h1 style="font-size:1.5rem;margin-bottom:6px;">{sido} {sigungu} 대형폐기물 수수료</h1>
  <p style="color:var(--text-muted);font-size:.9rem;margin-bottom:20px;">관리기관: {manage_org} · 품목 {len(items)}개</p>
  {''.join(sections)}
  </div>
  {AD_SIDEBAR}
</div>
"""
    short_sg = short_name(sigungu)
    sample_items = ", ".join(sorted({it.get("대형폐기물명", "") for it in items} & set(POPULAR_ITEMS))[:4]) or ", ".join(POPULAR_ITEMS[:4])
    title = f"{sido} {sigungu} 대형폐기물 스티커 가격·요금 {TODAY[:4]} | 우아트래시"
    desc = f"{sido} {sigungu}({short_sg}) 대형폐기물 스티커 가격을 품목별로 확인하세요. {sample_items} 등 총 {len(items)}개 품목 배출 수수료 정보 제공."
    keywords = f"{sigungu} 대형폐기물, {short_sg} 폐기물 가격, {sigungu} 폐기물 스티커, {sido} {sigungu} 대형폐기물 요금, {sample_items} 버리는법"
    canonical = f"{BASE_URL}/지역/{sido}/{sigungu}.html"
    return page_shell(title, desc, canonical, "../../", body, keywords=keywords)


GRID_STYLE = "display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;"


def gen_sido_page(sido, sigungu_list):
    cards = "".join(
        f"""<a href="{sido}/{sg}.html" class="region-card" style="display:block;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px 20px;transition:transform .12s,box-shadow .12s;">
          <strong>{sg}</strong>
        </a>"""
        for sg in sigungu_list
    )
    short_sido = SIDO_SHORT.get(sido, sido)
    sido_desc = SIDO_INFO.get(sido, f"{sido}는 각 시·군·구별로 대형폐기물 수수료와 배출 방법이 다릅니다. 아래에서 거주 지역을 선택하면 냉장고, 세탁기, 침대, 소파 등 품목별 정확한 수수료를 확인할 수 있습니다.")
    faq_html = f"""
  <div style="margin-top:32px;background:white;border-radius:14px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:24px 28px;">
    <h2 style="font-size:1.1rem;margin-bottom:16px;">자주 묻는 질문 — {sido} 대형폐기물</h2>
    <details style="margin-bottom:12px;">
      <summary style="cursor:pointer;font-weight:600;padding:8px 0;">{sido}에서 대형폐기물은 어떻게 배출하나요?</summary>
      <p style="padding:8px 0 4px;color:#374151;line-height:1.7;">각 시·군·구청 홈페이지 또는 민원실에서 납부필증(스티커)을 구입하거나 인터넷으로 신청 후 결제합니다. 납부필증을 폐기물에 부착한 뒤 지정 날짜와 장소에 배출하면 됩니다. 일부 지역은 앱·모바일 신청도 지원합니다.</p>
    </details>
    <details style="margin-bottom:12px;">
      <summary style="cursor:pointer;font-weight:600;padding:8px 0;">{sido} 시·군·구마다 수수료가 다른가요?</summary>
      <p style="padding:8px 0 4px;color:#374151;line-height:1.7;">네, {sido}는 {len(sigungu_list)}개 시·군·구별로 수수료가 다르게 책정됩니다. 같은 품목이라도 거주 지역에 따라 수천 원 이상 차이가 날 수 있으니, 반드시 아래에서 해당 지역을 선택해 정확한 금액을 확인하세요.</p>
    </details>
    <details>
      <summary style="cursor:pointer;font-weight:600;padding:8px 0;">냉장고·에어컨·세탁기 같은 가전제품도 수수료를 내야 하나요?</summary>
      <p style="padding:8px 0 4px;color:#374151;line-height:1.7;">냉장고, 에어컨, 세탁기, TV 등 5대 가전제품은 한국전자제품자원순환공제조합(또는 제조사)을 통해 무상 방문 수거가 가능합니다. 무상수거 서비스를 이용하면 대형폐기물 수수료 없이 처리할 수 있습니다. 단, 이 서비스를 이용하지 않고 일반 폐기물로 배출하면 수수료가 부과됩니다.</p>
    </details>
  </div>"""
    body = f"""
<div style="max-width:1100px;margin:0 auto;padding:24px 20px 40px;">
  <nav style="font-size:.8rem;color:var(--text-muted);margin-bottom:16px;">
    <a href="../index.html">홈</a> &rsaquo; <span>{sido}</span>
  </nav>
  <h1 style="font-size:1.5rem;margin-bottom:12px;">{sido} 대형폐기물 수수료 — 시군구 선택 ({len(sigungu_list)}개 지역)</h1>
  <p style="color:#374151;line-height:1.75;margin-bottom:20px;font-size:.95rem;">{sido_desc}</p>
  {AD_BANNER}
  <h2 style="font-size:1rem;font-weight:700;margin:20px 0 12px;">{short_sido} 시군구 선택 ({len(sigungu_list)}개 지역)</h2>
  <div style="{GRID_STYLE}">
  {cards}
  </div>
  {faq_html}
</div>
"""
    short_sido = SIDO_SHORT.get(sido, sido)
    title = f"{sido} 대형폐기물 스티커 가격·수수료 지역별 조회 | 우아트래시"
    desc = f"{sido}({short_sido}) 내 시군구별 대형폐기물(냉장고, 세탁기, 침대 등) 스티커 가격과 배출 수수료를 확인하세요."
    keywords = f"{sido} 대형폐기물, {short_sido} 폐기물 가격, {sido} 폐기물 스티커 요금, {sido} 시군구 폐기물"
    canonical = f"{BASE_URL}/지역/{sido}.html"
    return page_shell(title, desc, canonical, "../", body, keywords=keywords)


CATEGORY_INFO = [
    ("가전제품류", "🧊", "냉장고, 세탁기, TV, 에어컨 등"),
    ("가구류", "🛋️", "침대, 소파, 옷장, 책상 등"),
    ("생활용품류", "🧺", "매트리스, 카페트, 항아리 등"),
    ("기타", "📦", "자전거, 운동기구, 화분 등"),
]


def gen_index_page(sido_map, records):
    total_items = len(records)
    total_sigungu = sum(len(sgs) for sgs in sido_map.values())
    total_sido = len(sido_map)

    stats_bar = f"""
<div style="max-width:1100px;margin:0 auto;padding:24px 20px 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;">
  <div style="background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px;text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:var(--primary);">{total_sido}</div>
    <div style="font-size:.82rem;color:var(--text-muted);">개 시도</div>
  </div>
  <div style="background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px;text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:var(--primary);">{total_sigungu}</div>
    <div style="font-size:.82rem;color:var(--text-muted);">개 시군구</div>
  </div>
  <div style="background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px;text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:var(--primary);">{total_items:,}</div>
    <div style="font-size:.82rem;color:var(--text-muted);">개 품목 요금 정보</div>
  </div>
  <div style="background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px;text-align:center;">
    <div style="font-size:1.6rem;font-weight:800;color:var(--primary);">매달</div>
    <div style="font-size:.82rem;color:var(--text-muted);">자동 업데이트</div>
  </div>
</div>
"""

    category_cards = "".join(
        f"""<div style="background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px;text-align:center;">
          <div style="font-size:1.8rem;margin-bottom:6px;">{icon}</div>
          <div style="font-weight:700;margin-bottom:4px;">{name}</div>
          <div style="font-size:.8rem;color:var(--text-muted);">{desc}</div>
        </div>"""
        for name, icon, desc in CATEGORY_INFO
    )

    sido_cards = "".join(
        f"""<a href="지역/{sido}.html" class="region-card" style="display:block;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:18px 20px;">
          <strong>{sido}</strong><br><span style="color:var(--text-muted);font-size:.85rem;">{len(sgs)}개 지역</span>
        </a>"""
        for sido, sgs in sorted(sido_map.items())
    )
    body = f"""
<div style="background:linear-gradient(135deg,#1D4ED8,#3B82F6);color:white;padding:44px 20px;text-align:center;">
  <h1 style="font-size:1.8rem;font-weight:800;margin-bottom:10px;">\U0001f5d1️ 전국 대형폐기물 수수료 조회</h1>
  <p style="opacity:.9;">우리 동네 냉장고, 세탁기, 침대 버릴 때 얼마인지 바로 확인하세요</p>
</div>
{stats_bar}
<div style="max-width:1100px;margin:24px auto 0;padding:0 20px;">
  {AD_BANNER}
</div>
<div style="max-width:1100px;margin:0 auto;padding:32px 20px 0;">
  <h2 style="font-size:1.1rem;margin-bottom:16px;">품목 카테고리</h2>
  <div style="{GRID_STYLE.replace('220px','160px')}">
    {category_cards}
  </div>
</div>
<div style="max-width:1100px;margin:0 auto;padding:32px 20px 50px;">
  <h2 style="font-size:1.1rem;margin-bottom:16px;" id="region">지역 선택</h2>
  <div style="{GRID_STYLE}">
  {sido_cards}
  </div>
</div>
"""
    title = "전국 대형폐기물 스티커 가격·요금 조회 — 냉장고·세탁기·침대 배출비용 | 우아트래시"
    desc = "전국 시군구별 대형폐기물(가전제품, 가구, 생활용품) 스티커 가격과 배출 수수료를 무료로 확인하세요. 매달 업데이트되는 공공데이터 기반, 전국 142개 지역 22,000여 개 품목 정보 제공."
    keywords = "대형폐기물 가격, 대형폐기물 스티커 요금, 폐기물 스티커 가격, 냉장고 버리는 가격, 세탁기 버리는 가격, 침대 버리는 가격, 대형폐기물 배출 수수료"
    canonical = f"{BASE_URL}/"
    return page_shell(title, desc, canonical, "", body, keywords=keywords)


def gen_sitemap(sido_map):
    urls = [f"  <url><loc>{BASE_URL}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>"]
    for sido, sgs in sido_map.items():
        urls.append(f"  <url><loc>{BASE_URL}/지역/{sido}.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>")
        for sg in sgs:
            urls.append(f"  <url><loc>{BASE_URL}/지역/{sido}/{sg}.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
    (DOCS_DIR / "sitemap.xml").write_text(xml, encoding="utf-8")


def main():
    records = load_records()
    print(f"{len(records)}건 로드")

    by_sido_sigungu = defaultdict(lambda: defaultdict(list))
    for r in records:
        by_sido_sigungu[r["시도명"]][r["시군구명"]].append(r)

    sido_map = {sido: sorted(sgs.keys()) for sido, sgs in by_sido_sigungu.items()}

    generated = 0
    for sido, sgs in by_sido_sigungu.items():
        sido_dir = REGION_DIR / sido
        sido_dir.mkdir(parents=True, exist_ok=True)
        (REGION_DIR / f"{sido}.html").write_text(gen_sido_page(sido, sorted(sgs.keys())), encoding="utf-8")
        generated += 1
        for sg, items in sgs.items():
            (sido_dir / f"{sg}.html").write_text(gen_sigungu_page(sido, sg, items), encoding="utf-8")
            generated += 1

    (DOCS_DIR / "index.html").write_text(gen_index_page(sido_map, records), encoding="utf-8")
    generated += 1

    gen_sitemap(sido_map)
    print(f"총 {generated}개 페이지 생성 완료")


if __name__ == "__main__":
    main()
