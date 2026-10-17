import re, subprocess, shutil
R='/workspace/ModuLaser-Battery-Calculator/'
S='/workspace/v2build/src/'
h=subprocess.run(['git','-C',R,'show','7a54438:modulaser_battery_calculator.html'],capture_output=True,text=True,check=True).stdout
def rep(old,new,count=1):
    global h
    assert old in h, 'MISSING: '+old[:90]
    h=h.replace(old,new,count)
def resub(pat,new,flags=re.S):
    global h
    r=new if callable(new) else (lambda mm,new=new: new)
    h2,n=re.subn(pat,r,h,count=1,flags=flags); assert n==1,'RE MISSING '+pat[:80]; h=h2

# --- no CDN ---
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>\n','')
# --- CSS ---
rep('</style>\n', open(S+'v2.css').read()+'</style>\n')

# --- topbar: menu strip + quick row ---
m=re.search(r'  <div class="topbar">.*?\n  </div>\n\n  <div class="project-info-bar">',h,re.S)
top=m.group(0)
nav=re.search(r'      <nav class="menubar".*?</nav>\n',top,re.S).group(0)
nav=nav.replace('<button role="menuitem" id="print-menu-btn">Print…<span class="mi-kbd">Ctrl+P</span></button>',
 '<button role="menuitem" id="print-menu-btn" title="Preview and export the printout as PDF, Word (.docx), HTML or Excel">Print / Export…<span class="mi-kbd">Ctrl+P</span></button>')
nav=nav.replace('<button role="menuitem" id="export-xlsx-btn">Export to Excel</button>','<button role="menuitem" id="export-xlsx-btn" title="Excel workbook: CAD Schedule + Detail sheets">Export to Excel</button>')
nav=nav.replace('<button role="menuitem" id="add-location-menu-btn">+ Add Location</button>','<button role="menuitem" id="add-location-menu-btn" title="Add another power supply sheet">+ Add Location</button>')
nav=nav.replace('<button role="menuitem" id="cluster-report-btn">Cluster Report</button>',
 '<button role="menuitem" id="cluster-report-btn">Cluster Report</button>\n            <hr>\n            <button role="menuitem" id="view-settings-btn" title="Expand or collapse the Project Settings bar">Project Settings bar</button>\n            <button role="menuitem" id="view-sidebar-btn" title="Show or hide the power supply sheet list">Sheet sidebar</button>\n            <button role="menuitem" id="view-results-btn" title="Show or hide the live results panel">Results panel</button>')
rev=re.search(r'    <div class="revision-cells">.*?\n    </div>\n',top,re.S).group(0)
newtop=f'''  <div class="topbar v2-top">
    <div class="v2-menustrip">
      <div class="brand brand-mini"><div class="brand-mark">ML</div><div class="brand-text"><h1>ModuLaser Battery Calculator</h1></div></div>
{nav}{rev}    </div>
    <div class="quick-row">
      <input type="file" id="import-calc-file" accept=".html,.htm,text/html" hidden>
      <button class="btn qr-icon" id="sb-toggle-btn" title="Show or hide the sheet sidebar" aria-label="Sheet sidebar">☰</button>
      <button class="btn btn-primary" id="import-pl-btn" title="Import one or more PipeCAD .pl files">Import .pl</button>
      <button class="btn" id="add-location-btn" title="Add another power supply sheet">+ Add Location</button>
      <span class="qr-sep"></span>
      <button class="btn" id="save-as-copy-btn" title="Download this calculator as a self-contained .html file">Save As…</button>
      <button class="btn" id="print-btn" title="Print / Export: PDF, Word, HTML or Excel with a live preview">Print</button>
      <span id="save-indicator" class="save-indicator">Auto-Save off</span>
      <button class="btn qr-icon" id="rp-toggle-btn" title="Show or hide the results panel" aria-label="Results panel">◧</button>
    </div>
  </div>

  <section class="ps-bar" id="proj-settings">
    <div class="ps-bar-head"><button type="button" class="ps-toggle" id="proj-settings-toggle" aria-expanded="true" aria-controls="proj-settings-body"><span class="chev">▾</span> Project Settings</button><span id="proj-settings-summary"></span></div>
    <div class="ps-bar-body" id="proj-settings-body">
  <div class="project-info-bar">'''
rep(top,newtop)
# close settings bar after project-info-bar
rep('''  </div>

  <div class="report-overlay" id="report-overlay">''','''  </div>
    <div id="proj-basis-line"></div>
    </div>
  </section>

  <div class="report-overlay" id="report-overlay">''')
# --- shell around main ---
rep('''  <main>
    <p class="intro">''','''  <div id="app-shell">
  <aside id="sheet-sidebar" aria-label="Power supply sheets">
    <div class="sb-top"><span>Power supplies</span><span id="sb-count"></span></div>
    <div id="sb-list"></div>
    <div class="sb-foot">
      <button type="button" id="sb-add-btn" title="Add another power supply sheet">+ Add power supply</button>
      <div class="sb-legend"><span><i class="dot st-complete"></i>Complete</span><span><i class="dot st-needs"></i>Needs entry</span><span><i class="dot st-error"></i>Error</span><span><i class="dot st-overridden"></i>Overridden</span></div>
    </div>
  </aside>
  <main id="v2-center">
    <p class="intro">''')
