import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':int(sys.argv[2]) if len(sys.argv)>2 else 1500,'height':1000})
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('file:///workspace/ModuLaser-Battery-Calculator/modulaser_battery_calculator.html'); await pg.wait_for_timeout(600)
        if len(sys.argv)>3: await pg.evaluate(sys.argv[3]); await pg.wait_for_timeout(400)
        await pg.screenshot(path=sys.argv[1], full_page='full' in sys.argv[1]); print(errs)
        await b.close()
asyncio.run(main())
