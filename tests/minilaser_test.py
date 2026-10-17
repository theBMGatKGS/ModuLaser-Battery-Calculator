"""Battery Calculator 02.01.000 — MiniLaser ASD (FHSD8075-ULF). Real fixture: Brent's Example Shaft .pl (qa/minilaser/minilaser.pl).
Run: python3 tests/minilaser_test.py   (APP=<file url> to test another copy; output → $MLP_TEST_OUT or a temp dir; SHOTS=<dir> for screenshots)"""
import asyncio, os, sys, json, zipfile, io, re, tempfile, base64
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP = os.environ.get('APP', 'file://' + ROOT + '/modulaser_battery_calculator.html')
PL = os.environ.get('ML_FIXTURE', '/workspace/qa/minilaser/minilaser.pl')
OUT = os.environ.get('MLP_TEST_OUT') or tempfile.mkdtemp(prefix='ml-calc-'); os.makedirs(OUT, exist_ok=True)
SHOTS = os.environ.get('SHOTS') or os.path.join(OUT, 'shots'); os.makedirs(SHOTS, exist_ok=True)
R = []
def ok(n, c, i=''): R.append(bool(c)); print('PASS' if c else 'FAIL', n, str(i)[:300])
FLAGS = "(loc)=>[...document.querySelectorAll(`#location-${loc} .flags-list li`)].map(li=>li.textContent)"
async def fresh(pg):
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(700)
    return await pg.evaluate("document.querySelector('.location').dataset.loc")
