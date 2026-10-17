# 02.00.003: module table Module Type / Model / Cluster / Power fit without truncation or wrap, every sheet of Brent's file,
# a sheet with no cluster display, print (KGS) and Word (layout checked: fixed table, default font, spans, LibreOffice render).
import asyncio, os, sys, re, zipfile, io, base64, subprocess, tempfile
from playwright.async_api import async_playwright
from brent_fixture import load_brent, sheets, goto, SHOT_DIR
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'

APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:400])
SHORT={'Minimum Display':'DISP-MIN','Standard Display':'DISP-STD','Command Display':'DISP-CMD','Detector':'DETECTOR'}
# overflow: element wider than its box, unless it deliberately ellipsizes with the full text in a tooltip
FIT='''(sel)=>{const root=document.querySelector('.location-current')||document.body;const bad=[];
 const lines=e=>{const r=document.createRange();r.selectNodeContents(e);return new Set([...r.getClientRects()].filter(x=>x.width>0).map(x=>Math.round(x.top))).size;};
 root.querySelectorAll(sel).forEach(e=>{if(!e.offsetParent)return;const cs=getComputedStyle(e);
   const ell=cs.textOverflow==='ellipsis'&&cs.overflow!=='visible'&&!!e.title;
   const leaf=!e.matches('td')||!e.querySelector('select,input,button,div,span');
   if((e.scrollWidth>e.clientWidth+1&&!ell)||(leaf&&lines(e)>1))bad.push((e.className||e.tagName)+':'+(e.innerText||'').trim().slice(0,40)+' '+e.scrollWidth+'/'+e.clientWidth);});return bad;}'''
