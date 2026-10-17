import asyncio, json, os, subprocess
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
T='/workspace/plbuild/t/'
async def pick_step1(pg, basis='NFPA 72 Voice', temp='77'):
    # 02.00.004: wizard step 1 Design Basis / Ambient Temp start on '- Select -' (required)
    await pg.evaluate("([b,t])=>{for(const [id,v] of [['plw-basis',b],['plw-temp',t]]){const s=document.getElementById(id);if(s&&!s.value){s.value=v;s.dispatchEvent(new Event('change'))}}}", [basis,temp])
async def confirm_settings(pg, value='confirm'):
    if await pg.evaluate("document.getElementById('prompt-overlay').classList.contains('open') && document.getElementById('prompt-title').textContent==='Confirm Settings?'"):
        await pg.click(f'#prompt-actions button[data-value="{value}"]'); await pg.wait_for_timeout(300)
AA_TITLES=('Networked or Standalone?','Auto address?','Address the new sheets?','Address the new modules?')
# 02.00.005 defaults: new build → Networked, no auto address; existing project → Manually address
AUTO_ADDRESS_ANSWER={'Networked or Standalone?':'networked','Auto address?':'no','Address the new sheets?':'manual','Address the new modules?':'manual'}
async def aa_title(pg):
    return await pg.evaluate("document.getElementById('prompt-overlay').classList.contains('open')?document.getElementById('prompt-title').textContent:''")
async def auto_address(pg, answers=None, wait_ms=2500):
    """Answer the 02.00.005 auto-addressing prompt(s) if/when they appear (older builds never show them).
    answers: dict title→button value (defaults AUTO_ADDRESS_ANSWER) or a single value for whatever prompt shows."""
    if not await pg.evaluate("typeof promptAutoAddress==='function'"): return []
    seen=[]; waited=0
    while waited < wait_ms:
        t=await aa_title(pg)
        if t in AA_TITLES:
            v=answers.get(t) if isinstance(answers,dict) else (answers if answers is not None else AUTO_ADDRESS_ANSWER.get(t))
            if v is None: v=AUTO_ADDRESS_ANSWER.get(t)
            await pg.click(f'#prompt-actions button[data-value="{v}"]'); await pg.wait_for_timeout(300); seen.append((t,v)); waited=wait_ms-600; continue
        await pg.wait_for_timeout(100); waited+=100
    return seen
async def import_files(pg, files, project='Demo Project'):
    await pg.click('#import-pl-btn'); await pg.wait_for_timeout(150)
    await pick_step1(pg)
    await pg.click('#plw-next')
    await pg.set_input_files('#plw-file',[T+f for f in files]); await pg.wait_for_timeout(600)
    await pg.click('#plw-next'); await pg.wait_for_timeout(200)
    await pg.click('#plw-suggest-all'); await pg.wait_for_timeout(100)
    await pg.click('#plw-next'); await pg.wait_for_timeout(200)
    for gk in await pg.evaluate("Object.keys(plWiz.unassignedByGroup).filter(k=>plWiz.unassignedByGroup[k].length)"):
        await pg.click(f'[data-pack="{gk}"]'); await pg.wait_for_timeout(50)
    await pg.click('#plw-finish'); await pg.wait_for_timeout(600)
    await confirm_settings(pg)
    if globals().get('AUTO_ADDRESS_ANSWER'): await auto_address(pg)
async def fill_addresses(pg):
    # give every module a unique address and fill header so some sheets PASS
    await pg.evaluate('''()=>{let a=1;document.querySelectorAll('.location').forEach(l=>{l.querySelectorAll('[data-role=module]').forEach(r=>{const s=r.querySelector('.module-address');s.dataset.desiredValue=String(a);s.value=String(a);a++;});});
      updateNetworkAddressAvailability();document.querySelectorAll('.location').forEach(l=>{recalcLocationInner(l.dataset.loc)});
      document.getElementById('project-name-input').value='Sample Tower Expansion';document.getElementById('prepared-by-input').value='B. Wilkins';document.getElementById('network-number-input').value='Network 1';document.getElementById('building-input').value='Bldg 4';refreshAllAmber();}''')
    await pg.wait_for_timeout(400)
async def render_pdf(browser, html, path):
    pg=await browser.new_page(); await pg.set_content(html); await pg.wait_for_function("document.documentElement.getAttribute('data-fit')==='done'")
    over=await pg.evaluate("[...document.querySelectorAll('.page')].map((p,i)=>[i,p.className,p.scrollHeight>p.clientHeight+1]).filter(x=>x[2])")
    npg=await pg.evaluate("document.querySelectorAll('.page').length")
    await pg.pdf(path=path, prefer_css_page_size=True, print_background=True); await pg.close()
    info=subprocess.run(['pdfinfo',path],capture_output=True,text=True).stdout
    pages=int([l for l in info.splitlines() if l.startswith('Pages:')][0].split()[1])
    return pages, npg, over
