# Load Brent's saved calculator (qa/brent-needs-entry.html) into the app under test via File > Import Calc (Replace),
# so the app's own current code runs on his data (no patching of his saved HTML).
import os, tempfile, asyncio
BRENT='/workspace/qa/brent-needs-entry.html'
SHOT_DIR=os.environ.get('SHOT_DIR') or (os.path.join(os.environ['MLP_TEST_OUT'],'shots') if os.environ.get('MLP_TEST_OUT') else tempfile.mkdtemp(prefix='calc-shots-')); os.makedirs(SHOT_DIR, exist_ok=True)
async def load_brent(pg, app):
    await pg.goto(app); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(800)
    await pg.set_input_files('#import-calc-file', BRENT); clicked=[]
    for _ in range(6):
        await pg.wait_for_timeout(450)
        bt=await pg.evaluate("[...document.querySelectorAll('#prompt-actions button')].filter(b=>b.offsetParent).map(b=>b.textContent.trim())")
        if not bt: continue
        pick=next((t for t in bt if 'Import anyway' in t),None) or next((t for t in bt if 'Replace' in t),None)
        if pick: await pg.click(f'#prompt-actions >> text={pick}')
        else: pick='primary'; await pg.click('#prompt-actions .btn-primary')
        clicked.append(pick)
    await pg.wait_for_timeout(1500)
    await pg.evaluate("document.querySelectorAll('.open').forEach(e=>{if(/overlay|modal/.test(e.className))e.classList.remove('open')})")
    return clicked
async def sheets(pg):
    return await pg.evaluate("[...document.querySelectorAll('.location')].map(l=>l.dataset.loc)")
async def goto(pg, loc):
    await pg.evaluate("l=>{const it=[...document.querySelectorAll('.sb-item')].find(x=>x.dataset.loc==l); it&&it.click();}", loc)
    await pg.wait_for_timeout(350); await pg.evaluate("()=>{try{refreshAllAmber()}catch(e){} try{v2Refresh()}catch(e){}}"); await pg.wait_for_timeout(250)
