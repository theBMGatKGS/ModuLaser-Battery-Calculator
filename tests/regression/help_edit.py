# executed inside inject.py (uses rep / resub / h)
def step(sid, title, body):
    return f'''        <div class="qs-step">
          <div class="qs-step-num">0</div>
          <div class="qs-step-body">
            <div class="qs-step-title" id="{sid}">{title}</div>
            {body}
          </div>
        </div>
'''
layout = step('qs-step-layout','Find your way around the screen','''<p>The screen has six parts, top to bottom and left to right. <b>Menu bar</b> — File, Edit, View and Help hold every command. <b>Quick row</b> — the most-used buttons: ☰ (show/hide the sheet sidebar), <b>Import .pl</b>, <b>+ Add Location</b>, <b>Save As…</b>, <b>Print</b>, the Auto-Save indicator and ◧ (show/hide the results panel). <b>Project Settings</b> bar — the project and network header; click its title to collapse it to a one-line summary. <b>Sheet sidebar</b> (left) — every power supply sheet, grouped by Area/Group, with a status dot. <b>Sheet</b> (center) — the selected power supply's name, location, settings and module table. <b>Live results</b> panel (right) — required Ah, PASS/FAIL, load breakdown, clusters and validation messages for the selected sheet. On a narrow window the sidebar and results panel collapse; open them with ☰ and ◧ or from the View menu.</p>''')
proj = step('qs-step-project-settings','Fill in Project Settings','''<p>Every document represents one <b>ModuLaser SenseNET network</b>. In the <b>Project Settings</b> bar fill in <b>Project Name</b>, <b>Prepared By</b>, <b>Date</b>, <b>Network #</b>, <b>Building</b>, and the <b>Primary</b> (and optional <b>Backup</b>) <b>Command Display Location</b>, and turn <b>Auto-Save</b> on if you want it. These carry into every printed page, the export files and the Cluster Validation Report. Click <b>Project Settings</b> to collapse the bar: it then shows a one-line summary of the project and the sheet settings most sheets use (Design Basis, standby/alarm, temperature, margin).</p>
            <p><b>Overrides:</b> Design Basis, Standby, Alarm, Ambient Temp. and Safety margin are set on each sheet. When a sheet differs from what most sheets use, it shows a blue <span class="mono-inline">Overrides project settings: …</span> badge next to its name, gets a blue dot in the sidebar, and is listed under the bar (click a name to jump to it). An override is allowed — it just makes the difference easy to spot.</p>
            <figure class="qs-figure"><img data-qs-slot="1-project-header" alt="Project Settings bar"><figcaption>Screenshot: Project Settings bar, expanded and collapsed</figcaption></figure>''')
sidebar = step('qs-step-sidebar','Add power supply sheets and use the sidebar','''<p>Each sheet = one power supply. Add one with <b>+ Add power supply</b> at the bottom of the sidebar, <b>+ Add Location</b> in the quick row, or <b>Edit → + Add Location</b>. Click a sheet in the sidebar to show it. Sheets are grouped by their <b>Location</b> (the Area/Group name; an Import .pl fills it from the PipeCAD floor). Each shows its required Ah and a status dot: <b>green</b> complete, <b>amber</b> needs entry (blue-outlined fields left), <b>red</b> error (an INVALID CALCULATION condition or a Validation Error; the red count shows how many), and an extra <b>blue</b> dot when the sheet overrides the project settings. At the top of the sheet fill in the <b>Power Supply Name</b> (e.g. <span class="mono-inline">PS-1</span>) and <b>Location</b> (e.g. <span class="mono-inline">Riser Closet A</span>); use <b>Remove ⌫</b> on the sheet to delete it.</p>
            <figure class="qs-figure"><img data-qs-slot="2-add-location" alt="Sidebar"><figcaption>Screenshot: sheet sidebar with status dots and + Add power supply</figcaption></figure>''')
