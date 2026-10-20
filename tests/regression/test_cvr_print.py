# 02.00.005 / Toolbox 00.01.003: Cluster Validation Report print redesign (Brent approved; Toolbox c8955e4 patch).
# Renders a real multi-file .pl project to PDF (Chrome, print media) and checks running header/footer on every page,
# Page n of N, app name, chips, repeated table headers, no wrapping.
import asyncio, os, sys, subprocess, re
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from test_sensenet import fresh
import helpers; from helpers import import_files, fill_addresses
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
TB='Toolbox' in APP or 'tb-' in APP; NAME='MASD Engineering Toolbox' if TB else 'ModuLaser Battery Calculator'
import tempfile
OUT=os.path.join(os.environ.get('MLP_TEST_OUT') or tempfile.mkdtemp(prefix='mlp-test-'),'cvr-0205'); os.makedirs(OUT,exist_ok=True); TAG='tb-' if TB else 'calc-'   # QA F3
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=await b.new_page(viewport={'width':1300,'height':900}); pg.set_default_timeout(15000); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    if not await pg.evaluate("typeof cvrPageCss==='function'"):   # QA F7: baseline without the CVR redesign
        ok('CVR print redesign present (cvrPageCss)', False); await b.close(); print(f'{sum(R)}/{len(R)} passed'); sys.exit(1)
    await import_files(pg,['NFPA318-Fab-Ceiling.pl','Example Project.pl','Example Warehouse Main Room (OAP).pl'])
    await fill_addresses(pg)
    await pg.evaluate(r"""()=>{document.getElementById('project-name-input').value='Sample Project';document.getElementById('network-number-input').value='Network 1';document.getElementById('prepared-by-input').value='Designer';
      const re=/Example Project|Example Warehouse Main Room \(OAP\)|Example Warehouse Parts/g;   // neutral names in rendered images
      document.querySelectorAll('.location input').forEach(e=>{ if(typeof e.value==='string' && e.value.match(re)) e.value=e.value.replace(re,'Site'); });
      document.querySelectorAll('.location').forEach(l=>recalcLocationInner(l.dataset.loc)); if(window.syncPrintHeaders) syncPrintHeaders();}""")
    ok('cvrPageCss names this app', NAME in await pg.evaluate("cvrPageCss()"), NAME)
    await pg.evaluate("()=>{openReportModal(); document.body.classList.add('report-print'); const st=document.createElement('style');st.id='cvr-page-style';st.textContent=cvrPageCss();document.head.appendChild(st);}")
    ch=await pg.evaluate("[...document.querySelectorAll('#report-overlay .report-chip')].map(c=>c.className.split(' ')[1])")
    ok('chips: entry point and ribbon path present', 'ep' in ch and 'rp' in ch, sorted(set(ch)))
    await pg.emulate_media(media='print'); await pg.wait_for_timeout(500)
    wrap=await pg.evaluate("[...document.querySelectorAll('#report-overlay .report-table td, #report-overlay .report-table th')].filter(c=>c.offsetParent && c.getClientRects().length && c.scrollHeight>parseFloat(getComputedStyle(c).lineHeight||16)*1.9).length")
    ok('no wrapped table cells in print', wrap==0, wrap)
    ok('thead repeats (table-header-group)', await pg.evaluate("getComputedStyle(document.querySelector('#report-overlay .report-table thead')).display")=='table-header-group')
    ok('rows avoid page breaks', await pg.evaluate("getComputedStyle(document.querySelector('#report-overlay .report-table tr')).breakInside")=='avoid')
    pdf=os.path.join(OUT,TAG+'cvr.pdf'); await pg.pdf(path=pdf, format='Letter', print_background=True, prefer_css_page_size=True)
    await b.close()
  n=int(re.search(r'Pages:\s+(\d+)',subprocess.run(['pdfinfo',pdf],capture_output=True,text=True).stdout).group(1))
  ok('multi-page report', n>=2, n)
  pages=[subprocess.run(['pdftotext','-layout','-f',str(i),'-l',str(i),pdf,'-'],capture_output=True,text=True).stdout for i in range(1,n+1)]
  ok('header on every page', all('CLUSTER VALIDATION REPORT' in t and 'Sample Project · Network 1' in t for t in pages), [i+1 for i,t in enumerate(pages) if 'CLUSTER VALIDATION REPORT' not in t])
  ok('footer Page n of N on every page', all(f'Page {i+1} of {n}' in t for i,t in enumerate(pages)))
  ok('footer app name + revision on every page', all(NAME in t for t in pages))
  ok('table header repeated on continuation pages', all(('ADDRESS' in t and 'ZONE' in t) or 'QTY' in t for t in pages))
  ok('no real project names leaked', not any(x in ''.join(pages) for x in ['NDA']))
  subprocess.run(['pdftoppm','-r','70','-png','-f','1','-l','2',pdf,os.path.join(OUT,TAG+'cvr-p')])
  ok('no page errors', not errs, errs)
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())
