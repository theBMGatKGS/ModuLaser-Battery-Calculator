"""02.02.000 completion (Brent 10-19 1:55 PM): manual battery pick → Auto off + toast; networked ASD-160s count toward 127 per SenseNET
and share its addresses; unidentified power source → ⚠ Incomplete everywhere; manual ASD-160 alarm factor feeds validation;
Excel Brand row (no fill); brand logo in the KGS print band. Runs on the Calculator and (APP=…Toolbox) the Toolbox."""
import asyncio, os, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from test_sensenet import BUILD
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
R=[]
EXAMPLE_FILL='''() => { let z = 0;
  const fire = (e, t) => e.dispatchEvent(new Event(t, { bubbles: true }));
  document.querySelectorAll('.location').forEach(l => {
    const pick = (q, pref) => { const s = l.querySelector(q); if (!s) return; const o = [...s.options].map(x => x.value).filter(v => v && v !== 'other');
      s.value = (pref && o.find(v => pref.test(v))) || o[0]; fire(s, 'change'); };
    pick('.design-basis-select', /NFPA ?72/i); pick('.temperature-select', /^(20|21|25|77|room)/i);
    l.querySelectorAll('[data-role=module] .zone-name').forEach(i => { const r = i.closest('[data-role=module]'); const disp = /Display/i.test((r.querySelector('.type-select') || {}).value || ''); z++; i.value = disp ? ('DISPLAY ' + z) : ('FLOOR 1 ZONE ' + z); fire(i, 'input'); fire(i, 'change'); });
    l.querySelectorAll('[data-role=module] .fanspeed-select').forEach(s => { if (s.hidden) return; const o = [...s.options].map(x => x.value).filter(Boolean); if (o.length){ s.value = o[Math.min(2, o.length - 1)]; fire(s, 'change'); } });
    recalcLocation(l.dataset.loc); recalcLocation(l.dataset.loc); });
}
'''
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':1000}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await pg.goto(APP); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(800)
    await pg.evaluate(BUILD,[{'n':5}]); await pg.evaluate("document.getElementById('prompt-overlay').classList.remove('open')")
    await pg.evaluate("applyUnifiedAddressing('networked', true)"); await pg.wait_for_timeout(300); await pg.evaluate("document.getElementById('prompt-overlay').classList.remove('open')")
    L="[...document.querySelectorAll('.location')].filter(l=>l.querySelector('[data-role=module]'))[0]"
    loc=await pg.evaluate(f"{L}.dataset.loc")
    # d1
    st=await pg.evaluate(f"(()=>{{const l={L}; recalcLocation(l.dataset.loc); return [l.querySelector('.auto-battery-mode').value, l.querySelector('.battery-size-select').disabled]}})()")
    ok('Auto on; battery size stays selectable in Auto', st==['auto',False], st)
    sel=f"#location-{loc} .battery-size-select"
    opts=await pg.evaluate(f"[...document.querySelector('{sel}').options].map(o=>o.value).filter(v=>v&&v!=='other')")
    await pg.select_option(sel, opts[-1]); await pg.wait_for_timeout(300)
    st=await pg.evaluate(f"(()=>{{const l=document.getElementById('location-{loc}'); return [l.querySelector('.auto-battery-mode').value, l.querySelector('.builtin-auto-battery-toggle .ra-off').classList.contains('active'), l.querySelector('.battery-size-select').value, (document.getElementById('br-toast')||{{}}).textContent||'']}})()")
    ok('manual battery pick turns Auto off, keeps the pick, shows a toast', st[0]=='off' and st[1] and st[2]==opts[-1] and 'Auto Battery Sizing turned off' in st[3], st)
    # d3
    await pg.evaluate(EXAMPLE_FILL)
    pre=await pg.evaluate(f"(()=>{{const m=v2SheetModel(document.getElementById('location-{loc}')); return [m.status, m.dot, v2NeedsFields(document.getElementById('location-{loc}')).map(e=>e.className||e.label||String(e)).slice(0,6)]}})()")
    ok('example sheet passes before the power-source change', pre[0]=='pass', pre)
    await pg.evaluate(f"(()=>{{const l=document.getElementById('location-{loc}'); l.dataset.powerSource='unidentified'; recalcLocation('{loc}')}})()"); await pg.wait_for_timeout(300)
    m=await pg.evaluate(f"(()=>{{const m=v2SheetModel(document.getElementById('location-{loc}')); return [m.status, m.dot, v2StatusWord(m.status)]}})()")
    ok('unidentified power source → ⚠ INCOMPLETE (amber dot)', m[0]=='incomplete' and m[1]=='needs' and m[2].startswith('\u26a0'), m)
    if True:
      d=json.loads(await pg.evaluate("(()=>{const d=MLP.blank();d.project=mlpProjectInfo();d.design=mlpBuildDesign();return MLP.stringify(d,'t',mlpCalcRev(),'QA')})()"))
      ps=[x for x in d['design']['psus'] if x.get('powerSource')=='unidentified']
      ok('.mlproj: power source unidentified + INCOMPLETE', ps and ps[0]['status']=='INCOMPLETE', ps[:1])
    note=await pg.evaluate(f"(()=>{{const n=document.querySelector('#location-{loc} .br-psrc-note, #location-{loc} [class*=psrc]'); return n? n.textContent:''}})()")
    ok('on-screen ⚠ Incomplete note for the power source', '\u26a0 Incomplete' in note, note)
    await pg.evaluate(f"(()=>{{const l=document.getElementById('location-{loc}'); l.dataset.powerSource='in-house'; recalcLocation('{loc}')}})()")
    # d2
    await pg.evaluate(f"asdUiAdd('{loc}')"); await pg.wait_for_timeout(200)
    c0=await pg.evaluate("senseNetCounts()[1]")
    await pg.evaluate(f"(()=>{{const tr=document.querySelector('#location-{loc} tr[data-kind=asd160]'); const n=tr.querySelector('.asd-net'); n.value='networked'; n.dispatchEvent(new Event('change',{{bubbles:true}})); const a=document.querySelector('#location-{loc} [data-role=module] .module-address'); if(!a.value){{a.value=a.options[3].value;}} tr.querySelector('.asd-addr').value=a.value; window.__dupA=a.value; }})()")
    c1=await pg.evaluate("senseNetCounts()[1]")
    ok('networked ASD-160 counts toward SenseNET 1', c1==c0+1, [c0,c1])
    dup=await pg.evaluate("[...(addrConflicts().network[1]||[])]")
    da=await pg.evaluate("window.__dupA")
    ok('ASD-160 address equal to a module address on SenseNET 1 is a duplicate', da in dup, [da,dup])
    await pg.evaluate(f"(()=>{{const tr=document.querySelector('#location-{loc} tr[data-kind=asd160]'); tr.querySelector('.asd-addr').value='120'; }})()")
    ok('unique ASD-160 address → no duplicate', '120' not in await pg.evaluate("[...(addrConflicts().network[1]||[])]"))
    # d4
    af=await pg.evaluate(f"""(()=>{{const tr=document.querySelector('#location-{loc} tr[data-kind=asd160]'); tr.dataset.pipe=JSON.stringify({{designSens:0.1,maxTransit:120,af:0,afActivatedRaw:'false',lengthFt:100,holes:Array.from({{length:8}},(_,i)=>({{i:String(i+1),size:0.08,sens:0.5,tt:6*(i+1)}})),testPoints:[],resultsValid:'true',hasResults:true,balance:95,balanceMinLimit:80}});
      const a=tr.querySelector('.ml-af'); a.value='8'; a.dispatchEvent(new Event('change',{{bubbles:true}})); const e=asdEval(tr, tr.closest('.location')); return [tr.dataset.afSrc, e.af.src, e.af.af, e.issues.filter(i=>i.level==='error').map(i=>i.msg)]}})()""")
    ok('manual ASD-160 alarm factor feeds validation', af[0]=='manual' and af[1]=='manual' and af[2]==8 and any('alarm factor 8' in m for m in af[3]), af)
    await pg.evaluate(f"(()=>{{const tr=document.querySelector('#location-{loc} tr[data-kind=asd160]'); delete tr.dataset.pipe; recalcLocation('{loc}')}})()")
    # Excel + print band
    rows=await pg.evaluate("v2DetailRows(Array.from(document.querySelectorAll('.location')).map(el=>v2SheetModel(el)),'standard')")
    br=[r for r in rows if r.get('cells') and r['cells'][0]=='Brand']
    ok('Excel Detail: Brand row, no style (no fill)', br and br[0]['cells'][1]=='Edwards' and 'style' not in br[0], br)
    html=await pg.evaluate("v2BuildPrintHtml({level:'standard'})")
    ok('print: brand logo in the KGS band', 'class="band-logo"' in html and '#102645' in html, html.count('band-logo'))
    await pg.click('#brand-seg button[data-v="kidde-commercial"]'); await pg.wait_for_timeout(300)
    await pg.evaluate("document.getElementById('prompt-overlay').classList.remove('open')")
    html=await pg.evaluate("v2BuildPrintHtml({level:'standard'})")
    ok('print: Kidde Commercial logo after brand switch', 'alt="Kidde Commercial"' in html)
    ok('no page errors', not errs, errs[:3])
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())