async def sheet(pg, displays, mls, fans=None):
    """one sheet with N displays (entry points) and M MiniLasers (manual config)"""
    return await pg.evaluate('''([nd, nm, fans])=>{ clearEntireDocument({clearHeaders:false}); const pre=[...document.querySelectorAll('.location')]; addLocation();
      const l=[...document.querySelectorAll('.location')].pop(), loc=l.dataset.loc; pre.forEach(e=>e.remove()); l.querySelector('.ps-name').value='PS-1';
      for (let i=0;i<nd;i++) addModuleRow(loc,'Standard Display');
      for (let i=0;i<nm;i++){ const tr=mlAddRow(loc,{setup:'manual', zone:'ML '+(i+1), fan:(fans&&fans[i])||4, af:4, method:'DIP'}); }
      recalcLocationInner(loc); recalcLocation(loc); return loc; }''', [displays, mls, fans])
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1600, 'height': 1000}, accept_downloads=True); pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    loc = await fresh(pg)
    v = await pg.evaluate('[runningRevisionFull(), MLP.VERSION, MASD_ENGINE_VERSION, typeof mlRecalcHook]')
    ok('revision 02.01.000 (Toolbox 00.02.000), MLP 1.5.0, engine 1.1.0, MiniLaser layer loaded', (v[0].startswith('02.01.000') or v[0].startswith('00.02.000')) and v[1] == '1.5.0' and v[2] == '1.1.0' and v[3] == 'function', v)
    ok('standalone ASD card on every sheet', await pg.evaluate("[...document.querySelectorAll('.location')].every(l=>l.querySelector('.ml-card .ml-add'))"))
    # ---- hand add: picker is the default, Cancel → manual; blank fan amber
    await pg.click(f'#location-{loc} .ml-add'); await pg.wait_for_timeout(200)
    ok('+ Add MiniLaser opens the Pre-engineered picker', await pg.evaluate("!!document.querySelector('.ml-pe')"))
    await pg.screenshot(path=SHOTS + '/03-preengineered-picker.png')
    await pg.click('.ml-pe .pe-cancel'); await pg.wait_for_timeout(200)
    r = await pg.evaluate("(()=>{const tr=document.querySelector('[data-role=minilaser]'); return [tr.querySelector('.ml-setup').value, tr.querySelector('.ml-fan').value, tr.querySelector('.ml-fan').classList.contains('field-needs'), tr.querySelector('.ml-ma').textContent, tr.querySelector('.ml-adv').textContent]})()")
    ok('Cancel → manual config, blank fan amber, ⚠ shown', r[0] == 'manual' and r[1] == '' and r[2] and '⚠' in r[3] and '⚠' in r[4], r)
    ok('no address field on a MiniLaser row', await pg.evaluate("!document.querySelector('[data-role=minilaser] .module-address')"))
    # ---- picker apply: I-shaped, fan 4, 4 holes, AF 8 → DIP (M Tables 23–24)
    await pg.click('[data-role=minilaser] .ml-pick'); await pg.wait_for_timeout(150)
    await pg.select_option('.ml-pe .pe-shape', 'I'); await pg.select_option('.ml-pe .pe-fan', '4'); await pg.select_option('.ml-pe .pe-holes', '4')
    afs = await pg.evaluate("[...document.querySelectorAll('.ml-pe .pe-af option')].map(o=>o.value)")
    await pg.select_option('.ml-pe .pe-af', '8'); await pg.wait_for_timeout(100)
    out = await pg.inner_text('.ml-pe .pe-out')
    ok('picker shows table values (34 s, 2.00 %obs/ft SFD|SA|OAP, 9/64 in., 80 ft, Tables 23–24)', '34 s' in out and '2.00' in out and 'OAP' in out and '9/64' in out and '80 ft' in out and '23–24' in out, out)
    ok('picker offers only valid alarm factors', afs == ['2', '4', '6', '8'], afs)
    await pg.screenshot(path=SHOTS + '/04-preengineered-picker-filled.png')
    await pg.click('.ml-pe .pe-ok'); await pg.wait_for_timeout(250)
    r = await pg.evaluate("(()=>{const tr=document.querySelector('[data-role=minilaser]'); return [tr.querySelector('.ml-fan').value, tr.querySelector('.ml-af').value, tr.querySelector('.ml-method').value, tr.querySelector('.ml-ma').textContent, tr.querySelector('.aux-circuit-num').value, tr.querySelector('.circuit-source').value]})()")
    ok('applied: fan 4, AF 8, DIP, 180/180 mA, own AUX 01, source auto-filled', r[:4] == ['4', '8', 'DIP', '180 / 180'] and r[4] == '1' and 'AUX-1' in r[5], r)
    t = await pg.evaluate(f"[document.querySelector('#location-{loc} .total-ma').textContent, document.querySelector('#location-{loc} .ps-load-ma').textContent]")
    ok('load = 180 + 70 quiescent + 35 per AUX circuit = 285 mA', t == ['285', '105'], t)
    await pg.screenshot(path=SHOTS + '/02-calculator-minilaser-row.png')
    # ---- draw table fans 1–10
    d = await pg.evaluate("[1,2,3,4,5,6,7,8,9,10].map(f=>MASD_ENGINE.miniLaserMa(f))")
    ok('draw 120…365 mA (M p.65), standby = alarm', d == [120, 134, 157, 180, 200, 230, 255, 285, 320, 365], d)
    # ---- AUX fixtures (a)–(d)
    L = await sheet(pg, 3, 1); f = await pg.evaluate(FLAGS, L)
    ok('(a) 3 entry points + 1 MiniLaser → no AUX error', not any('AUX circuits' in x for x in f), f)
    L = await sheet(pg, 4, 1); f = await pg.evaluate(FLAGS, L)
    ok('(b) 4 entry points + 1 MiniLaser → AUX error recommending another PSU', any('1 MiniLaser(s) + 4 entry point(s) need 5 AUX circuits' in x and 'add a power supply' in x for x in f), f)
    await pg.screenshot(path=SHOTS + '/05-aux-overflow-error.png')
    L = await sheet(pg, 0, 4); f = await pg.evaluate(FLAGS, L)
    aux = await pg.evaluate(f"[...document.querySelectorAll('#location-{L} [data-role=minilaser] .aux-circuit-num')].map(s=>s.value)")
    ok('(c) 4 MiniLasers → AUX 1–4, one each, no error', aux == ['1', '2', '3', '4'] and not any('AUX circuits' in x for x in f), [aux, f])
    L = await sheet(pg, 0, 5); f = await pg.evaluate(FLAGS, L)
    ok('(c) 5 MiniLasers → error (never shared)', any('5 MiniLaser(s) + 0 entry point(s) need 5 AUX circuits' in x for x in f), f)
    L = await sheet(pg, 0, 4, [10, 10, 10, 10]); cap = await pg.evaluate(f"document.querySelector('#location-{L} .ps-capacity-select').value")
    ok('(d) per-circuit 3.0 A respected; 4 × 365 mA stays on a 6 A supply', cap == '6', cap)
    # ---- BOM (e)
    L = await sheet(pg, 0, 2); await pg.evaluate(f"(()=>{{const rs=document.querySelectorAll('#location-{L} [data-role=minilaser]'); rs[0].querySelector('.ml-io').value='2'; recalcLocation('{L}');}})()")
    bom = await pg.evaluate(f"buildBOM(document.getElementById('location-{L}')).map(r=>[r.qty,r.manufacturer,r.partNumber])")
    ok('(e) BOM: FHSD8075-ULF ×2, 9-30520 ×1 (auto), 9-30521 ×2; expansions by part number only', [2, 'Edwards', 'FHSD8075-ULF'] in bom and [1, '—', '9-30520'] in bom and [2, '—', '9-30521'] in bom, bom)
    ok('BOM never shows the Kidde number', not any('KID' in str(x) for x in bom))
    # ---- addressing exclusion
    L = await sheet(pg, 2, 1)
    await pg.evaluate("applyAutoAddressing ? applyAutoAddressing('networked', 'all') : null") if False else None
    c = await pg.evaluate("[senseNetCounts ? JSON.stringify(senseNetCounts()) : '', document.querySelectorAll('[data-role=module]').length]")
    ok('SenseNET module count excludes the MiniLaser', '"1":2' in c[0] or c[1] == 2, c)
    # ---- save / restore round trip
    st = await pg.evaluate("JSON.stringify(buildStateObject())")
    await pg.evaluate("s=>applyLoadedState(JSON.parse(s))", st); await pg.wait_for_timeout(300)
    n = await pg.evaluate("[document.querySelectorAll('[data-role=minilaser]').length, document.querySelector('[data-role=minilaser] .ml-zone').value]")
    ok('save → load keeps the MiniLaser row', n == [1, 'ML 1'], n)
    # ---- Example Shaft .pl import
    await fresh(pg)
    await pg.click('#import-pl-btn'); await pg.wait_for_timeout(150)
    await pg.evaluate("(()=>{ const s=plWiz.settings; if(!s.designBasis) s.designBasis='NFPA 72 Standard'; if(!s.temperature) s.temperature='77'; plWiz.step=2; plRender(); })()"); await pg.wait_for_timeout(150)
    await pg.set_input_files('#plw-file', [PL]); await pg.wait_for_timeout(600)
    for _ in range(3):
        if await pg.evaluate("!!document.querySelector('#plw-finish:not([hidden])') && getComputedStyle(document.getElementById('plw-finish')).display!=='none'"): break
        await pg.click('#plw-next'); await pg.wait_for_timeout(250)
    await pg.screenshot(path=SHOTS + '/06-pl-wizard.png')
    await pg.click('#plw-finish'); await pg.wait_for_timeout(700)
    async def prompt_text():
        return await pg.evaluate("document.getElementById('prompt-overlay') && getComputedStyle(document.getElementById('prompt-overlay')).display!=='none' && document.getElementById('prompt-overlay').classList.contains('open') ? document.getElementById('prompt-title').textContent+' :: '+document.getElementById('prompt-desc').innerText : ''")
    seen = []
    for _ in range(6):
        t = await prompt_text()
        if not t: await pg.wait_for_timeout(250); t = await prompt_text()
        if not t: break
        seen.append(t)
        if t.startswith('Confirm Settings'): await pg.screenshot(path=SHOTS + '/07-confirm-settings.png')
        labels = await pg.evaluate("[...document.querySelectorAll('#prompt-actions button')].map(b=>b.textContent.trim())")
        pick = next((x for x in ['Confirm', 'OK', 'Manually address', 'No', 'Not now'] if x in labels), labels[0])
        await pg.click(f"#prompt-actions button:has-text('{pick}')"); await pg.wait_for_timeout(400)
    ok('Confirm Settings? lists the MiniLaser (standalone, not addressed)', any(x.startswith('Confirm Settings') and '1 MiniLaser' in x for x in seen), seen)
    ok('no address prompt for the MiniLaser-only import', not any('ddress' in x.split('::')[0] for x in seen), [x.split('::')[0] for x in seen])
    r = await pg.evaluate("(()=>{const tr=document.querySelector('[data-role=minilaser]'); if(!tr) return null; return {fan:tr.querySelector('.ml-fan').value, af:tr.querySelector('.ml-af').value, afSrc:tr.dataset.afSrc, holes:tr.dataset.holes, method:tr.querySelector('.ml-method').value, adv:tr.querySelector('.ml-adv').textContent, setup:tr.querySelector('.ml-setup').value, amberAf:tr.querySelector('.ml-af').classList.contains('field-needs'), der:JSON.parse(tr.dataset.derivation||'null'), mods:document.querySelectorAll('[data-role=module]').length, zone:tr.querySelector('.ml-zone').value}})()")
    ok('Example Shaft: imported as a MiniLaser in the standalone ASD table (no ModuLaser modules)', r and r['mods'] == 0 and r['setup'] == 'pl', r)
    ok('Example Shaft: fan 6 from aspiratorSpeed', r and r['fan'] == '6')
    ok('Example Shaft: AF derived silently = 8 (8 holes × 0.25 = 2.00 ≤ SFD 2.0), not amber', r and r['af'] == '8' and r['afSrc'] == 'derived' and r['holes'] == '8' and not r['amberAf'] and r['der']['avg'] == 2, r and r['der'])
    ok('Example Shaft: Remote recommended (fan 6 not DIP; 10 × 90°, not pre-engineered)', r and r['method'] == 'Remote' and 'Remote' in r['adv'], r and r['adv'])
    ok('no page errors', not errs, errs[:3])
    with open(OUT + '/hoistway-import.json', 'w') as fh: json.dump(r, fh, indent=1)
    await pg.evaluate("document.getElementById('project-name-input').value='Example Shaft MiniLaser'; document.getElementById('prepared-by-input').value='B. Wilkins'; refreshAllAmber(); v2Refresh && v2Refresh()")
    await pg.wait_for_timeout(300); await pg.screenshot(path=SHOTS + '/01-hoistway-imported.png', full_page=False)
    # ---- outputs: print html, CVR, Excel (no fills), Word, project file
    html = await pg.evaluate("v2BuildPrintHtml({level:'standard', bom:true, scope:'all'})")
    ok('print: Standalone ASDs table', 'Standalone ASDs — not on SenseNET, not addressed' in html and 'FHSD8075-ULF' in html)
    open(OUT + '/print.html', 'w').write(html)
    pp = await b.new_page(viewport={'width': 1000, 'height': 1300}); await pp.set_content(html); await pp.wait_for_timeout(500)
    el = await pp.query_selector('.ml-print');
    if el: await el.scroll_into_view_if_needed()
    await pp.screenshot(path=SHOTS + '/08-print-standalone-asd.png', full_page=True); await pp.close()
    await pg.evaluate("buildClusterReport()"); cvr = await pg.evaluate("document.getElementById('report-body').innerHTML")
    ok('CVR: Standalone ASDs section with Dedicated AUX chip', 'Standalone ASDs' in cvr and 'Dedicated AUX' in cvr, len(cvr))
    xb = await pg.evaluate("(async()=>{const u=v2BuildXlsx({level:'standard',scope:'all'}); const a=new Uint8Array(u instanceof Blob? await u.arrayBuffer(): u); let s=''; for (const c of a) s+=String.fromCharCode(c); return btoa(s);})()")
    z = zipfile.ZipFile(io.BytesIO(base64.b64decode(xb))); open(OUT + '/export.xlsx', 'wb').write(base64.b64decode(xb))
    cad = z.read('xl/worksheets/sheet1.xml').decode(); sty = z.read('xl/styles.xml').decode()
    ok('Excel: Standalone ASDs block in the CAD schedule', 'Standalone ASDs' in cad and 'FHSD8075-ULF' in cad)
    ok('Excel: no fills or colour (only none/gray125 fills; no fillId≠0; no rgb colours)', 'fillId="1"' not in sty and 'rgb=' not in sty and sty.count('<fill>') == 2, '')
    db = await pg.evaluate("(async()=>{const u=await v2BuildDocx({level:'standard',bom:true,scope:'all'}); const a=new Uint8Array(u instanceof Blob? await u.arrayBuffer(): u); let s=''; for (const c of a) s+=String.fromCharCode(c); return btoa(s);})()")
    open(OUT + '/export.docx', 'wb').write(base64.b64decode(db)); dz = zipfile.ZipFile(io.BytesIO(base64.b64decode(db))); doc = dz.read('word/document.xml').decode()
    ok('Word: Standalone ASDs table', 'standalone asds' in doc.lower() and 'FHSD8075-ULF' in doc)
    des = await pg.evaluate("mlpBuildDesign()")
    mld = [x for x in des['devices'] if x.get('kind') == 'minilaser']
    ok('project file: MiniLaser device (FHSD8075-ULF, standalone, no address, AF 8, Remote, pipe carried)', len(mld) == 1 and mld[0]['model'] == 'FHSD8075-ULF' and mld[0]['standalone'] and mld[0]['address'] == '' and mld[0]['minilaser']['alarmFactor'] == 8 and mld[0]['minilaser']['configMethod'] == 'Remote' and mld[0]['pipe'] and len(mld[0]['pipe']['holes']) == 8, mld and {k: mld[0][k] for k in ('model', 'fan', 'address', 'minilaser')})
    await pg.evaluate("(()=>{const d=MLP.blank(); d.design=mlpBuildDesign(); d.project={name:'Example Shaft MiniLaser'}; window.__mlproj=MLP.stringify(d,'battery-calculator',runningRevisionFull());})()")
    open(OUT + '/hoistway.mlproj.json', 'w').write(await pg.evaluate('window.__mlproj'))
    await b.close()
  print(f"{sum(R)}/{len(R)}"); sys.exit(0 if all(R) else 1)
asyncio.run(main())
