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


def page_shell(title, description, canonical, root, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
{HEAD_COMMON}
  <title>{title}</title>
  <meta name="description" content="{description}">
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
        </div>""")

    manage_org = items[0].get("관리기관명", "") if items else ""
    body = f"""
<div style="max-width:900px;margin:0 auto;padding:24px 20px 40px;">
  <nav style="font-size:.8rem;color:var(--text-muted);margin-bottom:16px;">
    <a href="../index.html">홈</a> &rsaquo; <a href="{slug_sido}.html">{sido}</a> &rsaquo; <span>{sigungu}</span>
  </nav>
  <h1 style="font-size:1.5rem;margin-bottom:6px;">{sido} {sigungu} 대형폐기물 수수료</h1>
  <p style="color:var(--text-muted);font-size:.9rem;margin-bottom:20px;">관리기관: {manage_org} · 품목 {len(items)}개</p>
  {''.join(sections)}
</div>
"""
    title = f"{sido} {sigungu} 대형폐기물 스티커 요금 {TODAY[:4]} | 우아트래시"
    desc = f"{sido} {sigungu} 대형폐기물(가전제품, 가구, 생활용품) 배출 수수료를 품목별로 확인하세요. 총 {len(items)}개 품목 요금 정보 제공."
    canonical = f"{BASE_URL}/지역/{sido}/{sigungu}.html"
    return page_shell(title, desc, canonical, "../../", body)


def gen_sido_page(sido, sigungu_list):
    cards = "".join(
        f"""<a href="{sido}/{sg}.html" class="region-card" style="display:block;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:16px 20px;margin-bottom:10px;">
          <strong>{sg}</strong>
        </a>"""
        for sg in sigungu_list
    )
    body = f"""
<div style="max-width:700px;margin:0 auto;padding:24px 20px 40px;">
  <nav style="font-size:.8rem;color:var(--text-muted);margin-bottom:16px;">
    <a href="../index.html">홈</a> &rsaquo; <span>{sido}</span>
  </nav>
  <h1 style="font-size:1.5rem;margin-bottom:20px;">{sido} 대형폐기물 수수료 — 시군구 선택</h1>
  {cards}
</div>
"""
    title = f"{sido} 대형폐기물 수수료 지역별 조회 | 우아트래시"
    desc = f"{sido} 내 시군구별 대형폐기물 배출 수수료를 확인하세요."
    canonical = f"{BASE_URL}/지역/{sido}.html"
    return page_shell(title, desc, canonical, "../", body)


def gen_index_page(sido_map):
    sido_cards = "".join(
        f"""<a href="지역/{sido}.html" class="region-card" style="display:block;background:white;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.06);padding:16px 20px;margin-bottom:10px;">
          <strong>{sido}</strong> <span style="color:var(--text-muted);font-size:.85rem;">({len(sgs)}개 지역)</span>
        </a>"""
        for sido, sgs in sorted(sido_map.items())
    )
    body = f"""
<div style="background:linear-gradient(135deg,#1D4ED8,#3B82F6);color:white;padding:44px 20px;text-align:center;">
  <h1 style="font-size:1.8rem;font-weight:800;margin-bottom:10px;">\U0001f5d1️ 전국 대형폐기물 수수료 조회</h1>
  <p style="opacity:.9;">우리 동네 냉장고, 세탁기, 침대 버릴 때 얼마인지 바로 확인하세요</p>
</div>
<div style="max-width:700px;margin:0 auto;padding:24px 20px 40px;">
  <h2 style="font-size:1.1rem;margin-bottom:16px;">지역 선택</h2>
  {sido_cards}
</div>
"""
    title = "전국 대형폐기물 스티커 요금 조회 — 냉장고·세탁기·침대 배출비용 | 우아트래시"
    desc = "전국 시군구별 대형폐기물(가전제품, 가구, 생활용품) 배출 수수료를 무료로 확인하세요. 매달 업데이트되는 공공데이터 기반."
    canonical = f"{BASE_URL}/"
    return page_shell(title, desc, canonical, "", body)


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

    (DOCS_DIR / "index.html").write_text(gen_index_page(sido_map), encoding="utf-8")
    generated += 1

    gen_sitemap(sido_map)
    print(f"총 {generated}개 페이지 생성 완료")


if __name__ == "__main__":
    main()
