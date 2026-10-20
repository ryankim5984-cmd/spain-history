#!/usr/bin/env python3
"""Offline-first Spanish history study site builder.
Usage: pip install mistune && python build_site.py
The 28 Markdown chapters are the source of truth; running rebuilds every HTML page.
Updated 2026-10-20.
"""
from pathlib import Path
import json, html, re
import mistune

ROOT = Path(__file__).resolve().parent
META = json.loads((ROOT/'metadata.json').read_text(encoding='utf-8'))
md = mistune.create_markdown(escape=True, plugins=['table','strikethrough'])

CATEGORY_LABELS = {'선사·고대':'선사 · 고대','중세':'중세','근세':'근세','근현대':'근현대'}
DONE=sum(1 for x in META if x['completed'])
TOTAL=len(META)

def esc(t): return html.escape(str(t),quote=True)
def chapter_link(i): return f'era-{i:02}.html'

def build_nav(active=None):
    out=[]
    for d in META:
        i=d['number']; cl=' current' if i==active else ''; tag='draft' if not d['completed'] else 'complete'
        out.append(f'<a class="side-link{cl}" href="{chapter_link(i)}" aria-current="{"page" if i==active else "false"}"><span class="num">{i:02}</span><span class="nav-name">{esc(d["short_title"])}</span><span class="nav-status {tag}" aria-label="{"작성됨" if d["completed"] else "예정"}"></span></a>')
    return ''.join(out)

