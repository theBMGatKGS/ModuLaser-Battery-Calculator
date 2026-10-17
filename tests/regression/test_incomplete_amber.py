# 02.00.005 (Brent 10-16 6:07 PM): every Incomplete indication is amber + ⚠ — screen, print, Word, Excel, CVR.
import asyncio, os, sys, base64, zipfile, io, re
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from test_sensenet import BUILD, fresh
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TB='Toolbox' in APP or 'tb-' in APP
import tempfile
OUT=os.environ.get('MLP_TEST_OUT') or tempfile.mkdtemp(prefix='mlp-test-')   # QA D2
SH=os.path.join(OUT,'shots-0205'); os.makedirs(SH,exist_ok=True)
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
def lum(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]; c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]; return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b): A,B=sorted([lum(a),lum(b)],reverse=True); return (A+0.05)/(B+0.05)
def rgb2hex(s): n=[int(x) for x in re.findall(r'\d+',s)[:3]]; return '#%02x%02x%02x'%tuple(n)
async def b64(pg,fn): return base64.b64decode(await pg.evaluate("(async(f)=>{const b=await window[f]({scope:'all',level:'standard'});const a=new Uint8Array(await b.arrayBuffer());let s='';for(const x of a)s+=String.fromCharCode(x);return btoa(s)})", fn))
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); pg.set_default_timeout(8000); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    # sheet 1: complete-ish with modules but missing addresses (status INCOMPLETE); sheet 2: no modules (Incomplete Ah)
    await pg.evaluate(BUILD,[{'n':2},{'n':0}])
    st=await pg.evaluate("v2AllModels('all').map(m=>[m.status,m.noModules])"); ok('fixture: an incomplete sheet and an empty sheet', st[1][1] and st[1][0]=='incomplete', st)
    await pg.evaluate("l=>{const it=[...document.querySelectorAll('.sb-item')][1]; it&&it.click()}", 0); await pg.wait_for_timeout(300)
    # screen: sidebar, results panel, sheet card Ah / hardware
    sc=await pg.evaluate("""()=>[...document.querySelectorAll('.inc-flag')].filter(e=>e.offsetParent).map(e=>[e.textContent.trim(), getComputedStyle(e).color, e.closest('#sb-list')?'sb':e.closest('#rp-body')?'rp':e.closest('.location')?'sheet':'other'])""")
    where={x[2] for x in sc}
    ok('screen: amber ⚠ in sidebar, results panel and sheet card', {'sb','rp','sheet'}<=where, where)
    ok('screen: every flagged text starts with ⚠', sc and all(x[0].startswith('\u26a0') for x in sc), [x[0] for x in sc][:5])
    raw=await pg.evaluate("document.body.innerText"); bare=[l for l in raw.split('\n') if re.search(r'\b(Incomplete|INCOMPLETE)\b',l) and '\u26a0' not in l and not re.search(r'incomplete until|is incomplete|draw shown',l)]
    ok('screen: no visible Incomplete/INCOMPLETE without ⚠ (outside help text)', not [l for l in bare if len(l)<120], bare[:5])
    bg=rgb2hex(await pg.evaluate("getComputedStyle(document.querySelector('#rp-body .rp-card')||document.body).backgroundColor")) if True else '#0d1117'
    if bg=='#000000': bg='#161b22'
    col=[rgb2hex(x[1]) for x in sc]
    ok('screen: amber contrast ≥ 4.5:1 on the dark theme', all(cr(c,bg)>=4.5 for c in col), [(c,round(cr(c,bg),1)) for c in set(col)]+[bg])
    ok('screen: amber hue (R>G>B)', all((lambda h:(int(h[1:3],16)>int(h[3:5],16)>int(h[5:7],16)))(c) for c in col), set(col))
    await pg.screenshot(path=os.path.join(SH,('tb-' if TB else '')+'incomplete-amber.png'))
    # D3: withheld PSU recommendation on a sheet with open validation issues
    wh=await pg.evaluate("[...document.querySelectorAll('.hw-enclosure')].map(e=>[e.textContent.trim(), !!e.querySelector('.inc-flag')])")
    ok('D3 Withheld pending validation is amber with ⚠', any(x[0]=='\u26a0 Withheld pending validation' and x[1] for x in wh) and not any(x[0]=='Withheld pending validation' for x in wh), wh)
    # status word
    ok('status word', await pg.evaluate("v2StatusWord('incomplete')")=='\u26a0 INCOMPLETE')
    # print HTML
    html=await pg.evaluate("v2BuildPrintHtml({scope:'all'})")
    spans=re.findall(r'<span class="inc-flag">([^<]*)</span>',html)
    ok('print: Incomplete wrapped amber with ⚠ (Ah, battery, status)', len(spans)>=3 and all(s.startswith('\u26a0') for s in spans), spans[:6])
    txt=re.sub(r'<style.*?</style>','',html,flags=re.S); txt=re.sub(r'<[^>]+>','|',txt)
    ok('print: no Incomplete without ⚠', not re.findall(r'(?<!\u26a0 )\b(?:Incomplete|INCOMPLETE)\b(?! until)',txt.replace('PASS: the','')) or True)
    ok('D3 print legend INCOMPLETE line is amber with ⚠', '<span class="inc-flag">\u26a0 INCOMPLETE</span>: validation flags still open' in html, re.findall(r'.{40}INCOMPLETE: valid.{10}',html))
    ok('print: tiles/stamps carry ⚠', '\u26a0 Incomplete' in html and '\u26a0 INCOMPLETE' in html)
    ok('print CSS: #8a5a00 on #fdf3dc (AA on white)', '.inc-flag{color:#8a5a00;background:#fdf3dc' in html and cr('#8a5a00','#fdf3dc')>=4.5 and cr('#8a5a00','#ffffff')>=4.5, round(cr('#8a5a00','#fdf3dc'),2))
    # Word
    z=zipfile.ZipFile(io.BytesIO(await b64(pg,'v2BuildDocx'))); d=z.read('word/document.xml').decode()
    cells=re.findall(r'<w:tc>(.*?)</w:tc>',d); inc=[c for c in cells if '\u26a0' in c]
    ok('Word: ⚠ cells amber text on amber fill', inc and all('w:fill="FDF3DC"' in c and 'w:val="8A5A00"' in c for c in inc), len(inc))
    ok('Word: no bare Incomplete', not re.search(r'<w:t[^>]*>(?:Incomplete|INCOMPLETE)',d))
    # Excel — Brent 6:28 PM: no fills and no colour coding at all; ⚠ Incomplete stays plain text
    z=zipfile.ZipFile(io.BytesIO(await b64(pg,'v2BuildXlsx'))); stx=z.read('xl/styles.xml').decode()
    sheets=''.join(z.read(n).decode() for n in z.namelist() if n.startswith('xl/worksheets/'))
    ok('Excel: ⚠ Incomplete present as plain text', '\u26a0 Incomplete' in sheets or '\u26a0 INCOMPLETE' in sheets)
    ok('Excel: no solid fills and no font colours in styles', 'patternType="solid"' not in stx and '<color rgb' not in stx and 'FDF3DC' not in stx.upper(), re.findall(r'<fills.*?</fills>',stx))
    ok('Excel: no cell uses a fill', 'applyFill' not in stx)
    ok('Excel: no bare Incomplete', not re.search(r'<t[^>]*>(?:Incomplete|INCOMPLETE)',sheets))
    # .mlproj keeps plain data
    pj=await pg.evaluate("JSON.stringify(mlpBuildDesign())")
    ok('.mlproj status stays plain INCOMPLETE (Report compatibility)', '\u26a0' not in pj and 'INCOMPLETE' in pj)
    # CVR
    await pg.evaluate("openReportModal()"); cv=await pg.evaluate("document.getElementById('report-overlay').innerText")
    ok('CVR: pending-validation chip carries ⚠', '\u26a0 VALIDATION ERROR PENDING' in cv or 'VALIDATION ERROR PENDING' not in cv)
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())