results = step('qs-step-results','Read the live results panel','''<p>The right-hand panel updates as you type. <b>Required capacity</b> shows the Ah per supply in large type with a gauge: the solid part is the standby + alarm load, the lighter part is the safety margin and temperature de-rating, the blue mark is the selected battery and the dashed red mark is the 65 Ah maximum. Below it a status line reads <b>PASS</b> (valid, no flags, within the selected battery and 65 Ah), <b>FAIL</b> (an INVALID CALCULATION condition, more than one supply needed, or capacity beyond the battery / 65 Ah) or <b>INCOMPLETE</b> (Validation Error flags still open). Then the selected battery and recommended hardware, the load breakdown (modules, power supply quiescent + AUX, total, standby/alarm/required Ah), the clusters on this supply, and the sheet's own validation messages — red for INVALID CALCULATION, yellow for Validation Errors, blue for fields that still need entry. The full calculation, hardware and Bill of Materials stay on the sheet below the module table.</p>''')
printx = step('qs-step-print-export','Print or export (PDF, Word, HTML, Excel)','''<p><b>File → Print / Export…</b>, <b>Print</b> in the quick row, or <b>Ctrl+P</b> opens the Print / Export dialog with a live 8.5 × 11 in preview. Under <b>Sheets</b> choose <b>All power supply sheets</b> or <b>Current sheet only</b>; pick a <b>Detail level</b>; under <b>Include</b> tick <b>Project summary page</b> and <b>Bill of Materials</b> (the same setting as File → Print BOM); then under <b>Save as</b> click a format:</p>
            <ul class="help-steps" style="margin:0 0 10px;">
              <li><b>PDF</b> — opens the print window; choose “Save as PDF”, Letter. In the Windows app the PDF is written directly and you pick where to save it.</li>
              <li><b>Word (.docx)</b> — built in the app, offline, with the same pages, tables and graphics.</li>
              <li><b>HTML</b> — one self-contained .html report you can email or open in any browser; Full detail uses expandable sections.</li>
              <li><b>Excel (.xlsx)</b> — the CAD Schedule and Detail sheets (see the next step). File → Export to Excel saves the same workbook directly.</li>
            </ul>
            <p>Page 1 is the <b>project summary</b>: project header and one row per power supply with Area/Group, required Ah, battery and PASS/FAIL. Then each power supply gets <b>one letter page</b>: header (project, PSU tag, location/Area-Group, calculator revision), the <b>capacity gauge</b>, a <b>PASS/FAIL stamp</b>, a <b>mini cluster diagram</b> (the supply with its displays ■ and detectors ○ labelled with fan speed), the module table (Zone, Type, Fan speed, Address, Standby mA, Alarm mA, with totals and Required Ah | Battery | status), the settings used, any validation messages, the BOM (if included) and the code-compliance statement when the sheet is clean.</p>''')
levels = step('qs-step-detail-levels','Choose a detail level','''<p>The <b>Detail level</b> in the Print / Export dialog controls how much of the calculation goes into PDF, Word, HTML and the Excel Detail sheet (the preview updates live):</p>
            <ul class="help-steps" style="margin:0 0 10px;">
              <li><b>Summary</b> — results only: the one-page sheet per power supply.</li>
              <li><b>Standard</b> — adds the formulas with your values filled in (standby, alarm, margin, temperature, battery and supplies). If a sheet would overflow its page, the formulas move to an appendix page right after it.</li>
              <li><b>Full</b> — adds appendix pages after each sheet with every step: per-module currents, subtotals, quiescent and AUX load, standby/alarm Ah, the BS 5839-1 de-rating factor D where it applies, safety margin, temperature multiplier, battery selection, supplies required and the BOM. Each step shows the formula, the formula with values substituted, the result with units, and its reference — the Design Basis citation the sheet uses (e.g. NFPA 72 (2022 Edition), Section 10.6.7.2 or BS 5839-1:2025, Annex E), or the calculator's own data table where that is the source.</li>
            </ul>
            <p>Every number is read from the sheet's own calculation, so exports always match the screen. The on-sheet <b>Show granular calculation detail</b> checkbox still shows the same breakdown on screen.</p>''')
cad = step('qs-step-cad-paste','Paste the CAD Schedule onto a drawing','''<p>The Excel workbook's <b>CAD Schedule</b> sheet has one compact table per power supply — Zone, Type, Fan speed, Address, Standby mA, Alarm mA, then Total load and a footer row Required Ah | Battery | PASS/FAIL — with thin plain borders, fixed column widths, no merged cells and no fills. To place one on a drawing: select that table's cells in Excel, copy, then in AutoCAD use <b>Paste Special → AutoCAD Entities</b> (a native table) or <b>Picture (Metafile)</b>. The <b>Detail</b> sheet holds the full calculation at the chosen detail level, grouped per power supply and per step — use Excel's outline buttons (1 / 2 / 3 or + / −) on the left to expand or collapse it.</p>''')

