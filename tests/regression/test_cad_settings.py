# 02.00.005 (Brent 10-16): Excel CAD Schedule shows each sheet's standby time, alarm time and safety margin with units.
import asyncio, os, sys, base64, zipfile, io, re
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(__file__))
from test_sensenet import BUILD, fresh
APP=os.environ.get('APP','file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html')
import tempfile
OUT=os.environ.get('MLP_TEST_OUT') or tempfile.mkdtemp(prefix='mlp-test-'); os.makedirs(OUT,exist_ok=True)   # QA F3
R=[]
def ok(n,c,i=''): R.append(bool(c)); print('PASS' if c else 'FAIL',n,str(i)[:300])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(); pg.set_default_timeout(8000); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d: asyncio.ensure_future(d.accept()))
    await fresh(pg)
    await pg.evaluate(BUILD,[{'n':2,'addrs':[1,2]},{'n':2,'addrs':[3,4]}])
    # sheet 1: 24 h / 5 min / first margin; sheet 2: 60 h / 15 min / last margin
    exp=await pg.evaluate('''()=>{const ls=[...document.querySelectorAll('.location')];const set=(l,h,a,last)=>{l.querySelector('.standby-hours').value=h;l.querySelector('.alarm-minutes').value=a;const m=l.querySelector('.margin-select');m.selectedIndex=last?m.options.length-1:0;[...l.querySelectorAll('.standby-hours,.alarm-minutes,.margin-select')].forEach(e=>e.dispatchEvent(new Event('change',{bubbles:true})));recalcLocationInner(l.dataset.loc);return m.options[m.selectedIndex].textContent.trim()};
      return [set(ls[0],'24','5',false),set(ls[1],'60','15',true)]}''')
    b64=await pg.evaluate("(async()=>{const b=await v2BuildXlsx({scope:'all',level:'standard'});const a=new Uint8Array(await b.arrayBuffer());let s='';for(const x of a)s+=String.fromCharCode(x);return btoa(s)})()")
    raw=base64.b64decode(b64); open(os.path.join(OUT,'cad-settings.xlsx'),'wb').write(raw)
    z=zipfile.ZipFile(io.BytesIO(raw)); x=z.read('xl/worksheets/sheet1.xml').decode()
    rows=[re.findall(r'<t xml:space="preserve">([^<]*)</t>',r) for r in re.findall(r'<row[^>]*>(.*?)</row>',x)]
    st=[r for r in rows if r and r[0]=='Standby time']
    ok('one settings row per sheet', len(st)==2, st)
    ok('sheet 1 actual values with units', st and st[0]==['Standby time','24 h','Alarm time','5 min','Safety margin',exp[0]], (st[:1],exp))
    ok('sheet 2 actual values with units', len(st)>1 and st[1]==['Standby time','60 h','Alarm time','15 min','Safety margin',exp[1]], (st[1:],exp))
    ok('margin carries a % unit', all('%' in e for e in exp), exp)
    ok('no merged cells / fills added', '<mergeCell' not in x)
    ok('no page errors', not errs, errs)
    await b.close()
  print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
asyncio.run(main())
