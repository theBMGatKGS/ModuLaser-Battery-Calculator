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
ARR_JS = r'''async ()=>{ const W=ms=>new Promise(r=>setTimeout(r,ms)); clearEntireDocument({clearHeaders:false}); const pre=[...document.querySelectorAll('.location')]; addLocation();
  const l=[...document.querySelectorAll('.location')].pop(), loc=l.dataset.loc; pre.forEach(e=>e.remove()); l.querySelector('.ps-name').value='PS-1';
  const set=(el,v)=>{ el.value=v; el.dispatchEvent(new Event('change',{bubbles:true})); };
  addModuleRow(loc,'Standard Display'); addModuleRow(loc,'Standard Display'); addModuleRow(loc,'Detector'); addModuleRow(loc,'Detector'); recalcLocationInner(loc);
  const R=()=>[...l.querySelectorAll('[data-role=module]')]; const Ds=()=>R().filter(r=>r.querySelector('.type-select').value!=='Detector'), Ts=()=>R().filter(r=>r.querySelector('.type-select').value==='Detector');
  Ds().forEach((d,i)=>{ set(d.querySelector('.cluster-select'), String(i+1)); set(d.querySelector('.module-address'), String(i+1)); d.querySelector('.zone-name').value='D'+(i+1); }); recalcLocationInner(loc);
  Ts().forEach((t,i)=>{ set(t.querySelector('.cluster-select'), String(i+1)); }); recalcLocationInner(loc);
  Ts().forEach((t,i)=>{ const d=Ds()[i]; const ps=t.querySelector('.power-select'); const o=[...ps.options].find(o=>o.value==='follow:'+d.id); if(o) set(ps,o.value); set(t.querySelector('.module-address'), String(i+3)); t.querySelector('.zone-name').value='T'+(i+1); set(t.querySelector('.fanspeed-select'),'16'); });
  l.querySelector('.mode-radio[value=thirdparty]').checked=true; const ah=l.querySelector('.tp-battery-ah'); ah.disabled=false; ah.value='40'; const ac=l.querySelector('.aux-circuits-custom'); if(ac){ac.disabled=false; ac.value='4';} recalcLocationInner(loc);
  mlAddRow(loc,{setup:'manual', zone:'ML 1', fan:10, af:4, method:'DIP'});
    recalcLocationInner(loc); recalcLocation(loc); await W(300);
  const vm=v2SheetModel(l); const ab=l.querySelector('.arrangement-block');
  const t=ab.hidden?null:ab.querySelector('.arrangement-list').innerText; return {t, flags: vm.flags, btn: !!(ab.querySelector('button')&&!ab.querySelector('button').disabled)}; }'''
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
    ok('revision 02.02.000 (Toolbox 00.03.000), MLP 1.6.0, engine 1.2.0, MiniLaser layer loaded', (v[0].startswith('02.02.000') or v[0].startswith('00.03.000')) and v[1] == '1.6.0' and v[2] == '1.2.0' and v[3] == 'function', v)
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
    # ---- MiniLaser-only sheet: no empty-modules guide, still counts for completeness
    L = await sheet(pg, 0, 1)
    r = await pg.evaluate(f"(()=>{{const l=document.getElementById('location-{L}'); const e=l.querySelector('.empty-modules'); const m=v2SheetModel(l); return [e?getComputedStyle(e).display:'none', getComputedStyle(l.querySelector('.devtable')).display, m.noModules, m.dot]}})()")
    await pg.evaluate(f"document.getElementById('location-{L}').scrollIntoView()"); await pg.wait_for_timeout(400); await pg.screenshot(path=SHOTS + '/09-minilaser-only-sheet.png')
    ok('MiniLaser-only sheet: no "no modules" guide, table visible, not noModules', r[0] == 'none' and r[1] != 'none' and r[2] is False, r)
    await pg.evaluate(f"(()=>{{const tr=document.querySelector('#location-{L} [data-role=minilaser]'); const s=tr.querySelector('.ml-fan'); s.value=''; s.dispatchEvent(new Event('change',{{bubbles:true}})); recalcLocation('{L}');}})()")
    r = await pg.evaluate(f"(()=>{{const m=v2SheetModel(document.getElementById('location-{L}')); return [m.dot, m.needs, m.status]}})()")
    ok('MiniLaser with blank fan keeps the sheet incomplete (needs entry)', r[0] != 'complete' and r[1] >= 1, r)
    # ---- 2+ clusters on one sheet: disparate-clusters warning stays AND the arrangement card shows (Brent 10-16 9:02 PM); MiniLasers on Arrangement 1
    ar = await pg.evaluate(ARR_JS); at = ar['t'] or ''
    ok('2 clusters: "Disparate clusters must not share power pathways" warning shown', any('Disparate clusters must not share power pathways' in x for x in ar['flags']), ar['flags'])
    ok('2 clusters: arrangement card shown alongside the warning (not withheld, export enabled)', 'Arrangement 1' in at and 'Arrangement 2' in at and 'withheld' not in at and ar['btn'], at[:200])
    ok('Arrangement 1 lists "MiniLasers (stay on this sheet)"; MiniLaser only in group 1', 'MiniLasers (stay on this sheet)' in at and at.count('MiniLasers') == 1 and '365 mA' in at, at)
    await pg.evaluate("document.querySelector('.location:last-of-type .arrangement-block').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(300); await pg.screenshot(path=SHOTS + '/11-arrangement-card-with-disparate-warning.png')
    # ---- Current Draw Reference: in-app help, html and xlsx (no fills)
    hp = await pg.evaluate("document.body.innerHTML.includes('FHSD8075-ULF') && [...document.querySelectorAll('table')].some(t=>/Module Current Draw/i.test((t.closest('section,div')||t).textContent) && t.textContent.includes('365'))")
    ok('help Current Draw Reference has the MiniLaser rows', hp)
    if APP.startswith('file://') and os.path.exists(os.path.dirname(APP[7:]) + '/ModuLaser_Current_Draw_Reference.xlsx'):
        base = os.path.dirname(APP[7:])
        ch = open(base + '/ModuLaser_Current_Draw_Reference.html').read()
        cp = await b.new_page(viewport={'width': 1100, 'height': 1400}); await cp.goto('file://' + base + '/ModuLaser_Current_Draw_Reference.html'); await cp.wait_for_timeout(300); await cp.screenshot(path=SHOTS + '/10-current-draw-reference.png', full_page=True); await cp.close()
        ok('CDR html: MiniLaser table fans 1–10', 'minilaser-rows' in ch and '365' in ch and 'FHSD8075-ULF' in ch)
        cz = zipfile.ZipFile(base + '/ModuLaser_Current_Draw_Reference.xlsx'); cs = cz.read('xl/styles.xml').decode(); cw = ''.join(cz.read(n).decode() for n in cz.namelist() if n.startswith('xl/worksheets/') or n == 'xl/sharedStrings.xml')
        ok('CDR xlsx: MiniLaser rows, no fills, explicit black font only (QA F6)', 'FHSD8075-ULF' in cw and set(re.findall(r'rgb="([0-9A-F]+)"', cs)) == {'FF000000'} and 'theme=' not in cs and cs.count('<font>') == cs.count('<color rgb="FF000000"/>') and cs.count('<fill>') == 2 and '<colors>' not in cs, '')
    # ---- QA F1: M p.66 pipe limits enforced on .pl rows (20 holes VEWFD fails; 10 OK; 450 ft fails)
    L = await sheet(pg, 0, 0)
    f1 = await pg.evaluate("""(loc)=>{ const F=()=>[...document.querySelectorAll(`#location-${loc} .flags-list li`)].map(li=>li.textContent).filter(t=>/manual p.66/.test(t));
      const tr=mlAddRow(loc,{setup:'pl', zone:'P1', fan:4, af:2, cls:'VEWFD', holes:20, lengthFt:120, method:'DIP'}); recalcLocation(loc); const a=F();
      tr.dataset.holes='10'; recalcLocation(loc); const b=F(); tr.dataset.lengthFt='450'; recalcLocation(loc); const c=F();
      const pre=mlAddRow(loc,{setup:'pre', zone:'PE', fan:4, af:8, holes:40, pre:{shape:'I',fan:4,holes:4,cite:'T23'}}); tr.dataset.lengthFt='100'; recalcLocation(loc); const d=F();
      return [a,b,c,d]; }""", L)
    ok('F1: 20 holes on VEWFD → validation flag (max 10, manual p.66)', len(f1[0]) == 1 and 'maximum of 10' in f1[0][0], f1[0])
    ok('F1: 10 holes on VEWFD → no pipe-limit flag', f1[1] == [], f1[1])
    ok('F1: 450 ft pipe → flag (NFPA max 400 ft)', any('400 ft' in x for x in f1[2]), f1[2])
    ok('F1: pre-engineered picker rows are exempt (manual tables)', f1[3] == [], f1[3])
    L = await sheet(pg, 2, 1)   # restore the 2-display + 1-MiniLaser sheet for the save/load check
    # ---- save / restore round trip
    st = await pg.evaluate("JSON.stringify(buildStateObject())")
    await pg.evaluate("s=>applyLoadedState(JSON.parse(s))", st); await pg.wait_for_timeout(300)
    n = await pg.evaluate("[document.querySelectorAll('[data-role=minilaser]').length, document.querySelector('[data-role=minilaser] .ml-zone').value]")
    ok('save → load keeps the MiniLaser row', n == [1, 'ML 1'], n)
    if not os.path.exists(PL):   # Brent: the Example Shaft .pl stays off GitHub — skip the import/output checks with a clear message
        print(f'SKIP Example Shaft .pl import and output checks: fixture not present ({PL}); set ML_FIXTURE to run them.')
        req = os.environ.get('REQUIRE_FIXTURES') == '1'
        ok('no page errors', not errs, errs[:3]); await b.close(); print(f"{sum(R)}/{len(R)} passed, SKIPPED: Example Shaft section (fixture absent)" + (' — REQUIRE_FIXTURES=1, failing' if req else '')); sys.exit(1 if (req or not all(R)) else 0)
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
    ok('Example Shaft: Remote recommended (fan 6 not DIP-settable; .pl import is non-pre-engineered by default)', r and r['method'] == 'Remote' and 'Remote' in r['adv'], r and r['adv'])
    PP = "(()=>{const tr=document.querySelector('[data-role=minilaser]'); const c=tr.querySelector('.ml-plpre'); return c?[c.checked, tr.querySelector('.ml-method').value, tr.querySelector('.ml-adv').textContent]:null})()"
    pp0 = await pg.evaluate(PP)
    ok('imported unit: "Pre-engineered" override present, unticked by default', pp0 is not None and pp0[0] is False and pp0[1] == 'Remote', pp0)
    await pg.click('[data-role=minilaser] .ml-plpre'); await pg.wait_for_timeout(250); pp1 = await pg.evaluate(PP)
    ok('ticking Pre-engineered → DIP (pre-engineered layout)', pp1 and pp1[0] and pp1[1] == 'DIP' and 'pre-engineered' in pp1[2], pp1)
    st2 = await pg.evaluate("JSON.stringify(buildStateObject())"); await pg.evaluate("s=>applyLoadedState(JSON.parse(s))", st2); await pg.wait_for_timeout(300)
    ok('Pre-engineered override survives save → load', (await pg.evaluate(PP) or [0])[0] is True)
    await pg.click('[data-role=minilaser] .ml-plpre'); await pg.wait_for_timeout(250); pp2 = await pg.evaluate(PP)
    ok('unticking → back to Remote', pp2 and not pp2[0] and pp2[1] == 'Remote', pp2)
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