# replace steps 1 and 2 with layout/project/sidebar
resub(r'        <div class="qs-step">\n          <div class="qs-step-num">1</div>.*?(?=        <div class="qs-step">\n          <div class="qs-step-num">3</div>)', layout+proj+sidebar)
# step 11 multi-supply text: toolbar
rep('the <b>Cluster Report</b> button in the toolbar ties everything back together.','<b>View → Cluster Report</b> ties everything back together. Each exported arrangement becomes its own sheet in the sidebar.')
# step 12 save/export
rep('<b>Export to Excel</b> in the toolbar produces a multi-sheet .xlsx workbook, one worksheet per power supply, mirroring each sheet\'s module table and results — useful for handing data to someone who wants it outside this tool.',
    '<b>File → Export to Excel</b> saves an .xlsx workbook with a <b>CAD Schedule</b> sheet and a <b>Detail</b> sheet (see Print or export, below) — useful for drawings and for anyone who wants the data outside this tool. <b>Print / Export…</b> offers PDF, Word and HTML as well.')
rep('The <b>Autosave</b> toggle (next to it)','The <b>Auto-Save</b> toggle (in the Project Settings bar; its state shows at the right of the quick row)')
rep('Screenshot: Confirm defaults toolbar button clearing blue','Screenshot: Edit → Confirm defaults clearing blue')
rep('(The separate "Clear saved data" control in the project bar is only for wiping browser Autosave storage — different from toolbar Clear.)','(The separate <b>Edit → Clear saved data</b> only wipes browser Auto-Save storage — different from Clear….)')
# menubar step
resub(r'<p>The top of the calculator has a menu bar plus a short row of the most-used buttons\..*?Esc to close\.</p>',
 '<p>The menu bar at the top holds every command. <b>File</b>: New…, Open / Import Calc…, Import .pl…, Linked .pl files…, Save As…, Export to Excel, Print / Export… (Ctrl+P) and the <b>Print BOM</b> switch. <b>Edit</b>: + Add Location, Clear…, Confirm defaults, Clear saved data. <b>View</b>: Cluster Report, Project Settings bar, Sheet sidebar, Results panel. <b>Help</b>: Help, How Do I…, Revision log. The quick row underneath holds ☰ (sheet sidebar), <b>Import .pl</b>, <b>+ Add Location</b>, <b>Save As…</b>, <b>Print</b>, the Auto-Save indicator and ◧ (results panel). Menus work from the keyboard too: Tab to a menu name, press Enter or ↓ to open it, ↑/↓ to move, ←/→ to switch menus, Esc to close.</p>')
rep('<div class="qs-step-title" id="qs-step-menubar">Find commands in the menu bar</div>','<div class="qs-step-title" id="qs-step-menubar">Find commands in the menu bar and quick row</div>')
# step 18 wizard: mention restyled step 4 / sidebar
rep('One sheet is created per supply, with type, zone name, fan speed and display model filled in; addresses and anything the file doesn\'t provide stay highlighted for you to enter.</p>',
    'One sheet is created per supply, with type, zone name, fan speed and display model filled in, its Location set to the Area/Group (so the sidebar groups them), and addresses and anything the file doesn\'t provide highlighted for you to enter — the sidebar shows those sheets with an amber <i>needs entry</i> dot until you finish.</p>')
# insert results after step "validation"/invalid (before multi-supply) and print/levels/cad at end (after linked pl)
rep('''        <div class="qs-step">
          <div class="qs-step-num">11</div>''', results + '''        <div class="qs-step">
          <div class="qs-step-num">11</div>''')
resub(r'(<div class="qs-step-title" id="qs-step-linked-pl">.*?</p>\n          </div>\n        </div>\n)', lambda mm: mm.group(1)+printx+levels+cad)
# renumber steps
import itertools
cnt=itertools.count(1)
h=re.sub(r'<div class="qs-step-num">\d+</div>', lambda mm: f'<div class="qs-step-num">{next(cnt)}</div>', h)
# fix cross reference "Steps 9–10 below"
n_val = None
rep('Steps 9–10 below cover the yellow Validation Error flags and the red INVALID CALCULATION banner','The <b>Review Validation Error flags</b> and <b>Resolve any INVALID CALCULATION banner</b> steps below cover the yellow Validation Error flags and the red INVALID CALCULATION banner')
rep('(Step 4) keeps working normally','(see Build each cluster) keeps working normally')
rep('Address stays the 1–127 dropdown from Step 5,','Address stays the 1–127 dropdown from the Address step,')
# FAQ updates
rep('<p class="a">It\'s a single document-wide switch (not per-sheet) that leaves the Bill of Materials out of the printed/PDF output entirely when unchecked — every sheet\'s BOM, and its identifying header, are skipped. It only affects print; the on-screen Bill of Materials, Excel export, and Cluster Validation Report are unaffected.',
    '<p class="a">It\'s a single document-wide switch (not per-sheet) that leaves the Bill of Materials out of the PDF, Word and HTML output when unchecked. It is the same setting as the <b>Bill of Materials</b> box in the Print / Export dialog — changing one changes the other. The on-screen Bill of Materials, the Excel workbook and the Cluster Validation Report are unaffected.')