SCREEN='.devtable td, .devtable th, .devtable .calc-select-btn, .devtable .cluster-remote-hint'
ROWS='''()=>[...document.querySelectorAll('.location-current [data-role=module]')].map(r=>{const bt=s=>{const w=r.querySelector(s)?.closest('.calc-select-wrap');return w&&!w.hidden?w.querySelector('.calc-select-btn').textContent.trim():null};
  return {type:r.querySelector('.type-select').value,typeBtn:bt('.type-select'),cluster:bt('.cluster-select')||r.querySelector('.cluster-label:not([hidden])')?.textContent.trim(),power:r.querySelector('.power-select').value,powerBtn:bt('.power-select'),
   clusterPrint:r.querySelector('.cluster-print-text').textContent,powerPrint:r.querySelector('.power-print-text').textContent}})'''
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1600,'height':1000}); pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await load_brent(pg, APP); locs=await sheets(pg)
    ok("Brent's file imported (2 sheets)", len(locs)==2, locs)
    for loc in locs:
      await pg.set_viewport_size({'width':1600,'height':1000}); await goto(pg, loc)
      rows=await pg.evaluate(ROWS)
      ok(f'sheet {loc}: Module Type labels', rows and all(x['typeBtn']==SHORT[x['type']] for x in rows), [x['typeBtn'] for x in rows])
      ok(f'sheet {loc}: Cluster 2-digit only (screen + print)', all(re.fullmatch(r'\d\d',x['cluster'] or '') and re.fullmatch(r'\d\d',x['clusterPrint']) for x in rows), [(x['cluster'],x['clusterPrint']) for x in rows])
      fol=[x for x in rows if x['power'].startswith('follow:')]
      ok(f'sheet {loc}: Ribbon Path for every ribbon follower', all(x['powerBtn']=='Ribbon Path' and x['powerPrint']=='Ribbon Path' for x in fol), [(x['powerBtn'],x['powerPrint']) for x in fol])
      for w in (1600,1366):
        await pg.set_viewport_size({'width':w,'height':1000}); await pg.wait_for_timeout(250)
        bad=await pg.evaluate(FIT, SCREEN); ok(f'sheet {loc} @{w}px: no truncation/wrap', not bad, bad)
      await pg.set_viewport_size({'width':1600,'height':1000})
      await pg.locator('.location-current .devtable').screenshot(path=os.path.join(SHOT_DIR,f'columns-screen-sheet{loc}.png'))
    # print / KGS
    html=await pg.evaluate("v2BuildPrintHtml({scope:'all',level:'full'})")
    pp=await ctx.new_page(); await pp.set_viewport_size({'width':816,'height':1056}); await pp.emulate_media(media='print'); await pp.set_content(html); await pp.wait_for_timeout(800)
    heads=await pp.evaluate("[...document.querySelector('table.mods thead').rows[0].cells].map(t=>t.textContent)")
    ok('print heads', heads==['Zone','Type','Model','Cluster','Power','Fan','Addr','Standby mA','Alarm mA'], heads)
    cells=await pp.evaluate("[...document.querySelectorAll('table.mods tbody tr')].map(r=>[...r.cells].map(c=>c.textContent))")
    ok('print labels: short types, 2-digit cluster, Ribbon Path', any('DISP-MIN' in r for r in cells) and any('Ribbon Path' in r for r in cells) and not any(re.search('Follows via|Cluster 0|Minimum Display',''.join(r)) for r in cells), cells[:2])
    bad=await pp.evaluate(FIT.replace(".location-current","table.mods"), 'table.mods td, table.mods th'); ok('print: no truncation/wrap (all sheets)', not bad, bad)
    await pp.locator('table.mods').first.screenshot(path=os.path.join(SHOT_DIR,'columns-print.png'))
    # Word: structure + LibreOffice render
    b64=await pg.evaluate("(async()=>{const b=await v2BuildDocx({scope:'all',level:'standard'});const a=new Uint8Array(await b.arrayBuffer());let s='';for(const x of a)s+=String.fromCharCode(x);return btoa(s)})()")
    raw=base64.b64decode(b64); z=zipfile.ZipFile(io.BytesIO(raw)); x=z.read('word/document.xml').decode()
    sty=z.read('word/styles.xml').decode() if 'word/styles.xml' in z.namelist() else ''
    rels=z.read('word/_rels/document.xml.rels').decode(); ct=z.read('[Content_Types].xml').decode()
    ok('Word: styles.xml default font Arial wired in', 'w:rFonts w:ascii="Arial"' in sty and 'styles.xml' in rels and '/word/styles.xml' in ct)
    mods=[t for t in re.findall(r'<w:tbl>.*?</w:tbl>',x,re.S) if '>Model<' in t]
    ok('Word: module tables fixed layout, 9-col grid within 10800 dxa, no-wrap', mods and all('<w:tblLayout w:type="fixed"/>' in t and len(re.findall(r'<w:gridCol ',t))==9 and sum(map(int,re.findall(r'<w:gridCol w:w="(\d+)"',t)))<=10800 and '<w:noWrap/>' in t for t in mods), len(mods))
    ok('Word: summary labels span 7 columns', all(re.search(r'<w:gridSpan w:val="7"/>.*?Power supply quiescent \+ AUX',t,re.S) for t in mods))
    td=_od('module-columns'); dp=os.path.join(td,'export.docx'); open(dp,'wb').write(raw)
    subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',td,dp],capture_output=True,timeout=180)
    txt=subprocess.run(['pdftotext','-layout',os.path.join(td,'export.pdf'),'-'],capture_output=True,text=True).stdout
    fonts=subprocess.run(['pdffonts',os.path.join(td,'export.pdf')],capture_output=True,text=True).stdout
    one=[l for l in txt.splitlines() if 'Power supply quiescent + AUX' in l]
    ok('Word render (LibreOffice): summary label on one line, no Times fallback', one and all(re.search(r'AUX\s+\d',l) for l in one) and 'Times' not in fonts, [one[:2], [l for l in fonts.splitlines() if 'Times' in l][:2]])
    hdr=[l for l in txt.splitlines() if re.search(r'\bZone\b.*\bType\b',l)]
    ok('Word render: header row on one line (Standby mA / Alarm mA not wrapped)', hdr and all(re.search(r'Zone\s+Type\s+Model\s+Cluster\s+Power\s+Fan\s+Addr\s+Standby mA\s+Alarm mA',l) for l in hdr) and not any(re.fullmatch(r'\s*mA\s+mA\s*',l) for l in txt.splitlines()), hdr[:1])
    ok('Word render: Status label in summary row', re.search(r'Status: (PASS|FAIL|INCOMPLETE)',txt), [l for l in txt.splitlines() if 'Required Ah' in l][:2])
    rowl=[l for l in txt.splitlines() if 'NC-AreaA-D4' in l]; rowd=[l for l in txt.splitlines() if 'NC-AreaA-DSP1' in l]
    ok('Word render: module rows on one line, nothing clipped', rowl and all(re.search(r'DETECTOR\s+FHSD8330-ULF\s+01\s+Ribbon Path\s+9',l) for l in rowl)
       and rowd and all(re.search(r'DISP-MIN\s+FHSD8300-ULF\s+01\s+Own circuit · PS-1 AUX-1 \(AUX 01\)\s+N/A',l) for l in rowd), rowl[:1]+rowd[:1])
    # sheet with no cluster display (DETECTOR row on a new sheet)
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(800)
    await pg.evaluate("()=>{const l=document.querySelector('.location-current');addModuleRow(l.dataset.loc,'Detector');const r=l.querySelector('[data-role=module] .type-select');r.value='Detector';recalcLocation(l.dataset.loc);v2Refresh()}"); await pg.wait_for_timeout(300)
    nd=await pg.evaluate("(()=>{const b=document.querySelector('.location-current [data-role=module] .cluster-select').closest('.calc-select-wrap').querySelector('.calc-select-btn');return [b.textContent.trim(),b.title]})()")
    ok('no-display sheet: Cluster button short "—" with full text in tooltip', nd[0]=='—' and 'No cluster display' in nd[1], nd)
    bad=await pg.evaluate(FIT, SCREEN); ok('no-display sheet: no truncation/wrap', not bad, bad)
    ok('no page errors', not errs, errs)
    await b.close()
  print('screenshots:', SHOT_DIR); print('RESULT',sum(R),'/',len(R)); sys.exit(0 if all(R) else 1)
asyncio.run(main())