rep('''    <div id="locations-container"></div>
  </main>
''','''    <div id="locations-container"></div>
  </main>
  <aside id="results-panel" aria-label="Live results">
    <div class="rp-head"><span>Live results</span><button type="button" id="rp-close-btn" title="Hide the results panel">✕</button></div>
    <div id="rp-body"></div>
  </aside>
  </div>

  <div class="v2-overlay" id="pe-overlay" role="dialog" aria-modal="true" aria-labelledby="pe-title">
    <div class="pe-card">
      <div class="pe-head"><h2 id="pe-title">Print / Export</h2><button class="help-close" id="pe-close" title="Close">✕</button></div>
      <div class="pe-body">
        <div class="pe-side">
          <div><h3>Sheets</h3><select id="pe-scope"><option value="all">All power supply sheets</option><option value="current">Current sheet only</option></select></div>
          <div><h3>Detail level</h3>
            <label><input type="radio" name="pe-level" value="summary" id="pe-level-summary"><span>Summary<small>Results only: one page per power supply.</small></span></label>
            <label><input type="radio" name="pe-level" value="standard" id="pe-level-standard" checked><span>Standard<small>Adds the formulas with your values filled in.</small></span></label>
            <label><input type="radio" name="pe-level" value="full" id="pe-level-full"><span>Full<small>Every step, per-module currents, de-rating and BOM on appendix pages after each sheet.</small></span></label>
          </div>
          <div><h3>Include</h3>
            <label><input type="checkbox" id="pe-summary" checked><span>Project summary page</span></label>
            <label><input type="checkbox" id="pe-bom" checked><span>Bill of Materials</span></label>
          </div>
          <div><h3>Save as</h3>
            <div class="pe-btns">
              <button class="btn btn-primary" id="pe-pdf" title="Print to PDF (Letter)">PDF</button>
              <button class="btn" id="pe-docx" title="Word document, built offline">Word (.docx)</button>
              <button class="btn" id="pe-html" title="Self-contained .html report">HTML</button>
              <button class="btn" id="pe-xlsx" title="Excel: CAD Schedule + Detail">Excel (.xlsx)</button>
            </div>
          </div>
          <div id="pe-pages"></div><div id="pe-status" role="status"></div>
          <p style="font-size:11px;color:var(--muted);margin:0">Each power supply prints on one 8.5 × 11 in page. Excel's CAD Schedule sheet pastes cleanly into AutoCAD; its Detail sheet follows the detail level with expandable row groups.</p>
        </div>
        <iframe id="pe-preview" title="Print preview"></iframe>
      </div>
    </div>
  </div>
''')
rep('<p class="intro">Enter each','<p class="intro">Enter each')
# Excel wiring
rep('document.getElementById("export-xlsx-btn").addEventListener("click", exportToExcel);','document.getElementById("export-xlsx-btn").addEventListener("click", () => v2ExportXlsx());')
rep("  on('print-menu-btn', () => window.print());\n","")
# --- version ---
rep('const APP_MAJOR = "01";','const APP_MAJOR = "02";'); rep('const APP_MINOR = "06";','const APP_MINOR = "00";')
newrev=open(S+'amend.txt').read().strip()
resub(r'  \{ rev: "000", minor: "06", date: "261013", desc: ".*?" \},\n', newrev+'\n')
rep('const revShort = `${APP_MAJOR}.${latest.minor || APP_MINOR}.${latest.rev}`;','const revShort = `${latest.major || APP_MAJOR}.${latest.minor || APP_MINOR}.${latest.rev}`;')
rep('`<tr><td class="mono-inline">${APP_MAJOR}.${a.minor || "00"}.${a.rev}</td>','`<tr><td class="mono-inline">${a.major || "01"}.${a.minor || "00"}.${a.rev}</td>')
rep('return `${APP_MAJOR}.${latest.minor || APP_MINOR}.${latest.rev}_${latest.date}`;','return `${latest.major || APP_MAJOR}.${latest.minor || APP_MINOR}.${latest.rev}_${latest.date}`;')
# --- help ---
exec(open('/workspace/v2build/help_edit.py').read())
# --- JS ---
js=''.join(open(S+f).read() for f in ['v2-model.js','v2-shell.js','v2-print.js','v2-office.js'])
rep('\nrenderRevisionInfo();\nsyncPrintHeaders();\nupdateSaveIndicator();\n</script>', '\n'+js+'\nrenderRevisionInfo();\nsyncPrintHeaders();\nupdateSaveIndicator();\nwireV2Shell();\nwirePrintDialog();\n</script>')
for t in ['modulaser_battery_calculator.html','app/modulaser_battery_calculator.html','docs/index.html','pwa/index.html','modulaser_calculator_electron/electron-app/app/modulaser_battery_calculator.html']:
    open(R+t,'w').write(h)
print('written',len(h))