def layout(title, main, active=None, page='chapter', description=''):
    nav=build_nav(active)
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(description or title)}">
<title>{esc(title)} · 스페인 역사 공부</title>
<link rel="stylesheet" href="assets/style.css"><script src="assets/site.js" defer></script>
</head>
<body data-page="{page}" data-number="{active if active else ''}">
<a class="skip-link" href="#main">본문으로 건너뛰기</a>
<header class="site-header"><div class="topbar"><a href="index.html" class="brand"><span class="logo-flag" aria-hidden="true"><i></i></span><span>스페인 역사 공부<span class="brand-en"> HISTORIA DE ESPAÑA</span></span></a><div class="header-links"><a href="index.html#all-chapters">전체 목차</a><a href="guide.html">이용 안내</a></div></div></header>
<div class="site-shell"><aside class="sidebar" aria-label="시대별 목차"><div class="sidebar-inner"><div class="side-heading">시대별 학습</div><p class="side-sub">작성된 {DONE}편 · 전체 {TOTAL}편</p><nav>{nav}</nav></div></aside><main id="main" class="main-content">{main}</main></div>
<footer class="site-footer"><span>스페인 역사 공부 · 정적 HTML 학습 자료</span><span><a href="guide.html">콘텐츠 관리 안내</a> · <a href="credits.html">이미지·자료 출처</a></span></footer>
</body></html>'''

def create_toc(soup_text):
    matches=list(re.finditer(r'<h([23])>(.*?)</h\1>',soup_text,re.S))
    links=[]; used={}
    for m in matches:
        label=re.sub(r'<[^>]+>','',m.group(2)).strip()
        # Headings already carry a section number; the <ol> supplies it in the TOC.
        label=re.sub(r'^\d+\.\s*','',label)
        clean=re.sub(r'[^a-zA-Z0-9가-힣]+','-',label).strip('-').lower()[:60] or 'section'
        used[clean]=used.get(clean,0)+1
        key=f'{clean}-{used[clean]}'
        links.append((m.group(0),f'<h{m.group(1)} id="{esc(key)}">{m.group(2)}</h{m.group(1)}>',label,key,int(m.group(1))))
    for old,new,*_ in links: soup_text=soup_text.replace(old,new,1)
    links_html=''.join(f'<li class="lvl-{h}"><a href="#{esc(k)}">{esc(lbl)}</a></li>' for _,__,lbl,k,h in links)
    return soup_text, f'<details class="toc" open><summary>이 편의 목차 <span>{len(links)}개 항목</span></summary><ol>{links_html}</ol></details>' if links else ''

def add_tables_wrappers(text):
    return re.sub(r'(<table>.*?</table>)',r'<div class="table-scroll">\1</div>',text, flags=re.S)

for d in META:
    i=d['number']; raw=(ROOT/'chapters'/f'{i:02}.md').read_text(encoding='utf-8')
    body=md(raw)
    body=add_tables_wrappers(body)
    body=re.sub(r'<p>자료 확인:\s*', r'<p class="sources-note">자료 확인: ' , body)
    body,toc=create_toc(body)
    state='상세 본문 집필 완료' if i>=17 else '작성된 학습편'
    note=(
        '<div class="content-note"><strong>기존 학습 내용 재구성</strong> 이 페이지는 이전 대화의 핵심 내용을 옮겨 구성한 학습용 원고입니다. 과거 답변의 모든 문장을 한 글자도 빠짐없이 복제한 원문은 아닙니다. 정확한 원문을 보유한 경우 <a href="guide.html">원고 파일에 교체</a>할 수 있습니다.</div>'
        if i<=16 else
        '<div class="content-note"><strong>상세 본문 집필 완료</strong> 사건의 배경·전개·결과와 역사적 의미를 연결한 한국어 학습 원고입니다. 주요 연도·인물·스페인어 명칭과 연표를 함께 정리했습니다.</div>'
    )
    prev=f'<a class="chapter-switch" href="{chapter_link(i-1)}"><span>← 이전 시대</span><strong>{esc(META[i-2]["short_title"])}</strong></a>' if i>1 else '<span></span>'
    nxt=f'<a class="chapter-switch next" href="{chapter_link(i+1)}"><span>다음 시대 →</span><strong>{esc(META[i]["short_title"])}</strong></a>' if i<len(META) else '<span></span>'
    header=f'''<div class="crumb"><a href="index.html">홈</a><span>›</span><a href="index.html#all-chapters">전체 시대</a><span>›</span>제{i:02}편</div><div class="chapter-label">제{i:02}편 · {esc(d['category'])} <span class="state-label {'pending' if not d['completed'] else ''}">{state}</span></div><h1 class="chapter-title">{esc(d['title'])}</h1><p class="date-range">{esc(d['period'])} · {esc(d['subtitle'])}</p>{note}{toc}'''
    reading=f'<div class="reading-wrap"><article class="article-body">{body}</article></div>'
    foot=f'<div class="page-controls">{prev}{nxt}</div><div class="editor-hint">원고 수정: <code>chapters/{i:02}.md</code> 파일을 수정한 다음 <code>python build_site.py</code>를 실행하세요.</div>'
    (ROOT/chapter_link(i)).write_text(layout(f'{i:02}편 {d["title"]}',header+reading+foot,active=i,description=d['title']+' '+d['period']),encoding='utf-8')

# Homepage — all 28 chapters are complete. Filter by historical period instead of draft status.
cards=''.join(
    f'<a class="era-card" data-filter="{esc(d["title"]+" "+d["short_title"]+" "+d["subtitle"]+" "+d["period"]+" "+d["keywords"])}" '
    f'data-category="{esc(d["category"])}" href="{chapter_link(d["number"])}">'
    f'<div class="card-meta"><span>{d["number"]:02}편 · {esc(d["category"])}</span><span class="card-state">학습하기</span></div>'
    f'<h2>{esc(d["title"])}</h2><p>{esc(d["period"])}</p><small>{esc(d["subtitle"])}</small><span class="card-arrow">→</span></a>'
    for d in META
)
filter_buttons=''.join(
    f'<button class="filter-btn{" active" if ix==0 else ""}" data-category="{esc(key)}" type="button" aria-pressed="{str(ix==0).lower()}">{esc(label)}</button>'
    for ix,(key,label) in enumerate([('all','전체'),('선사·고대','선사·고대'),('중세','중세'),('근세','근세'),('근현대','근현대')])
)
main=f'''<section class="hero"><div class="hero-copy"><div class="hero-identity"><img class="hero-flag" src="https://upload.wikimedia.org/wikipedia/en/9/9a/Flag_of_Spain.svg" data-fallback="assets/flag-civil.svg" alt="스페인의 국기" width="90" height="60"><span class="eyebrow">HISTORIA DE ESPAÑA</span></div><h1>스페인 역사 공부</h1><p class="hero-kicker">선사시대부터 현대 스페인까지 · 전 28편 완성</p><p>이베리아반도의 선사 문화와 여러 왕국, 스페인 제국, 내전과 독재, 민주화와 유럽 통합에 이르기까지 28개 시대를 순서대로 공부하는 한국어 학습 사이트입니다.</p><div class="hero-actions"><a class="primary-action" href="era-01.html">1편부터 공부하기 <span>→</span></a><a class="text-action" href="#all-chapters">전체 시대 살펴보기</a></div><div class="progress"><span>학습 원고 <strong>{DONE} / {TOTAL}편 완성</strong></span><span>모든 시대 본문 열람 가능</span><div class="progress-track"><div class="progress-fill" style="width:{100*DONE/TOTAL:.2f}%"></div></div></div></div><figure class="hero-photo"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Royal_Palace_of_Madrid%2C_facade_principal_20.JPG/1280px-Royal_Palace_of_Madrid%2C_facade_principal_20.JPG" alt="스페인 마드리드 왕궁 팔라시오 레알의 외관" loading="eager" decoding="async"><div class="photo-fallback">왕궁 사진은 인터넷 연결 시 표시됩니다.</div><figcaption>마드리드 왕궁(Palacio Real de Madrid) · 사진: <a href="https://commons.wikimedia.org/wiki/File:Royal_Palace_of_Madrid,_facade_principal_20.JPG">Dorieo / Wikimedia Commons</a> · CC BY-SA 4.0</figcaption></figure></section>
<section class="intro-strip"><div><strong>28개 시대 상세 본문</strong><p>시대를 한 편씩 열어 역사적 배경과 사건·결과를 살펴보세요.</p></div><div><strong>오프라인으로 학습</strong><p>글·디자인·목차 검색은 인터넷 없이 작동합니다. 왕궁 사진만 연결이 필요합니다.</p></div><div><strong>원고와 HTML 동기화</strong><p>편별 Markdown 원고를 수정하면 페이지와 홈페이지를 다시 만들 수 있습니다.</p></div></section>
<section id="all-chapters" class="all-chapters"><div class="section-title"><div><span class="eyebrow">28 CHAPTERS · COMPLETE</span><h2>전체 시대 목차</h2><p>시대별 필터나 검색으로 원하는 역사 주제를 찾아보세요.</p></div><div class="count-display" aria-live="polite"><span id="resultCount">28</span>개 시대</div></div><div class="filter-wrap"><label class="sr-only" for="eraSearch">시대 찾기</label><input id="eraSearch" type="search" placeholder="시대, 인물, 연도 검색 (예: 로마, 1492, 민주화)" autocomplete="off"><div class="filter-buttons" role="group" aria-label="시대별 필터">{filter_buttons}</div></div><div id="eraGrid" class="era-grid">{cards}</div><p id="noResults" hidden>검색 결과가 없습니다. 다른 단어나 시대 구분으로 검색해 보세요.</p></section>'''
(ROOT/'index.html').write_text(layout('홈',main,page='home',description='스페인 역사를 선사시대부터 2026년까지 공부하는 한국어 사이트 · 28편 완성'),encoding='utf-8')

guide='''<div class="crumb"><a href="index.html">홈</a><span>›</span>이용 안내</div><h1 class="chapter-title">이용 및 원고 관리 안내</h1><div class="reading-wrap"><article class="article-body">
<h2>사이트 열기</h2><p>압축을 완전히 해제한 뒤 <code>index.html</code> 파일을 더블클릭하세요. Chrome·Edge·Safari 등 일반 브라우저에서 바로 열립니다. 별도의 웹서버나 회원가입 없이 1~28편을 모두 읽을 수 있습니다. 홈 화면의 왕궁 사진과 외부 자료 링크는 인터넷 연결이 필요합니다.</p>
<h2>집필 현황과 원고의 성격</h2><p><strong>1~28편 전체 본문이 작성되어 있습니다.</strong> 1~16편은 이전 대화의 핵심 사건과 흐름을 토대로 재구성한 학습 원고이며, 이전 답변의 문장·표·인용을 빠짐없이 복제한 원문은 아닙니다. 17~28편은 이후에 상세 집필한 시대별 원고를 반영했습니다. 모든 편은 역사 학습 자료로서 사료·학술적 논의와 비교하며 읽으시기를 권장합니다.</p>
<h2>HTML과 Markdown의 관계</h2><p><code>era-01.html</code>부터 <code>era-28.html</code>까지가 바로 열어볼 수 있는 학습 페이지입니다. <code>chapters/01.md</code>부터 <code>chapters/28.md</code>까지는 각 페이지의 <strong>편집용 원고</strong>입니다. <code>metadata.json</code>에는 제목·연대·검색어·집필 상태가 기록되어 있습니다. <code>build_site.py</code>를 실행하면 원고와 메타데이터를 기준으로 28개 본문, 홈페이지, 안내·출처 페이지가 다시 만들어집니다.</p>
<h2>내용 수정 방법</h2><ol><li>수정할 편의 원고(예: <code>chapters/17.md</code>)를 메모장이나 Markdown 편집기로 엽니다.</li><li>본문을 고치고 UTF-8로 저장합니다. 제목·연대나 검색어를 바꾸려면 <code>metadata.json</code>도 함께 수정합니다.</li><li>Python 3가 설치되어 있다면 최초 한 번 <code>python -m pip install mistune</code>를 실행합니다.</li><li>사이트 최상위 폴더에서 <code>python build_site.py</code>를 실행하고 <code>index.html</code>을 새로고침합니다.</li></ol><p><strong>주의:</strong> HTML을 직접 수정하는 것도 가능하지만 빌드 스크립트를 실행하면 HTML은 Markdown 내용으로 다시 생성됩니다. 수정 사항을 오래 유지하려면 <code>chapters/*.md</code> 파일을 편집하세요.</p>
<h2>찾기와 이동</h2><p>홈페이지에서 시대명·연도·인물을 검색하거나 선사·고대 / 중세 / 근세 / 근현대 중 하나로 걸러볼 수 있습니다. 왼쪽 시대 목록과 각 편 하단의 이전·다음 이동 링크를 이용해 순서대로 학습할 수도 있습니다. 모바일에서는 시대 목록이 상단의 가로 스크롤로 표시됩니다. 표는 화면이 좁을 때 표 내부만 가로로 스크롤됩니다.</p>
<h2>현대사 자료의 기준 날짜</h2><p>28편의 현대 정치·사회 상황은 <strong>2026년 10월 20일</strong>을 기준으로 작성했습니다. 이후 선거 결과나 정책 변동은 자동으로 반영되지 않으므로 최신 상황은 해당 편의 원고를 직접 갱신해야 합니다.</p>
<h2>이미지와 참고 자료</h2><p>홈 화면 마드리드 왕궁 사진은 <a href="https://commons.wikimedia.org/wiki/File:Royal_Palace_of_Madrid,_facade_principal_20.JPG">Wikimedia Commons</a>에서 온라인으로 불러옵니다. 국기 그림은 사이트에 포함된 간략한 민간기 SVG입니다. 주요 기관 링크와 출처 설명은 <a href="credits.html">자료 및 이미지 출처</a>에서 확인할 수 있으며, 21~28편에는 본문 끝에도 참고 링크가 있습니다.</p>
</article></div>'''
(ROOT/'guide.html').write_text(layout('이용 안내',guide,page='guide'),encoding='utf-8')

credits='''<div class="crumb"><a href="index.html">홈</a><span>›</span>출처</div><h1 class="chapter-title">자료 및 이미지 출처</h1><div class="reading-wrap"><article class="article-body">
<h2>첫 화면의 왕궁 사진</h2><p><a href="https://commons.wikimedia.org/wiki/File:Royal_Palace_of_Madrid,_facade_principal_20.JPG">Royal Palace of Madrid, facade principal 20.JPG</a> — Dorieo, 2013, <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. 원본은 Wikimedia Commons에서 불러오며 오프라인 파일에 포함되어 있지 않습니다. 스페인 민간기는 빨강·노랑·빨강 줄무늬로 제작된 사이트 내 SVG를 사용합니다.</p>
<h2>역사 학습에 활용할 자료 기관</h2><ul><li><a href="https://www.cultura.gob.es/">스페인 문화부(Ministerio de Cultura)</a></li><li><a href="https://pares.cultura.gob.es/">스페인 국가문서보관소 PARES</a></li><li><a href="https://www.bne.es/">스페인 국립도서관(BNE)</a></li><li><a href="https://www.congreso.es/">스페인 하원의회(Congreso de los Diputados)</a></li><li><a href="https://www.boe.es/">스페인 관보(BOE)</a></li><li><a href="https://www.bde.es/">스페인 은행(Banco de España)</a></li><li><a href="https://www.museodelprado.es/">프라도 미술관(Museo del Prado)</a></li><li><a href="https://www.rah.es/">왕립역사학술원(Real Academia de la Historia)</a></li></ul>
<h2>현대사 자료 참고</h2><p>21~28편의 본문 아래에는 스페인 하원·관보·국제기구 등 참고 자료 링크가 있습니다. 17~20편에는 원고별 참고 링크가 별도 수록되어 있지 않으며, 위 기관 자료 등과 대조하여 읽을 수 있습니다. 개별 주장과 사료를 전부 일대일로 연결하는 학술 논문 형식의 주석 자료는 아닙니다.</p>
<h2>사이트의 서술 방식</h2><p>각 시대의 사건을 배경·전개·결과·역사적 의미에 따라 한국어로 설명했습니다. 1~16편의 원고는 원래 대화를 재구성한 자료이며, 17~28편은 추가 집필한 원고입니다. 역사적 해석이 갈리는 부분은 관련 연구와 1차 사료를 함께 확인하는 것이 좋습니다. 28편은 2026년 10월 20일 기준입니다.</p>
</article></div>'''
(ROOT/'credits.html').write_text(layout('출처',credits,page='credits'),encoding='utf-8')
print('generated',len(META),'chapter pages + index/guide/credits')