rep('When it\'s on, that sheet prints an additional page (after the calculation sheet and Bill of Materials) containing the same breakdown — it never affects whether the calculation sheet itself fits on one page, since the detail page is entirely separate. Off by default; saved per sheet with the rest of the document.',
    'Off by default; saved per sheet with the rest of the document. For printouts and exports use the <b>Detail level</b> in File → Print / Export… instead: <b>Standard</b> adds the formulas with values, <b>Full</b> adds appendix pages after each sheet with every step (formula, values substituted, result, reference) — available in PDF, Word, HTML and the Excel Detail sheet whether or not this checkbox is on.')
newfaq = '''        <div class="help-faq-item">
          <div class="q">What do the sidebar's status dots mean?</div>
          <p class="a">Green: complete — no validation messages and no fields left to enter. Amber: needs entry — blue-outlined fields are still empty or on unconfirmed factory defaults. Red: error — the sheet has an INVALID CALCULATION condition or a Validation Error (the red number is how many). A second, blue dot means the sheet overrides the settings most sheets use (Design Basis, standby, alarm, temperature or margin). The same legend is at the bottom of the sidebar.</p>
        </div>
        <div class="help-faq-item">
          <div class="q">How is PASS / FAIL / INCOMPLETE decided?</div>
          <p class="a">It only reads the sheet's own results. <b>PASS</b>: no INVALID CALCULATION condition, no Validation Error, one supply is enough and the required Ah per supply is within the selected battery and the 65 Ah maximum. <b>FAIL</b>: an INVALID CALCULATION condition, more than one supply required, or capacity beyond the selected battery or 65 Ah. <b>INCOMPLETE</b>: Validation Error flags are still open, so the recommendation and BOM are withheld. The status appears in the results panel, the summary page, each PSU page stamp and the CAD Schedule footer.</p>
        </div>
        <div class="help-faq-item">
          <div class="q">Why are Standby mA and Alarm mA the same in the module table?</div>
          <p class="a">This calculator uses one current per module (from the ModuLaser 24 V current-draw reference) for both standby and alarm — the same total load drives the Standby Ah and Alarm Ah lines. Both columns are shown because CAD schedules usually list both.</p>
        </div>
        <div class="help-faq-item">
          <div class="q">Do the exports need an internet connection?</div>
          <p class="a">No. PDF, Word (.docx), HTML and Excel (.xlsx) are all built inside the calculator file itself — nothing is downloaded from the internet, in the browser or in the Windows app.</p>
        </div>
        <div class="help-faq-item">
          <div class="q">Where did the toolbar go?</div>
          <p class="a">Every command is in the menu bar (File, Edit, View, Help); the most-used ones are also in the quick row under it. Print is now <b>Print / Export…</b>, with PDF, Word, HTML and Excel in one dialog.</p>
        </div>
'''
rep('''      <div class="help-section" id="help-faq">
        <h3>FAQs</h3>
''','''      <div class="help-section" id="help-faq">
        <h3>FAQs</h3>
'''+newfaq)
rep('<p class="help-sub">How to use the calculator · standards and formulas · FAQs · revision log</p>','<p class="help-sub">Screen layout · Import .pl · Print / Export · standards and formulas · FAQs · revision log (calculator 02.00)</p>')
rep('placeholder="Type to filter topics (Import, Clear, battery sizing…)"','placeholder="Type to filter topics (Import .pl, Print, detail level, CAD, sidebar…)"')
rep('''<p class="intro">Enter each display/detector module''','''<p class="intro">Enter each display/detector module''')
# How Do I entries
resub(r"  \{\n    id: 'menubar',.*?common: true,\n  \},\n", """  {
    id: 'menubar',
    title: 'Find a command (menu bar and quick row)',
    keywords: 'menu bar toolbar file edit view help where button moved quick row',
    blurb: 'Menu bar: File (New, Open / Import Calc, Import .pl, Linked .pl files, Save As, Export to Excel, Print / Export…, Print BOM), Edit (+ Add Location, Clear, Confirm defaults, Clear saved data), View (Cluster Report, Project Settings bar, Sheet sidebar, Results panel), Help (Help, How Do I…, Revision log). Quick row: ☰ sidebar, Import .pl, + Add Location, Save As…, Print, Auto-Save indicator, ◧ results panel.',
    target: 'qs-step-menubar',
    common: true,
  },
  {
    id: 'layout',
    title: 'Find my way around the new screen',
    keywords: 'layout screen sidebar results panel project settings 02.00 new design',
    blurb: 'Top: menu bar and quick row. Then the collapsible Project Settings bar. Left: the sheet sidebar grouped by Area/Group with status dots. Center: the selected sheet. Right: live results. ☰ and ◧ (or View) show or hide the side panels.',
    target: 'qs-step-layout',
    common: true,
  },
  {
    id: 'sidebar',
    title: 'Switch sheets / read the status dots',
    keywords: 'sidebar sheet list status dot green amber red blue add power supply area group',
    blurb: 'Click a sheet in the left sidebar to show it. Green = complete, amber = needs entry, red = error (count shown), blue = overrides the project settings. + Add power supply adds a sheet.',
    target: 'qs-step-sidebar',
    common: true,
  },
  {
    id: 'project-settings',
    title: 'Project Settings and per-sheet overrides',
    keywords: 'project settings bar collapse summary override badge design basis standby alarm',
    blurb: 'Click Project Settings to collapse or expand the header bar. Sheets whose Design Basis, standby, alarm, temperature or margin differ from what most sheets use show an override badge and a blue sidebar dot.',
    target: 'qs-step-project-settings',
    common: true,
  },
  {
    id: 'results-panel',
    title: 'Read the results panel (PASS / FAIL)',
    keywords: 'results panel pass fail incomplete gauge required ah battery 65 load breakdown',
    blurb: 'The right panel shows required Ah with a gauge (load, shaded margin & de-rating, battery mark, 65 Ah limit), PASS / FAIL / INCOMPLETE, battery and hardware, load breakdown, clusters and the sheet\\u2019s validation messages.',
    target: 'qs-step-results',
    common: true,
  },
  {
    id: 'print-export',
    title: 'Print or export to PDF, Word, HTML or Excel',
    keywords: 'print export pdf word docx html excel preview letter page dialog ctrl+p',
    blurb: 'File → Print / Export…, Print in the quick row, or Ctrl+P. Pick sheets, detail level, summary page and BOM, check the live preview, then click PDF, Word (.docx), HTML or Excel (.xlsx). Each power supply fits one letter page.',
    target: 'qs-step-print-export',
    common: true,
  },
  {
    id: 'detail-levels',
    title: 'Choose a detail level (Summary / Standard / Full)',
    keywords: 'detail level summary standard full formulas appendix math granular calculation',
    blurb: 'Summary = results only. Standard = formulas with values. Full = appendix pages after each sheet with every step (formula, values, result, reference), per-module currents, de-rating and BOM. The Excel Detail sheet follows the same level with expandable groups.',
    target: 'qs-step-detail-levels',
    common: true,
  },
  {
    id: 'cad-paste',
    title: 'Paste the schedule onto an AutoCAD drawing',
    keywords: 'cad autocad schedule paste excel table drawing',
    blurb: 'Export to Excel, open the CAD Schedule sheet, copy one power supply\\u2019s table and use Paste Special in AutoCAD (AutoCAD Entities for a table). No merged cells or fills, thin borders, fixed widths.',
    target: 'qs-step-cad-paste',
    common: true,
  },
""")
resub(r"  \{\n    id: 'export-excel',.*?common: true,\n  \},\n", """  {
    id: 'export-excel',
    title: 'Export to Excel',
    keywords: 'export excel xlsx spreadsheet workbook cad schedule detail',
    blurb: 'File → Export to Excel (or Excel in Print / Export) saves a workbook with a CAD Schedule sheet (one compact table per power supply) and a Detail sheet that follows the detail level, with expandable row groups.',
    target: 'qs-step-cad-paste',
    common: true,
  },
""")
rep("blurb: 'Save As… downloads","blurb: 'Save As… (quick row or File) downloads")
rep("blurb: 'Autosave stores work","blurb: 'Turn Auto-Save on in the Project Settings bar. It stores work")
