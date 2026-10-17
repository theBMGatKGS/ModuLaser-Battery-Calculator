import asyncio, json, sys, os, shutil
from playwright.async_api import async_playwright
from helpers import pick_step1, confirm_settings
import os as _os, tempfile as _tf
MLP_OUT=_os.environ.get('MLP_TEST_OUT') or _tf.mkdtemp(prefix='mlp-test-')   # all generated output goes here (QA r3)
def _od(*p):
    d=_os.path.join(MLP_OUT,*p); _os.makedirs(d,exist_ok=True); return d.rstrip('/')+'/'
APP='file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html'
T='/workspace/plbuild/t/'; SH=_od('calcshots')
FILES={'bwdg':'BWDG1.pl','solano':'Solano Prison Vacaville CA.pl','boyers':'Boyers Roadway_Re-Calc Pipes.pl','deck':'Deck MDA-A-D2.pl','fmp':'Factory Motor Parts ASRS Main Room (OAP).pl'}
res=[]
def ok(name,cond,info=''):
    res.append((name,bool(cond),info)); print(('PASS' if cond else 'FAIL'),name,info)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1500,'height':1000})
        pg=await ctx.new_page(); pg.set_default_timeout(180000)
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto(APP); await pg.wait_for_timeout(500)
        ok('no page errors on load', not errs, ';'.join(errs))
        # menu bar
        await pg.click('#menu-file-btn'); await pg.wait_for_timeout(150)
        await pg.screenshot(path=SH+'01-menu-file.png', clip={'x':0,'y':0,'width':1500,'height':520})
        await pg.keyboard.press('Escape')
        await pg.focus('#menu-edit-btn'); await pg.keyboard.press('ArrowDown'); await pg.wait_for_timeout(100)
        foc=await pg.evaluate('document.activeElement.id')
        ok('keyboard opens Edit menu and focuses first item', foc=='add-location-menu-btn', foc)
        await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(100)
        foc=await pg.evaluate('document.activeElement.id'); ok('ArrowRight moves to View menu', foc=='cluster-report-btn', foc)
        await pg.keyboard.press('Escape')
        ids=['new-calc-btn','import-calc-btn','import-pl-menu-btn','linked-pl-btn','save-as-menu-btn','export-xlsx-btn','print-menu-btn','print-bom-toggle','add-location-menu-btn','clear-calc-btn','confirm-defaults-btn','clear-saved-btn','cluster-report-btn','help-btn','howdoi-toolbar-btn','revision-log-menu-btn','import-pl-btn','add-location-btn','save-as-copy-btn','print-btn','save-indicator']
        miss=await pg.evaluate('ids=>ids.filter(i=>!document.getElementById(i))',ids); ok('every function reachable (ids present)', not miss, str(miss))
        # existing behaviours
        n0=await pg.evaluate("document.querySelectorAll('.location').length")
        await pg.click('#add-location-btn'); n1=await pg.evaluate("document.querySelectorAll('.location').length"); ok('+ Add Location (quick row)', n1==n0+1)
        await pg.click('#menu-edit-btn'); await pg.click('#add-location-menu-btn'); n2=await pg.evaluate("document.querySelectorAll('.location').length"); ok('Edit > + Add Location', n2==n1+1)
        await pg.click('#menu-edit-btn'); await pg.click('#confirm-defaults-btn'); await pg.wait_for_timeout(100)
        await pg.click('#menu-edit-btn'); await pg.click('#clear-calc-btn'); await pg.wait_for_timeout(150)
        ok('Clear opens prompt', await pg.evaluate("document.getElementById('prompt-overlay').classList.contains('open')"))
        await pg.click('#prompt-actions >> text=Entire file'); await pg.click('#prompt-actions >> text=Clear headers too'); await pg.click('#prompt-actions >> text=Clear entire file')
        ok('Clear entire file -> 1 sheet', await pg.evaluate("document.querySelectorAll('.location').length")==1)
        ok('custom listboxes present', await pg.evaluate("document.querySelectorAll('.calc-select-btn').length")>5)
        ok('needs-entry highlights present', await pg.evaluate("document.querySelectorAll('.field-needs').length")>0)
        await pg.click('#menu-view-btn'); await pg.click('#cluster-report-btn'); await pg.wait_for_timeout(100)
        ok('View > Cluster Report opens', await pg.evaluate("document.getElementById('report-overlay').classList.contains('open')")); await pg.keyboard.press('Escape')
        await pg.click('#menu-help-btn'); await pg.click('#revision-log-menu-btn'); await pg.wait_for_timeout(100)
        rev=await pg.evaluate("document.getElementById('about-revision-value').textContent"); ok('revision shown', rev.startswith('02.00.004_'), rev)
        await pg.click('#help-close-btn')
        # wizard
        await pg.click('#import-pl-btn'); await pg.wait_for_timeout(150)
        await pg.screenshot(path=SH+'02-wizard-step1-battery.png')
        await pick_step1(pg)
        await pg.click('#plw-next')
        await pg.set_input_files('#plw-file',[T+f for f in FILES.values()]); await pg.wait_for_function('plWiz.files.length==%d' % len(FILES), timeout=30000)
        nf=await pg.evaluate('plWiz.files.length'); ok('5 files parsed', nf==5, str(nf))
        # Boyers: untick 2 of 5 groups
        bi=await pg.evaluate("plWiz.files.findIndex(f=>f.fileName.startsWith('Boyers'))")
        await pg.click(f'[data-grp="{bi}:1"]'); await pg.click(f'[data-grp="{bi}:3"]')
        await pg.screenshot(path=SH+'03-wizard-step2-files.png', full_page=False)
        await pg.click('#plw-next'); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SH+'04-wizard-step3-rename-over16.png')
        msg=None
        await pg.click('#plw-next'); msg=await pg.text_content('#plw-msg'); ok('step 3 blocks names >16', '16' in msg, msg)
        await pg.click('#plw-suggest-all'); await pg.wait_for_timeout(200)
        await pg.click('#plw-next'); await pg.wait_for_timeout(200)
        st=await pg.evaluate('plWiz.step'); m=await pg.text_content('#plw-msg'); ok('step 3 passes after shortening', st==4, m)
        if st!=4:
            await pg.screenshot(path=SH+'debug.png'); 
        await pg.wait_for_timeout(200)
        await pg.screenshot(path=SH+'05-wizard-step4-psu-review.png')
        ok('step 4 prompt to group detectors shown', await pg.evaluate("!!document.querySelector('.plw-prompt') && /Group detectors to a power supply/.test(document.querySelector('.plw-prompt').textContent)"))
        tray=await pg.evaluate('''()=>Object.entries(plWiz.unassignedByGroup).map(([k,u])=>{const [fi,gi]=k.split(':').map(Number);return {file:plWiz.files[fi].fileName,group:plWiz.files[fi].groups[gi].origName,n:u.length}})''')
        dk=[t for t in tray if t['file'].startswith('Deck')]
        ok('Deck lone detectors land in Unassigned tray', sum(t['n'] for t in dk)>0, json.dumps(dk))
        ok('BWDG has nothing unassigned', all(t['n']==0 for t in tray if t['file']=='BWDG1.pl'), '')
        nun=await pg.evaluate('plUnassignedCount()')
        dis=await pg.evaluate("document.getElementById('plw-finish').disabled"); m=await pg.text_content('#plw-msg')
        ok('Create blocked with "N detectors still unassigned"', dis and f'{nun} detectors still unassigned' in m, m)
        await pg.locator('.plw-tray').first.scroll_into_view_if_needed()
        await pg.screenshot(path=SH+'05b-wizard-step4-unassigned-tray.png')
        await pg.locator('#plw-msg').scroll_into_view_if_needed()
        await pg.screenshot(path=SH+'05c-wizard-step4-blocked-unassigned.png')
        # Move-to from the tray onto a new supply
        dgk=await pg.evaluate("Object.keys(plWiz.unassignedByGroup).find(k=>plWiz.unassignedByGroup[k].length && plWiz.files[+k.split(':')[0]].fileName.startsWith('Deck'))")
        await pg.click(f'[data-addpsu="{dgk}"]'); await pg.wait_for_timeout(100)
        before=await pg.evaluate(f'plWiz.unassignedByGroup["{dgk}"].length'); last=await pg.evaluate(f'plWiz.psuByGroup["{dgk}"].length-1')
        await pg.locator(f'.plw-tray[data-gk="{dgk}"] .plw-move').first.select_option(str(last)); await pg.wait_for_timeout(100)
        after=await pg.evaluate(f'plWiz.unassignedByGroup["{dgk}"].length'); onp=await pg.evaluate(f'plWiz.psuByGroup["{dgk}"][{last}].devices.length')
        ok('Move to… from tray onto added PSU', after==before-1 and onp==1, f'{before}->{after}, psu {onp}')
        info=await pg.evaluate('''()=>Object.entries(plWiz.psuByGroup).map(([k,ps])=>{const [fi,gi]=k.split(':').map(Number);const f=plWiz.files[fi];return {file:f.fileName,group:f.groups[gi].origName,psus:ps.map(p=>({det:p.devices.filter(d=>d.kind==='detector').length,disp:p.devices.filter(d=>d.kind==='display').length,ah:+plRequiredAh(p.devices).toFixed(1),fromFile:!!p.fromFile}))}})''')
        json.dump(info,open(_od('plbuild')+'psu_info.json','w'),indent=1)
        bw=[g for g in info if g['file']=='BWDG1.pl'][0]
        ok('BWDG 6 detectors split to <=4 per PSU', sum(p['det'] for p in bw['psus'])==6 and all(p['det']<=4 for p in bw['psus']) and len(bw['psus'])>=2, json.dumps(bw['psus']))
        ok('BWDG splits 4+display / 2', sorted((p['det'],p['disp']) for p in bw['psus'])==[(2,0),(4,1)], json.dumps(bw['psus']))
        so=[g for g in info if g['file'].startswith('Solano')][0]
        ok('Solano seeded from 2 file PSUs', sum(p['fromFile'] for p in so['psus'])==2, json.dumps(so['psus']))
        by=[g['group'] for g in info if g['file'].startswith('Boyers')]
        ok('Boyers group selection (3 of 5)', len(by)==3, str(by))
        allp=[p for g in info for p in g['psus']]
        ok('all PSUs satisfy rules', all(p['det']<=4 and p['disp']<=1 and p['ah']<=65 for p in allp), f'{len(allp)} PSUs')
        # violation test: move a detector into the full BWDG PSU
        k=[k for k in await pg.evaluate('Object.keys(plWiz.psuByGroup)') if k.startswith(str(await pg.evaluate("plWiz.files.findIndex(f=>f.fileName==='BWDG1.pl')"))+':')][0]
        await pg.evaluate(f'''()=>{{const ps=plWiz.psuByGroup["{k}"]; const big=ps.find(p=>p.devices.filter(d=>d.kind==='detector').length===4); const other=ps.find(p=>p!==big&&p.devices.some(d=>d.kind==='detector')); big.devices.push(other.devices.splice(other.devices.findIndex(d=>d.kind==='detector'),1)[0]); plRender();}}''')
        dis=await pg.evaluate("document.getElementById('plw-finish').disabled"); ok('violation blocks Create sheets', dis)
        card=pg.locator('.plw-psu.bad').first; await card.scroll_into_view_if_needed()
        await pg.screenshot(path=SH+'06-wizard-step4-violation-blocked.png')
        # move it back via dropdown
        await pg.evaluate(f'''()=>{{plBuildSuggestions(); plRender();}}''')
        ok('re-suggest clears violation (tray still blocks)', await pg.evaluate("plStep4Problems().every(p=>/still unassigned|needs at least one power supply/.test(p))") and await pg.evaluate("document.getElementById('plw-finish').disabled"))
        # Pack into fewest on every Area/Group with a non-empty tray -> unblocks
        for gk in await pg.evaluate("Object.keys(plWiz.unassignedByGroup).filter(k=>plWiz.unassignedByGroup[k].length)"):
            await pg.click(f'[data-pack="{gk}"]'); await pg.wait_for_timeout(50)
        ok('Pack into fewest unblocks Create sheets', not await pg.evaluate("document.getElementById('plw-finish').disabled") and await pg.evaluate('plUnassignedCount()')==0, await pg.text_content('#plw-msg'))
        allp=await pg.evaluate("Object.values(plWiz.psuByGroup).flat().map(p=>p.devices.length?1:0)"); allp=[1]*sum(allp)
        dkp=await pg.evaluate("Object.entries(plWiz.psuByGroup).filter(([k])=>plWiz.files[+k.split(':')[0]].fileName.startsWith('Deck')).reduce((n,[k,p])=>n+p.length,0)"); print('Deck PSUs after pack', dkp)
        # re-import mode: new devices land in tray
        upd=await pg.evaluate('''()=>{const sv={m:plWiz.mode,p:plWiz.psuByGroup,u:plWiz.unassignedByGroup}; plWiz.mode='update'; plBuildSuggestions(); const r={psus:Object.values(plWiz.psuByGroup).flat().length, un:plUnassignedCount()}; plWiz.mode=sv.m; plWiz.psuByGroup=sv.p; plWiz.unassignedByGroup=sv.u; plRender(); return r;}''')
        ok('re-import: new devices start in Unassigned tray', upd['psus']==0 and upd['un']>0, json.dumps(upd))
        npsu=len(allp)
        import time; t0=time.time(); await pg.click('#plw-finish'); await pg.wait_for_timeout(500); await confirm_settings(pg); print('finish secs', round(time.time()-t0,1))
        nloc=await pg.evaluate("document.querySelectorAll('.location').length"); ok('one sheet per PSU', nloc==npsu, f'{nloc} sheets / {npsu} PSUs')
        e2=[e for e in errs]; ok('no page errors after import', not e2, ';'.join(e2[:3]))
        rows=await pg.evaluate('''()=>{const l=[...document.querySelectorAll('.location')].find(l=>l.querySelector('.ps-location').value==='Area A');return [...l.querySelectorAll('[data-role=module]')].map(r=>({t:r.querySelector('.type-select').value,z:r.querySelector('.zone-name').value,f:r.querySelector('.fanspeed-select').value,a:r.querySelector('.module-address').value,needs:r.querySelector('.module-address').classList.contains('field-needs'),k:r.dataset.plKey}))}''')
        ok('BWDG sheet prefilled (Minimum Display + fan speeds)', rows[0]['t']=='Minimum Display' and all(r['f'] for r in rows[1:]), json.dumps(rows)[:300])
        ok('address left blank + needs-entry highlight', all(r['a']=='' and r['needs'] for r in rows), '')
        cmp=await pg.evaluate("""()=>[...document.querySelectorAll('.location')].map(l=>{const t=(l.querySelector('.required-ah')||{}).textContent||''; return {ps:l.querySelector('.ps-name').value, sheet:parseFloat(t), aux:l.querySelector('.aux-circuits').value}})""")
        json.dump(cmp,open(_od('plbuild')+'sheet_ah.json','w'))
        over=[c for c in cmp if c['sheet']>65]
        ok('no created sheet requires >65 Ah', not over, json.dumps(over[:5]))
        await pg.evaluate("[...document.querySelectorAll('.location')].find(l=>l.querySelector('.ps-location').value==='Area A').scrollIntoView()")
        await pg.wait_for_timeout(200); await pg.screenshot(path=SH+'07-resulting-sheet-BWDG.png')
        links=await pg.evaluate('PL_LINKS.map(l=>({n:l.name,sha:l.sha256.length,d:Object.keys(l.devices).length}))'); ok('5 linked files with SHA-256', len(links)==5 and all(l['sha']==64 for l in links), json.dumps(links))
        # save/restore round trip of links
        st=await pg.evaluate('JSON.stringify(buildStateObject())')
        await pg.evaluate('s=>applyLoadedState(JSON.parse(s))', st); await pg.wait_for_timeout(500)
        ok('links + row mapping survive save/load', await pg.evaluate("PL_LINKS.length===5 && document.querySelectorAll('[data-pl-key]').length>0 && !!document.querySelector('.location[data-pl-sheet-id]')"))
        # link change: modify BWDG: fan 14->10 on MASD 1-1, remove one detector? add new detector
        src=open(T+'BWDG1.pl').read()
        mod=src.replace('<aspiratorSpeed>14</aspiratorSpeed>','<aspiratorSpeed>10</aspiratorSpeed>',1)
        T2=_od('plbuild','t2'); open(T2+'BWDG1.pl','w').write(mod)
        # manual edit a zone name for a different row to test protection
        await pg.click('#menu-file-btn'); await pg.click('#linked-pl-btn'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=SH+'08-linked-files.png')
        lid=await pg.evaluate("PL_LINKS.find(l=>l.name==='BWDG1.pl').id")
        await pg.evaluate("id=>{window.__lid=id}",lid)
        async with pg.expect_file_chooser() as fc:
            await pg.click(f'[data-check="{lid}"]')
        ch=await fc.value; await ch.set_files(T2+'BWDG1.pl'); await pg.wait_for_timeout(600)
        await pg.screenshot(path=SH+'09-link-change-diff.png')
        ban=await pg.evaluate("!document.getElementById('pl-link-banner').hidden"); ok('change banner shown', ban)
        await pg.click('#pld-cancel'); await pg.evaluate('window.scrollTo(0,0)'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=SH+'10-link-change-banner.png', clip={'x':0,'y':0,'width':1500,'height':560})
        await pg.click('[data-review]'); await pg.wait_for_timeout(200)
        await pg.click('#pld-apply'); await pg.wait_for_timeout(400)
        fan=await pg.evaluate(f"plRowsForKey('{lid}|Area A#id0')[0].querySelector('.fanspeed-select').value"); ok('re-import updated fan 14->10', fan=='10', fan)
        ok('banner cleared after apply', await pg.evaluate("document.getElementById('pl-link-banner').hidden"))
        # Import Calc round-trip of the imported document (Replace)
        html=await pg.evaluate("()=>{updateEmbeddedStateTag(buildStateObject()); return '<!DOCTYPE html>\\n'+document.documentElement.outerHTML}")
        open(_od('plbuild')+'saved.html','w').write(html)
        nsh=await pg.evaluate("document.querySelectorAll('.location').length")
        await pg.click('#menu-edit-btn'); await pg.click('#clear-calc-btn'); await pg.click('#prompt-actions >> text=Entire file'); await pg.click('#prompt-actions >> text=Clear headers too'); await pg.click('#prompt-actions >> text=Clear entire file')
        await pg.wait_for_timeout(300)
        ok('Clear entire file also clears links', await pg.evaluate('PL_LINKS.length')==0)
        await pg.set_input_files('#import-calc-file',_od('plbuild')+'saved.html'); await pg.wait_for_timeout(400)
        btxt=await pg.evaluate("[...document.querySelectorAll('#prompt-actions button')].map(b=>b.textContent)")
        rb=[t for t in btxt if 'Replace' in t]
        if rb: await pg.click(f'#prompt-actions >> text={rb[0]}')
        await pg.wait_for_timeout(300); await pg.click('#prompt-actions .btn-primary')
        await pg.wait_for_timeout(3000)
        ok('Import Calc (Replace) restores sheets + links', await pg.evaluate("document.querySelectorAll('.location').length")==nsh and await pg.evaluate('PL_LINKS.length')==5, str(btxt))
        ok('no page errors total', not errs, ';'.join(errs[:3]))
        await b.close()
    print(json.dumps([r for r in res if not r[1]]))
asyncio.run(main())
# ---- 02.00.000: layout, Print/Export (PDF/DOCX/HTML/Excel x Summary/Standard/Full), Help audit, screenshots ----
import test_v2
r2=asyncio.run(test_v2.main())
allres=res+r2
print('TOTAL', sum(1 for r in allres if r[1]), '/', len(allres), 'passed;', 'FAILED:', [r[0] for r in allres if not r[1]])
