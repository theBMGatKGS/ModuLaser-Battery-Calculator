/* ModuLaser project file — shared module (modulaser-project.js)
   Used by the ModuLaser Battery Calculator and the ModuLaser MASD Field Report.
   Keep the two repos' copies identical (MLP.VERSION below). No dependencies, no network.

   File: *.mlproj.json  { format:'modulaser-project', schemaVersion:1, ... }
   Ownership: the Battery Calculator / MASD Engineering Toolbox own `design` (incl. design.devices[].config);
   the Field Report owns `site`; `changes` (field-change log) and `approvals` are shared: the Report logs,
   the Toolbox verifies, QA signs off.
   Each app keeps the other app's section as-is and never overwrites it without a diff prompt. */
(function (root) {
'use strict';
const MLP = {};
MLP.VERSION = '1.6.0';   // 1.6.0: brand catalog (Edwards | Kidde Commercial), ASD-160 kind (MICRA25), hash defaults. 1.5.1: MiniLaser pipe limits (M p.66)
MLP.FORMAT = 'modulaser-project';
MLP.SCHEMA_VERSION = 1;
MLP.EXT = '.mlproj.json';
MLP.NAME_MAX = 16;                 // ModuLaser display shows 16 characters, spaces included
MLP.M_TO_FT = 3.28084;
MLP.DETECTOR_TYPES = { MULTISENSE: 'Detector', MODULASER_DETECTOR: 'Detector', MICRA25: 'ASD-160' };
MLP.DISPLAY_PARTS = { '0': 'Standard Display', '1': 'Minimum Display', '2': 'Command Display' };
MLP.DISPLAY_MODELS = { 'Standard Display': 'FHSD8310', 'Minimum Display': 'FHSD8300', 'Command Display': 'FHSD8320' };
MLP.TT_TO_CLASS = { 60: 'VEWFD', 90: 'EWFD', 120: 'SFD' };

/* Typical starting values by performance class, used ONLY as editable prefills marked
   "typical — confirm on site". They are not design values; the commissioning engineer confirms them. */
MLP.TYPICAL_DEFAULTS = {
  // Manual-sourced (ModuLaser Install Manual 04-4001-501-0803-05): flow High/Low limit 20% and flow-fault delay 120 s (Table 29, p.76).
  // Fire 1 per class = the FM/UL HOLE-sensitivity limit (App. A, printed p.113) used as a starting point; the manual gives no %obs/ft
  // alarm default (thresholds come from ClassiFire; Table 24 p.71 factors: Alert 10, Prealarm 6, Alarm 8, Alarm 2 absolute 20).
  // VEWFD Alert 0.2 = per NFPA 76-2024 8.5.3.1.2.5 (VEWFD Alert 0.2 / Alarm 1.0 %/ft = 0.65 / 3.2 %/m, effective at each port, above ambient). Everything else
  // (EWFD 0.5 / SFD 1.0 Alert — site/design choice, no code basis; Prealarm, Fire 2, the 5 s delays — site choice, Table 26 range 0–90 s) is 'typical – unverified'.
  VEWFD: { alert: 0.2, action: 0.5, fire1: 1.0, fire2: 2.0, actionDly: 5, fire1Dly: 5, flowLow: 20, flowHigh: 20, flowDly: 120 },
  EWFD:  { alert: 0.5, action: 1.0, fire1: 1.5, fire2: 3.0, actionDly: 5, fire1Dly: 5, flowLow: 20, flowHigh: 20, flowDly: 120 },
  SFD:   { alert: 1.0, action: 1.5, fire1: 2.5, fire2: 5.0, actionDly: 5, fire1Dly: 5, flowLow: 20, flowHigh: 20, flowDly: 120 }
};

/* ---------------- small helpers ---------------- */
function kid(el, tag){ if (!el) return null; for (const c of el.children) if (c.localName === tag || c.tagName === tag) return c; return null; }
function kids(el, tag){ return el ? Array.from(el.children).filter(c => c.localName === tag || c.tagName === tag) : []; }
function txt(el, tag){ const k = kid(el, tag); return k ? k.textContent.trim() : ''; }
function num(el, tag){ const t = txt(el, tag); if (t === '') return null; const n = Number(t); return isFinite(n) ? n : null; }
function num0(el, tag){ const n = num(el, tag); return n == null ? 0 : n; }
function first(el, tag){ const a = kid(el, tag); const c = a && a.children[0]; if (!c) return null; const n = Number(c.textContent); return isFinite(n) ? n : null; }
/* synchronous SHA-256 (hex) used for canonical-JSON hashes */
function sha256hex(str){
  const K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const b = new TextEncoder().encode(str), l = b.length, n = ((l + 9 + 63) >> 6) << 6, m = new Uint8Array(n);
  m.set(b); m[l] = 0x80; const dv = new DataView(m.buffer); dv.setUint32(n - 4, (l * 8) >>> 0); dv.setUint32(n - 8, Math.floor(l / 0x20000000));
  const H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19], W = new Uint32Array(64), r = (x, k) => (x >>> k) | (x << (32 - k));
  for (let o = 0; o < n; o += 64){
    for (let i = 0; i < 16; i++) W[i] = dv.getUint32(o + i * 4);
    for (let i = 16; i < 64; i++){ const s0 = r(W[i-15], 7) ^ r(W[i-15], 18) ^ (W[i-15] >>> 3), s1 = r(W[i-2], 17) ^ r(W[i-2], 19) ^ (W[i-2] >>> 10); W[i] = (W[i-16] + s0 + W[i-7] + s1) | 0; }
    let a = H[0], bb = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
    for (let i = 0; i < 64; i++){ const t1 = (h + (r(e, 6) ^ r(e, 11) ^ r(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + W[i]) | 0, t2 = ((r(a, 2) ^ r(a, 13) ^ r(a, 22)) + ((a & bb) ^ (a & c) ^ (bb & c))) | 0; h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = bb; bb = a; a = (t1 + t2) | 0; }
    H[0] = (H[0] + a) | 0; H[1] = (H[1] + bb) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0; H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
  }
  return H.map(x => (x >>> 0).toString(16).padStart(8, '0')).join('');
}
/* canonical JSON: keys sorted, listed volatile keys dropped */
function canon(v, drop){
  if (Array.isArray(v)) return '[' + v.map(x => canon(x, drop)).join(',') + ']';
  if (v && typeof v === 'object') return '{' + Object.keys(v).filter(k => !(drop || []).includes(k) && v[k] !== undefined).sort().map(k => JSON.stringify(k) + ':' + canon(v[k], drop)).join(',') + '}';
  return JSON.stringify(v === undefined ? null : v);
}
MLP.sha256Sync = sha256hex; MLP.canon = canon;
function fnv(str){ let h = 0x811c9dc5; for (let i = 0; i < str.length; i++){ h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193); } return (h >>> 0).toString(16).padStart(8, '0'); }
MLP.fnv = fnv;
MLP.baseName = n => String(n || '').replace(/^.*[\\/]/, '').replace(/\.pl$/i, '');
MLP.sha256 = async function (text){
  if (!(root.crypto && root.crypto.subtle)) return 'fnv-' + fnv(text);
  const buf = await root.crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
};
MLP.nameLen = s => String(s == null ? '' : s).length;
MLP.nameOk = s => MLP.nameLen(s) <= MLP.NAME_MAX;
MLP.shortName = function (s){
  s = String(s || '').replace(/\s+/g, ' ').trim();
  if (s.length <= MLP.NAME_MAX) return s;
  const ab = s.replace(/\b(Room|Rm)\b/gi, 'Rm').replace(/\bElectrical\b/gi, 'Elec').replace(/\bMechanical\b/gi, 'Mech').replace(/\bDetector\b/gi, 'Det')
    .replace(/\bDisplay\b/gi, 'Disp').replace(/\bCommunications?\b/gi, 'Comm').replace(/\bNorth\b/gi, 'N').replace(/\bSouth\b/gi, 'S').replace(/\bEast\b/gi, 'E').replace(/\bWest\b/gi, 'W');
  return ab.length <= MLP.NAME_MAX ? ab : ab.slice(0, MLP.NAME_MAX).trim();
};

/* ---------------- PipeCAD .pl parser ----------------
   Keys and fingerprints match the Battery Calculator's link format:
   detector key = `${area}#id${id}` (or #n<name>), display key = `${area}#disp${i}`. */
MLP.parsePl = function (text, fileName){
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  if (doc.getElementsByTagName('parsererror').length) throw new Error('Not a valid PipeCAD .pl (XML) file.');
  const rootEl = doc.documentElement;
  if (!rootEl || rootEl.localName !== 'PipeLayout') throw new Error('Not a PipeCAD project (no <PipeLayout> root).');
  const props = kid(rootEl, 'properties');
  const unitRaw = txt(rootEl, 'unit');
  const imperial = unitRaw === '1';
  const scale = imperial ? 1 : MLP.M_TO_FT;
  // Metric files: PipeCAD's metric hole-sensitivity unit is UNRESOLVED (no metric .pl sample yet). Values are NOT converted;
  // the parse result carries a warning so every app shows it until a metric sample confirms %obs/m vs %obs/ft.
  const sensScale = 1;
  const pipeProps = kid(rootEl, 'pipeType') ? rootEl : null;
  const projectName = txt(props, 'ProjectName');
  const results = {};
  kids(kid(rootEl, 'resultsDatabase'), 'SavedDatabase').forEach(sd => { results[txt(sd, 'detectorId')] = sd; });
  const out = {
    fileName: fileName || '', version: txt(rootEl, 'pipecadVersion'), unitRaw, imperial,
    unitLabel: imperial ? 'Imperial (ft)' : `Metric (m, unit ${unitRaw || '?'}) — lengths converted to ft`, sensWarning: imperial ? '' : 'Metric .pl: hole sensitivity is shown as PipeCAD wrote it. The metric unit (%obs/m or %obs/ft) is not yet confirmed — do not rely on the per-hole PASS/FAIL until a metric sample is verified.',
    project: { name: projectName || MLP.baseName(fileName), location: txt(props, 'Location'), designer: txt(props, 'Designer'), company: txt(props, 'CompanyName') },
    projectFromFile: !projectName,
    pipe: { innerDiameter: num(rootEl, 'innerDiameter'), outerDiameter: num(rootEl, 'outerDiameter'), material: txt(rootEl, 'material') },
    groups: [], skipped: []
  };
  if (!imperial) out.skipped.push(out.sensWarning);
  kids(kid(rootEl, 'floorDatabase'), 'Floor').forEach((fl, gi) => {
    const gname = txt(fl, 'name') || `Area ${gi + 1}`;
    const g = { idx: gi, name: gname, detectors: [], displays: [], psus: [], batteries: [] };
    const seen = {};
    kids(kid(fl, 'detectorDatabase'), 'Detector').forEach((d, di) => {
      const name = txt(d, 'name') || `Detector ${di + 1}`;
      const typeRaw = txt(d, 'type');
      const idTxt = txt(d, 'id');
      let key = `${gname}#${idTxt !== '' ? 'id' + idTxt : 'n' + name}`;
      if (seen[key]) key += '~' + (++seen[key]); else seen[key] = 1;
      const fanN = parseInt(txt(d, 'aspiratorSpeed'), 10);
      const isML = typeRaw === 'SOLO';   // 1.5.0: MiniLaser FHSD8075-ULF — standalone, never addressed (Brent Q1/Q2)
      const isASD = typeRaw === 'MICRA25' || txt(d, 'DetectorType') === 'MICRA25';   // 1.6.0: ASD-160 / Micra25 / Senator 25
      const rec = { key, ord: di, kind: isML ? 'minilaser' : isASD ? 'asd160' : 'detector', origName: name, typeRaw, type: MLP.DETECTOR_TYPES[typeRaw],
        fan: isASD ? null : (fanN >= 1 && fanN <= (isML ? 10 : 16)) ? fanN : null, address: isML ? '' : txt(d, 'address'), partNumber: txt(d, 'partNumber'),
        x: num0(d, 'startX') * scale, y: num0(d, 'startY') * scale, z: num0(d, 'startZ') * scale };
      rec.fp = fnv([rec.origName, rec.typeRaw, rec.fan, rec.x.toFixed(2), rec.y.toFixed(2)].join('|'));
      if (!rec.type){ out.skipped.push(`${gname}: “${name}” has unknown type “${typeRaw || 'blank'}” — skipped`); return; }
      // pipe network and PipeCAD results (relevant to commissioning)
      const runs = kids(kid(d, 'piperunDatabase'), 'Piperun').filter(r => !/^exhaust pipe$/i.test(txt(r, 'name')) && r.getElementsByTagName('Hole').length);
      let len = 0; const holes = [], testPoints = [];
      runs.forEach(r => kids(kid(r, 'pipeDatabase'), 'Pipe').forEach(pp => {
        const c = ['X', 'Y', 'Z'].map(a => [num(pp, 'start' + a), num(pp, 'end' + a)]);
        if (c.every(([a, b]) => a != null && b != null)) len += Math.hypot(...c.map(([a, b]) => b - a));
        kids(kid(pp, 'holeDatabase'), 'Hole').forEach(h => {
          const o = { i: txt(h, 'index'), endcap: /Endcap/i.test(h.getAttribute('xsi:type') || h.getAttribute('type') || ''), name: txt(h, 'name'), size: num(h, 'holeSize'), flow: num(h, 'holeFlowRate'), tt: num(h, 'transitTime'), sens: num(h, 'holeSensitivity') == null ? null : num(h, 'holeSensitivity') * sensScale };
          (txt(h, 'isTestPoint') === 'true' ? testPoints : holes).push(o);
        });
      }));
      const byIdx = (a, b) => (Number(a.i) || 0) - (Number(b.i) || 0);
      holes.sort(byIdx); testPoints.sort(byIdx);
      const sd = results[idTxt];
      rec.pipe = {
        runs: runs.map(r => txt(r, 'name')).join(', '), lengthFt: +(len * scale).toFixed(2),
        af: num(d, 'alarmFactor'), afActivated: txt(d, 'alarmFactorActivated') !== 'false',
        designSens: num(d, 'sensitivity'), maxTransit: num(d, 'maxTransitTime'),
        temperature: num(d, 'temperature'), pressure: num(d, 'pressure'),
        holeUnit: imperial ? 'in' : 'mm',
        flow: sd ? num(sd, 'totalFlow') : null, tt: sd ? first(sd, 'transitTime') : null, balance: sd ? first(sd, 'holeBalance') : null,
        bends90: sd ? first(sd, 'bends90') : null, sockets: sd ? first(sd, 'sockets') : null, clips: sd ? first(sd, 'clips') : null,
        hasResults: !!sd, holes, testPoints
      };
      if (isASD){ rec.pipe.resultsValid = sd ? txt(sd, 'resultsValid') : ''; rec.pipe.balanceMinLimit = num(d, 'balanceMinLimit') != null ? num(d, 'balanceMinLimit') : num(rootEl, 'balanceMinLimit'); rec.pipe.afActivatedRaw = txt(d, 'alarmFactorActivated'); rec.pipe.description = txt(props, 'Description'); }
      if (isML){   // 1.5.0: raw flags for the alarm-factor rule (Brent Q20) and DIP/Remote advice (Q22)
        const ints = tag => { const a = sd && kid(sd, tag); return a ? Array.from(a.children).map(c => Number(c.textContent) || 0) : null; };
        const b90 = ints('bends90'), b45 = ints('bends45');
        rec.pipe.afActivatedRaw = txt(d, 'alarmFactorActivated');
        rec.pipe.bends90Total = b90 ? b90.reduce((a, b) => a + b, 0) : null;
        rec.pipe.bends45Total = b45 ? b45.reduce((a, b) => a + b, 0) : null;
        rec.pipe.tees = sd ? sd.getElementsByTagName('tPieceList').length ? Array.from(sd.getElementsByTagName('tPieceList')).reduce((a, t) => a + t.children.length, 0) : 0 : null;
        const exp = kid(fl, 'expansionDatabase');
        rec.pipe.expansionInPl = !!(exp && exp.children.length);
        if (rec.pipe.expansionInPl) out.skipped.push(`${gname}: “${name}” — the .pl lists MiniLaser expansion items; they are not imported. Enter I/O modules by hand.`);
        if (txt(d, 'address') && txt(d, 'address') !== '0') out.skipped.push(`${gname}: “${name}” — MiniLaser address ${txt(d, 'address')} ignored (MiniLasers are never addressed).`);
      }
      if (!rec.pipe.tt && holes.length){ const m = Math.max(...holes.map(h => h.tt || 0)); if (m > 0) rec.pipe.tt = m; }
      g.detectors.push(rec);
    });
    kids(kid(fl, 'displayDatabase'), 'Display').forEach((d, i) => {
      const pn = txt(d, 'partNumber');
      const type = MLP.DISPLAY_PARTS[pn];
      if (!type){ out.skipped.push(`${gname}: display ${i + 1} has unknown partNumber “${pn}” — skipped`); return; }
      g.displays.push({ key: `${gname}#disp${i}`, ord: i, kind: 'display', origName: `${type} ${i + 1}`, type, partNumber: pn,
        x: num0(d, 'startX') * scale, y: num0(d, 'startY') * scale, z: num0(d, 'startZ') * scale,
        fp: fnv([pn, num0(d, 'startX'), num0(d, 'startY')].join('|')) });
    });
    kids(kid(fl, 'psuDatabase'), 'PSU').forEach(p => g.psus.push({ x: num0(p, 'startX') * scale, y: num0(p, 'startY') * scale, z: num0(p, 'startZ') * scale }));
    kids(kid(fl, 'batteryDatabase'), 'Battery').forEach(p => g.batteries.push({ x: num0(p, 'startX') * scale, y: num0(p, 'startY') * scale, z: num0(p, 'startZ') * scale }));
    out.groups.push(g);
  });
  if (!out.groups.some(g => g.detectors.length || g.displays.length)) throw new Error('No detectors or displays found in this PipeCAD file.');
  return out;
};


/* ---------------- design configuration (MASD Engineering Toolbox, Config mode) ----------------
   Same keys as the Field Report's Configure tab. src per key: 'manual' (value stated in the ModuLaser manual),
   'typical' (typical starting point — verify), 'design' (set by the designer). */
MLP.CONFIG_FIELDS = [
  { k: 'alert', label: 'Alert level', unit: '%obs/ft', kind: 'num', det: 1 },
  { k: 'action', label: 'Prealarm level', unit: '%obs/ft', kind: 'num', det: 1 },
  { k: 'fire1', label: 'Fire 1 level', unit: '%obs/ft', kind: 'num', det: 1 },
  { k: 'fire2', label: 'Fire 2 level (absolute)', unit: '%obs/ft', kind: 'num', det: 1 },
  { k: 'actionDly', label: 'Prealarm delay', unit: 's', kind: 'num', min: 0, max: 90, det: 1 },
  { k: 'fire1Dly', label: 'Fire 1 delay', unit: 's', kind: 'num', min: 0, max: 90, det: 1 },
  { k: 'cascade', label: 'Cascading alarms', kind: 'yn', det: 1 },
  { k: 'latchA', label: 'Latching alarms', kind: 'yn', det: 1, disp: 1 },
  { k: 'latchF', label: 'Latching faults', kind: 'yn', det: 1, disp: 1 },
  { k: 'flowLow', label: 'Flow low limit', unit: '%', kind: 'num', min: 0, max: 20, det: 1 },
  { k: 'flowHigh', label: 'Flow high limit', unit: '%', kind: 'num', min: 0, max: 20, det: 1 },
  { k: 'flowLow2', label: 'Flow low 2 limit', unit: '%', kind: 'num', min: 0, max: 30, det: 1 },
  { k: 'flowHigh2', label: 'Flow high 2 limit', unit: '%', kind: 'num', min: 0, max: 30, det: 1 },
  { k: 'flowDly', label: 'Flow fault delay', unit: 's', kind: 'num', min: 0, max: 240, det: 1 },
  { k: 'dayNight', label: 'Day/Night', kind: 'yn', det: 1 },
  { k: 'dayStart', label: 'Day start hour', kind: 'num', min: 0, max: 23, det: 1 },
  { k: 'nightStart', label: 'Night start hour', kind: 'num', min: 0, max: 23, det: 1 },
  { k: 'ldd', label: 'LDD (Laser Dust Discrimination)', kind: 'yn', det: 1 },
  { k: 'buzzer', label: 'Display buzzer enabled', kind: 'yn', disp: 1 },
  { k: 'cdmRole', label: 'Display role', kind: 'sel', opts: ['', 'Primary CDM', 'Backup CDM', 'Local display'], disp: 1 }
];
MLP.IO_PORTS = ['in1', 'in2', 'out1', 'out2', 'out3'];
MLP.IO_FUNCS = { in: ['', 'Remote reset', 'Remote isolate', 'Day/Night switch', 'Standby', 'Other'], out: ['', 'Alert', 'Action', 'Fire 1', 'Fire 2', 'General Fault', 'Urgent Fault', 'Flow Fault', 'Isolated', 'Other'] };
/* Values the ModuLaser manual states directly. Everything else in TYPICAL_DEFAULTS is a typical starting point. */
MLP.MANUAL_REF = 'ModuLaser Install Manual 04-4001-501-0803-05';
MLP.MANUAL_SOURCED = { flowLow: 'Table 29, p.76 (Flow Low Limit default 20%)', flowHigh: 'Table 29, p.76 (Flow High Limit default 20%)', flowDly: 'Table 29, p.76 (Flow Flt. Delay default 120 s, range 0–240)' };
/* Per-key citation / status text shown in tooltips and reports. */
MLP.CITES = {
  fire1: 'Starting point = FM/UL hole-sensitivity limit for the class (ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113: VEWFD ≤1.00, EWFD ≤1.50, SFD ≤2.50 %obs/ft; pass at or below). Design targets: VEWFD 1.0, EWFD 1.5, SFD 2.0 %obs/ft. Not a manual alarm default — Alarm Level is a ClassiFire factor (Table 24, p.71, default 8). Verify.',
  alert: 'Typical – unverified. Alert Level is a ClassiFire factor (Table 24, p.71, default 10). VEWFD 0.2 %obs/ft: per NFPA 76-2024 8.5.3.1.2.5 (VEWFD Alert 0.2 / Alarm 1.0 %/ft = 0.65 / 3.2 %/m, effective at each port, above ambient). EWFD 0.5 / SFD 1.0: site/design choice, no code basis.',
  action: 'Typical – unverified. ModuLaser has no "Action" level; this is the Prealarm level (Table 24, p.71: Prealarm factor default 6).',
  fire2: 'Typical – unverified. Alarm 2 Level is absolute (Table 24, p.71: 0.10–25, default 20; units not stated).',
  actionDly: 'Typical – unverified site choice. Prealarm Delay range 0–90 s (Table 26, p.73).',
  fire1Dly: 'Typical – unverified site choice. Alarm Delay range 0–90 s (Table 26, p.73).',
  flowLow: 'Table 29, p.76: default 20%.', flowHigh: 'Table 29, p.76: default 20%.', flowDly: 'Table 29, p.76: default 120 s (range 0–240).'
};
MLP.CLASSIFIRE_FACTORS = { alert: 10, prealarm: 6, alarm: 8, alarm2: 20 };   // Table 24, p.71 (factors / absolute; units not stated for Alarm 2)
MLP.HOLE_LIMITS = { VEWFD: 1.00, EWFD: 1.50, SFD: 2.50, ref: 'ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113 (FM/UL hole limits) — pass at or below (≤) the limit (Brent 2026-10-13)' };
MLP.configSeed = function (perfClass, kind){
  const values = {}, src = {};
  if (kind === 'display'){
    values.latchA = 'N'; values.latchF = 'N'; values.buzzer = 'Y'; ['latchA', 'latchF', 'buzzer'].forEach(k => { src[k] = 'typical'; });
    values.io = { out1: { used: true, fn: 'General Fault', addr: '' } }; src['io.out1'] = 'manual';
    return { perfClass: '', values, src };
  }
  const T = MLP.TYPICAL_DEFAULTS[perfClass];
  if (T) Object.keys(T).forEach(k => { values[k] = T[k]; src[k] = MLP.MANUAL_SOURCED[k] ? 'manual' : 'typical'; });
  Object.assign(values, { cascade: 'N', latchA: 'N', latchF: 'N', dayNight: 'N', ldd: 'Y' });
  ['cascade', 'latchA', 'latchF', 'dayNight', 'ldd'].forEach(k => { src[k] = 'typical'; });
  values.io = {};
  return { perfClass: perfClass || '', values, src };
};
MLP.srcLabel = s => s === 'manual' ? 'manual' : s === 'typical' ? 'typical – unverified' : s === 'design' ? 'design' : '';
function cfgFlat(c){ const o = {}; if (!c) return o; const v = c.values || {};
  o.cfg_perf = c.perfClass || '';
  MLP.CONFIG_FIELDS.forEach(f => { o['cfg_' + f.k] = v[f.k] == null ? '' : String(v[f.k]); });
  MLP.IO_PORTS.forEach(p => { const x = (v.io || {})[p]; o['cfg_io_' + p] = x && x.used ? `${x.fn || ''} ${x.addr || ''}`.trim() || 'used' : ''; });
  return o; }
const CFG_DIFF_FIELDS = [['cfg_perf', 'Performance class']].concat(MLP.CONFIG_FIELDS.map(f => ['cfg_' + f.k, f.label])).concat(MLP.IO_PORTS.map(p => ['cfg_io_' + p, p.toUpperCase() + ' assignment']));

/* ---------------- field-change loop ----------------
   doc.changes: [{ id, dev, devName, field, label, design, value, by, at, why, photo, pipecad, status, verify:{ by, at, note }, plCheck:{ state, at, file, found } }]
   status: logged → verified (designer, Toolbox) | rejected → approved (QA/Auditor).
   doc.approvals: { technician:{ name, date, status }, designer:{…}, qa:{…} } */
MLP.CHANGE_STATUS = ['logged', 'verified', 'rejected', 'approved'];
MLP.APPROVAL_ROLES = [['technician', 'Technician (logged on site)'], ['designer', 'Designer (verified in the Toolbox)'], ['qa', 'QA / Auditor (sign-off)']];
/* Fields whose change must also be made in the PipeCAD model (PipeCAD has no import). */
MLP.PIPECAD_FIELDS = { 'cfg.fan': 'Fan speed', 'cfg.af': 'Alarm Factor', desc: 'Detector name', 't.tt.pipecad': 'Transport time', 'perf.holes': 'Sampling holes', 'perf.target': 'Performance class' };
MLP.changeId = () => 'fc-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 6);
/* Check logged PipeCAD changes against a freshly parsed .pl (MLP.parsePl result). Returns [{id, state:'match'|'mismatch'|'not-found', found}] */
MLP.verifyChangesAgainstPl = function (changes, parsed, devices){
  const byKey = {}, byName = {};
  (parsed.groups || []).forEach(g => g.detectors.forEach(d => { byKey[d.key] = d; byName[String(d.origName || '').toLowerCase()] = d; }));
  const devById = {}; (devices || []).forEach(d => { devById[d.id] = d; });
  return (changes || []).filter(c => c.pipecad).map(c => {
    const dv = devById[c.dev] || {}; const key = dv.pl && dv.pl.key;
    let d = (key && byKey[key]) || byName[String(c.field === 'desc' ? c.value : (dv.plName || c.devName || '')).toLowerCase()];
    if (!d) return { id: c.id, state: 'not-found', found: '' };
    const p = d.pipe || {};
    const found = { 'cfg.fan': d.fan, 'cfg.af': p.af, desc: d.origName, 't.tt.pipecad': p.tt == null ? '' : (+p.tt).toFixed(1), 'perf.holes': p.holes ? p.holes.length : '', 'perf.target': MLP.TT_TO_CLASS[p.maxTransit] || '' }[c.field];
    const eq = (a, b) => { const x = parseFloat(a), y = parseFloat(b); return isFinite(x) && isFinite(y) ? Math.abs(x - y) < 0.051 : String(a).trim().toLowerCase() === String(b).trim().toLowerCase(); };
    return { id: c.id, state: eq(found, c.value) ? 'match' : 'mismatch', found: found == null ? '' : String(found) };
  });
};

/* ---------------- project document ---------------- */
MLP.blank = function (){
  return { format: MLP.FORMAT, schemaVersion: MLP.SCHEMA_VERSION, savedAt: '', savedBy: null,
    project: { name: '', location: '', designer: '', company: '', building: '', networkNumber: '', preparedBy: '', date: '', brand: '' },
    design: null, site: null, changes: [], approvals: {} };
};
MLP.isProject = o => !!(o && o.format === MLP.FORMAT && typeof o.schemaVersion === 'number');
MLP.parse = function (text){
  let o; try { o = JSON.parse(text); } catch (e){ throw new Error('Not a JSON file.'); }
  if (!MLP.isProject(o)) throw new Error('Not a ModuLaser project file (format must be “modulaser-project”).');
  if (o.schemaVersion > MLP.SCHEMA_VERSION) throw new Error(`This project file uses schema ${o.schemaVersion}; this app reads up to ${MLP.SCHEMA_VERSION}. Update the app.`);
  return o;
};
MLP.stringify = function (doc, app, rev, user){
  doc.format = MLP.FORMAT; doc.schemaVersion = MLP.SCHEMA_VERSION; doc.savedAt = new Date().toISOString(); doc.savedBy = Object.assign({ app, rev }, user ? { name: user } : {});
  if (doc.design){ doc.design.hash = MLP.designHash(doc.design); doc.design.id = MLP.designId(doc.design); }
  if (doc.site) doc.site.hash = MLP.siteHash(doc.site);
  return JSON.stringify(doc, null, 1);
};
/* SHA-256 over canonical JSON of the whole design (volatile keys excluded): tamper-evident.
   design.id keeps the old 32-bit FNV identity hash as a short display id only. */
MLP.HASH_DROP = ['hash', 'id', 'updatedAt', 'importedAt'];
/* 1.6.0 (B3a): new fields at their defaults are stripped before hashing, so an unchanged 02.01.000 file keeps its hash. */
MLP.HASH_DEFAULTS = { brand: 'edwards', variant: '120', accessories: [], facuSource: false, ulOptIn: false, psVariant: '120', psTamper: false, psSeismic: false, cabinetUserSet: false, tpFacuSource: false, tpFacuUserSet: false };
function stripDefaults(v){
  if (Array.isArray(v)) return v.map(stripDefaults);
  if (v && typeof v === 'object'){ const o = {}; Object.keys(v).forEach(k => { const d = MLP.HASH_DEFAULTS[k], x = v[k];
    if (d !== undefined && (Array.isArray(d) ? Array.isArray(x) && !x.length : x === d)) return; if (k === 'powerSource' || k === 'tpPowerSource') { if (x == null || x === '') return; } o[k] = stripDefaults(x); }); return o; }
  return v;
}
MLP.stripDefaults = stripDefaults;
MLP.designHash = function (design){ return design ? 'sha256:' + sha256hex(canon(stripDefaults(design), MLP.HASH_DROP)) : ''; };
MLP.siteHash = function (site){ return site ? 'sha256:' + sha256hex(canon(site, ['hash', 'updatedAt'])) : ''; };
MLP.designId = function (design){
  if (!design) return '';
  const strip = { psus: (design.psus || []).map(p => [p.id, p.name, p.area, p.location, p.model, p.battery && p.battery.ah, p.battery && p.battery.qty, p.requiredAh]),
    devices: (design.devices || []).map(d => [d.id, d.name, d.type, d.area, d.address, d.psuId, d.fan, d.pl && d.pl.fp].concat(d.config ? [JSON.stringify(d.config.values || {}), d.config.perfClass || ''] : [])) };
  return fnv(JSON.stringify(strip));
};

/* Build a design section straight from parsed .pl files (Field Report without a calc file).
   PSUs come only from the Battery Calculator; .pl PSU/Battery entries are placement only. */
MLP.designFromPl = function (parsedList, links, perf){
  const devices = [], areas = [];
  parsedList.forEach((pc, fi) => {
    const link = links[fi];
    pc.groups.forEach(g => {
      if (!areas.includes(g.name)) areas.push(g.name);
      g.displays.concat(g.detectors).forEach(d => devices.push(MLP.deviceFromPl(d, g.name, link, undefined, perf)));
    });
  });
  return { owner: 'pl-import', rev: '', updatedAt: new Date().toISOString(), plLinks: links, areas, psus: [], devices,
    placement: parsedList.map((pc, fi) => ({ link: links[fi].id, groups: pc.groups.map(g => ({ area: g.name, psus: g.psus, batteries: g.batteries })) })) };
};
MLP.deviceFromPl = function (d, area, link, extra, perf){
  const dev = { id: (link ? link.id : 'pl') + '|' + d.key, kind: d.kind, type: d.type, partNumber: d.partNumber || '',
    model: d.kind === 'display' ? MLP.DISPLAY_MODELS[d.type] || '' : d.kind === 'minilaser' ? MLP.MINILASER.model : d.kind === 'asd160' ? MLP.partFor('edwards', 'asd160') : 'FHSD8330',
    name: d.origName, plName: d.origName, area, address: '', psuId: '', fan: d.fan || null, cluster: '',
    pos: { x: +(d.x || 0).toFixed(2), y: +(d.y || 0).toFixed(2), z: +(d.z || 0).toFixed(2) },
    pl: link ? { link: link.id, file: link.name, key: d.key, fp: d.fp } : null, pipe: d.pipe || null };
  if (d.kind === 'minilaser'){ const ml = MLP.miniLaserFromPl(d, extra && extra.perfClass ? extra.perfClass : MLP.miniLaserClass(perf, area));
    Object.assign(dev, { standalone: true, network: null, ioModules: 0, minilaser: { alarmFactor: ml.alarmFactor, alarmFactorSrc: ml.alarmFactorSrc, perfClass: ml.perfClass, perfClassSrc: ml.perfClassSrc,
      holes: ml.holes, configMethod: ml.configMethod, advice: ml.advice.text, derivation: ml.derivation, expansionInPl: ml.expansionInPl } }); }
  if (d.kind === 'asd160'){ const ev = MLP.asd160Evaluate(d, perf, area); Object.assign(dev, { standalone: false, network: 1, relayCard: false,
    asd160: { alarmFactor: ev.af.af, alarmFactorSrc: ev.af.src, perfClass: ev.cls.cls, perfClassSrc: ev.cls.src, ul: ev.ul, holes: ev.counts.sampling, holesAll: ev.counts.all, worstHole: ev.worst, transport: ev.transport, issues: ev.issues } }); }
  return Object.assign(dev, extra || {});
};
MLP.linkFromParsed = function (pc, sha, size, lastModified){
  return { id: 'pl-' + String(sha).slice(0, 12), name: pc.fileName, sha256: sha, size: size || null, lastModified: lastModified || null,
    version: pc.version, unit: pc.unitLabel, project: pc.project.name, groups: pc.groups.map(g => g.name), importedAt: new Date().toISOString() };
};

/* ---------------- SenseNET networks (1.4.0) ----------------
   design.devices[].network: SenseNET network number (1, 2, …), each network holds up to 127 modules.
   Missing on older files → network 1. Standalone devices carry standalone:true (their own 1–9 pool per power
   supply) and network null. Addresses are unique per network, not per design. */
MLP.MAX_PER_NETWORK = 127;
MLP.devNetwork = d => (d && (d.standalone || d.kind === 'minilaser')) ? null : (parseInt(d && d.network, 10) >= 1 ? parseInt(d.network, 10) : 1);
MLP.devAddrScope = d => (d && d.standalone) ? 'sa:' + (d.psuId || '') : 'net:' + MLP.devNetwork(d);
MLP.networkCounts = function (devices){ const c = {}; (devices || []).forEach(d => { const n = MLP.devNetwork(d); if (n != null) c[n] = (c[n] || 0) + 1; }); return c; };
/* ---------------- validation ---------------- */
MLP.validateDesign = function (design){
  const issues = [];
  if (!design) return issues;
  const byAddr = {};
  (design.devices || []).forEach(d => {
    if (!MLP.nameOk(d.name)) issues.push({ id: d.id, level: 'error', msg: `“${d.name}” is ${MLP.nameLen(d.name)} characters — the ModuLaser display shows ${MLP.NAME_MAX}.` });
    if (d.kind && !MLP.KNOWN_KINDS.includes(d.kind)){ issues.push({ id: d.id, level: 'warn', msg: `${d.name}: unknown device kind “${d.kind}” — this app version cannot check it.` }); return; }
    if (d.kind === 'asd160' && d.standalone && String(d.address || '').trim()) issues.push({ id: d.id, level: 'error', msg: `${d.name}: a stand-alone ASD-160 is never addressed (address ${d.address} must be cleared).` });
    if (d.kind === 'asd160' && d.asd160 && d.asd160.issues) d.asd160.issues.forEach(x => issues.push({ id: d.id, level: x.level, msg: `${d.name}: ${x.msg}` }));
    if (d.kind === 'minilaser'){ const m = d.minilaser || {};   // 1.5.0: never addressed; fan and alarm factor checks
      if (String(d.address || '').trim()) issues.push({ id: d.id, level: 'error', msg: `${d.name}: MiniLasers are never addressed (address ${d.address} must be cleared).` });
      if (!(d.fan >= 1 && d.fan <= 10)) issues.push({ id: d.id, level: 'incomplete', msg: `⚠ ${d.name}: MiniLaser fan speed not set (1–10).` });
      if (m.derivation && m.derivation.fail) issues.push({ id: d.id, level: 'error', msg: `${d.name}: ${m.derivation.msg}` });
      return; }
    const a = String(d.address == null ? '' : d.address).trim();
    if (a && a !== '0'){ const k = MLP.devAddrScope(d) + '|' + a; (byAddr[k] = byAddr[k] || []).push(d); const n = Number(a), max = d.standalone ? 9 : 127;
      if (!(n >= 1 && n <= max)) issues.push({ id: d.id, level: 'error', msg: `${d.name}: address ${a} is outside 1–${max}.` }); }
  });
  Object.entries(byAddr).forEach(([k, list]) => { if (list.length > 1){ const a = k.slice(k.indexOf('|') + 1), sc = k.startsWith('net:') ? ` on SenseNET ${k.slice(4, k.indexOf('|'))}` : ' on standalone supply';
    list.forEach(d => issues.push({ id: d.id, level: 'error', msg: `Address ${a}${sc} is used by ${list.map(x => x.name).join(', ')}.` })); } });
  const nc = MLP.networkCounts(design.devices);
  Object.keys(nc).forEach(n => { if (nc[n] > MLP.MAX_PER_NETWORK) issues.push({ id: '', level: 'error', msg: `SenseNET ${n} has ${nc[n]} modules — limit ${MLP.MAX_PER_NETWORK} per network.` }); });
  return issues;
};

/* ---------------- diff ----------------
   Compares two design sections. Returns {project:[], psus:{added,removed,changed}, devices:{added,removed,changed}, count}. */
const DEV_FIELDS = [['ioModules', 'MiniLaser I/O modules'], ['mlAf', 'MiniLaser alarm factor'], ['mlMethod', 'MiniLaser configuration'], ['name', 'Name'], ['type', 'Type'], ['area', 'Area/Group'], ['address', 'Address'], ['network', 'SenseNET network'], ['psuId', 'Power supply'], ['fan', 'Fan speed'], ['cluster', 'Cluster'], ['model', 'Model'], ['pipeTT', 'PipeCAD transport time (s)'], ['pipeHoles', 'Sampling holes'], ['pipeLen', 'Pipe length (ft)'], ['af', 'Alarm Factor']];
const PSU_FIELDS = [['name', 'Name'], ['area', 'Area/Group'], ['location', 'Location'], ['model', 'Model'], ['batteryModel', 'Battery'], ['batteryAh', 'Battery Ah'], ['batteryQty', 'Battery qty'], ['requiredAh', 'Required Ah'], ['standbyHours', 'Standby (h)'], ['alarmMinutes', 'Alarm (min)'], ['status', 'Calculator result']];
function devFlat(d){ const p = d.pipe || {}; return { name: d.name, type: d.type, area: d.area, address: d.address || '', network: d.standalone ? 'standalone' : String(MLP.devNetwork(d)), psuId: d.psuId || '', fan: d.fan == null ? '' : String(d.fan), cluster: d.cluster || '', model: d.model || '',
  pipeTT: p.tt == null ? '' : (+p.tt).toFixed(1), pipeHoles: p.holes ? String(p.holes.length) : '', pipeLen: p.lengthFt == null ? '' : (+p.lengthFt).toFixed(1), af: p.af == null ? '' : String(p.af),
  ioModules: d.ioModules == null ? '' : String(d.ioModules), mlAf: d.minilaser && d.minilaser.alarmFactor != null ? String(d.minilaser.alarmFactor) : '', mlMethod: d.minilaser ? d.minilaser.configMethod || '' : '' }; }
function psuFlat(p){ const b = p.battery || {}; return { name: p.name, area: p.area || '', location: p.location || '', model: p.model || '', batteryModel: b.model || '', batteryAh: b.ah == null ? '' : String(b.ah), batteryQty: b.qty == null ? '' : String(b.qty),
  requiredAh: p.requiredAh == null ? '' : (+p.requiredAh).toFixed(2), standbyHours: p.standbyHours == null ? '' : String(p.standbyHours), alarmMinutes: p.alarmMinutes == null ? '' : String(p.alarmMinutes), status: p.status || '' }; }
function diffList(oldL, newL, flat, fields){
  const om = new Map((oldL || []).map(x => [x.id, x])), nm = new Map((newL || []).map(x => [x.id, x]));
  const res = { added: [], removed: [], changed: [] };
  nm.forEach((n, id) => {
    const o = om.get(id);
    if (!o){ res.added.push(n); return; }
    const a = flat(o), b = flat(n);
    const ch = fields.filter(([k]) => String(a[k]) !== String(b[k])).map(([k, l]) => ({ f: k, label: l, old: a[k], new: b[k] }));
    if (ch.length) res.changed.push({ id, name: n.name, item: n, fields: ch });
  });
  om.forEach((o, id) => { if (!nm.has(id)) res.removed.push(o); });
  return res;
}
MLP.diffDesign = function (oldD, newD){
  const project = [];
  const devices = diffList(oldD && oldD.devices, newD && newD.devices, d => Object.assign(devFlat(d), cfgFlat(d.config)), DEV_FIELDS.concat(CFG_DIFF_FIELDS));
  const psus = diffList(oldD && oldD.psus, newD && newD.psus, psuFlat, PSU_FIELDS);
  const count = devices.added.length + devices.removed.length + devices.changed.length + psus.added.length + psus.removed.length + psus.changed.length;
  return { project, devices, psus, count };
};
MLP.diffProject = function (oldP, newP){
  const keys = ['name', 'location', 'designer', 'company', 'building', 'networkNumber', 'brand'];
  return keys.filter(k => (newP || {})[k] && String((oldP || {})[k] || '') !== String(newP[k])).map(k => ({ f: k, old: (oldP || {})[k] || '', new: newP[k] }));
};
MLP.diffHtml = function (diff, esc){
  esc = esc || (s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])));
  const sec = (title, r) => {
    if (!r.added.length && !r.removed.length && !r.changed.length) return '';
    return `<div class="mlp-diff-sec"><div class="mlp-diff-h">${title}</div><ul>` +
      r.added.map(x => `<li class="add">+ Added <b>${esc(x.name)}</b>${x.area ? ' · ' + esc(x.area) : ''}</li>`).join('') +
      r.removed.map(x => `<li class="del">− Removed <b>${esc(x.name)}</b>${x.area ? ' · ' + esc(x.area) : ''}</li>`).join('') +
      r.changed.map(x => `<li class="chg">~ <b>${esc(x.name)}</b>: ${x.fields.map(f => `${esc(f.label)} <s>${esc(f.old || '—')}</s> → <b>${esc(f.new || '—')}</b>`).join('; ')}</li>`).join('') + '</ul></div>';
  };
  return (sec('Devices', diff.devices) + sec('Power supplies', diff.psus)) || '<p>No design changes.</p>';
};

/* ---------------- Performance Criteria (design.performance) ----------------
   perf.standard = one 'Referenced standard' preset (project), optional per-Area/Group overrides (perf.areas[a].standard).
   NFPA presets: UL 268 7th Ed. thresholds (hole sensitivity at or below (≤) VEWFD 1.0 / EWFD 1.5 / SFD-OAP 2.18 %obs/ft;
   transport time no more than 60 / 43 / 43 s) plus the selected code's prescriptions; printouts state "Complies with UL 268, 7th Edition".
   FM DS presets: FM requirements only (not UL, no UL 268 statement). BS presets mirror the Battery Calculator's BS design bases.
   Only cited values are prefilled; the rest are blank ("engineer to define") and must be entered, referenced and confirmed. */
MLP.PERF_CLASSES = ['VEWFD', 'EWFD', 'SFD'];
MLP.UL_STATEMENT = 'Complies with UL 268, 7th Edition';
/* Brent 2026-10-13 (21:10 ET, supersedes strict '<'): sensitivity PASSES when ≤ the class maximum — the more restrictive of UL and NFPA;
   transport time ≤. UL projects also enforce the ModuLaser UL 268 range lower limits (Install Manual 04-4001-501-0803-05, App. A, printed p.113). */
MLP.SENS_TARGETS = { VEWFD: 1.0, EWFD: 1.5, SFD: 2.0 };   // design 'Target' values, %obs/ft (Brent 2026-10-13)
MLP.UL_RANGES = {
  VEWFD: { name: 'Special Application Range 1', sensMin: 0.05, sensMax: 1.00, ttMin: 3, ttMax: 60, provisional: false },
  EWFD:  { name: 'Special Application Range 2', sensMin: 0.05, sensMax: 2.18, ttMin: 3, ttMax: 43, provisional: false, note: 'max 1.5 %obs/ft per NFPA 76-2024 8.5.3.2.1.3' },
  /* Brent 2026-10-13 21:17 ET: SFD/OAP = UL Open Area 1.70–2.18 %obs/ft, 6–43 s (App. A p.113) — final; both bounds enforced. */
  SFD:   { name: 'Open Area', sensMin: 1.70, sensMax: 2.18, ttMin: 6, ttMax: 43, provisional: false }
};
/* NFPA code limits per class (null = the code sets no per-hole value). */
MLP.NFPA_LIMITS = {
  VEWFD: { sens: 1.0, tt: 60, ref: 'NFPA 76-2024 8.5.3.1.2.5 (alarm 1.0 %/ft), 8.5.3.1.2.6 (60 s)' },
  EWFD:  { sens: 1.5, tt: 90, ref: 'NFPA 76-2024 8.5.3.2.1.3 (alarm 1.5 %/ft), 8.5.3.2.1.4 (90 s)' },
  SFD:   { sens: null, tt: 120, ref: 'NFPA 72 (no per-hole sensitivity; 120 s maximum ASD transport time)' }
};
/* the more restrictive of UL (range max) and NFPA, computed — VEWFD 1.0/60, EWFD 1.5/43, SFD 2.18/43; UL range minimums carried as lower bounds */
MLP.stricterOf = (a, b) => a == null ? b : b == null ? a : Math.min(a, b);
MLP.UL_LIMITS = {};
['VEWFD', 'EWFD', 'SFD'].forEach(c => { const r = MLP.UL_RANGES[c], n = MLP.NFPA_LIMITS[c];
  MLP.UL_LIMITS[c] = { sens: MLP.stricterOf(r.sensMax, n.sens), tt: MLP.stricterOf(r.ttMax, n.tt), sensMin: r.sensMin, ttMin: r.ttMin }; });   // SFD = SFD/OAP
MLP.ulRangeText = c => { const r = MLP.UL_RANGES[c]; if (!r) return ''; return `UL 268 ${r.name}: ${r.sensMin.toFixed(2)}–${r.sensMax.toFixed(2)} %obs/ft${c === 'EWFD' ? ' (max 1.5 per NFPA 76)' : ''}, ${r.ttMin}–${r.ttMax} s${r.provisional ? ' — provisional' : ''}`; };
/* pass rules: value ≤ max (and ≥ min when a UL lower limit applies) */
MLP.sensPass = (v, L) => v != null && L && L.sens != null && v <= L.sens + 1e-9 && (L.sensMin == null || v >= L.sensMin - 1e-9);
MLP.ttPass = (v, L) => v != null && L && L.tt != null && v <= L.tt + 1e-9 && (L.ttMin == null || v >= L.ttMin - 1e-9);
MLP.UL_REFS = {
  VEWFD: 'UL 268, 7th Ed. Special Application Range 1 — ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113; NFPA 76-2024 8.5.3.1.2.5 (1.0 %/ft) and 8.5.3.1.2.6 (60 s)',
  EWFD: 'UL 268, 7th Ed. Special Application Range 2 — Install Manual App. A, printed p.113; 1.5 %obs/ft from NFPA 76-2024 8.5.3.2.1.3 (maximum permitted threshold based on the UL detector limit and NFPA 76 sensitivity); NFPA 76-2024 8.5.3.2.1.4 allows 90 s but UL governs (43 s)',
  SFD: 'UL 268, 7th Ed. Open Area (SFD/OAP) — Install Manual App. A, printed p.113' };
MLP.UL_REF = 'UL 268, 7th Edition ranges per ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113 (EWFD 1.5 %obs/ft from NFPA 76)';
MLP.FM_REF = 'FM Class 3230 per ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113 (FM/UL hole limits)';
MLP.FM_LIMITS = { VEWFD: { sens: 1.00, tt: 60 }, EWFD: { sens: 1.50, tt: 90 }, SFD: { sens: 2.50, tt: 120 } };
/* family NFPA → UL thresholds + code; FM → FM only; BS / Custom → engineer-defined */
MLP.PERF_PRESETS = [
  { id: 'VEWFD – NFPA 76/318', cls: 'VEWFD', family: 'NFPA', code: 'NFPA 76 / NFPA 318' },
  { id: 'EWFD – NFPA 76', cls: 'EWFD', family: 'NFPA', code: 'NFPA 76' },
  { id: 'EWFD – FM DS 5-32', cls: 'EWFD', family: 'FM', code: 'FM Global Property Loss Prevention Data Sheet 5-32' },
  { id: 'SFD/OAP – NFPA 72', cls: 'SFD', family: 'NFPA', code: 'NFPA 72' },
  { id: 'SFD – FM DS 5-48', cls: 'SFD', family: 'FM', code: 'FM Global Property Loss Prevention Data Sheet 5-48' },
  /* British Standards: exactly the BS options of the Battery Calculator's Design Basis drop-down */
  { id: 'BS 5839-1 Category M/L', cls: '', family: 'BS', code: 'BS 5839-1 Category M/L' },
  { id: 'BS 5839-1 Category M/L + Generator', cls: '', family: 'BS', code: 'BS 5839-1 Category M/L + Generator' },
  { id: 'BS 5839-1 Category P (Staffed)', cls: '', family: 'BS', code: 'BS 5839-1 Category P (Staffed)' },
  { id: 'BS 5839-1 Category P (Unstaffed)', cls: '', family: 'BS', code: 'BS 5839-1 Category P (Unstaffed)' },
  { id: 'Custom', cls: '', family: 'Custom', code: '' }
];
MLP.perfPreset = id => MLP.PERF_PRESETS.find(p => p.id === id) || null;
MLP.perfIsUl = id => { const p = MLP.perfPreset(id); return !!(p && p.family === 'NFPA'); };
/* code prescriptions per preset: cited rows prefilled, everything else 'engineer to define' (value blank). */
/* Research 2026-10-13 (/workspace/deliverables/ModuLaser-Commissioning-Defaults-Citations-2026-10-13.md): NFPA 76-2024 clauses. */
MLP.PERF_CODE_CITED = {
  'VEWFD – NFPA 76/318': [
    { item: 'NFPA 76 VEWFD sensitivity at each sampling port (effective, above ambient)', value: 'Alert 0.2 %/ft (0.65 %/m); Alarm 1.0 %/ft (3.2 %/m)', ref: 'NFPA 76-2024 8.5.3.1.2.5' },
    { item: 'NFPA 76 VEWFD coverage area per port / detector', value: 'per NFPA 76-2024 8.5.3.1.2.1–8.5.3.1.2.2 (engineer to apply to this layout)', ref: 'NFPA 76-2024 8.5.3.1.2.1–8.5.3.1.2.2' },
    { item: 'NFPA 76 VEWFD transport time', value: '≤ 60 s from the most remote port', ref: 'NFPA 76-2024 8.5.3.1.2.6' },
    { item: 'NFPA 76 VEWFD manufacturer criteria', value: 'Installed per the manufacturer: ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113', ref: 'NFPA 76-2024 8.5.3.1.2.4' },
    /* Cleanroom / semiconductor path — NFPA 318-2025 §11.1.3 (Research addendum 2, read on NFPA LiNK). 318 does not use the VEWFD/EWFD terms. */
    { item: 'NFPA 318 cleanroom: listed smoke detection in the return airstream', value: 'Listed system in the cleanroom return airstream, installed per NFPA 72; ASD or spot-type permitted; listed for the cleanroom airflow velocities', ref: 'NFPA 318-2025 11.1.3.1, 11.1.3.1.1, 11.1.3.1.2, 11.1.3.3' },
    { item: 'NFPA 318 system designation (risk assessment)', value: 'Life safety (evacuation at the 11.1.3.5.2 alarm level) or property protection (ERT investigates on alert; no automatic evacuation) — engineer selects', ref: 'NFPA 318-2025 11.1.3.4' },
    { item: 'NFPA 318 below the waffle floor', value: '≤ 200 ft² per port; alert ≤ 0.2 %/ft (0.65 %/m); alarm ≤ 1.0 %/ft (3.2 %/m) at the sampling port (hole sensitivity)', ref: 'NFPA 318-2025 11.1.3.5, 11.1.3.5.1, 11.1.3.5.2, A.11.1.3.5.2' },
    { item: 'NFPA 318 entry to the return air path', value: '≤ 4.3 ft² (0.4 m²) per port absent a performance-based design; alert 0.2 / alarm 1.0 %/ft', ref: 'NFPA 318-2025 11.1.3.6, 11.1.3.6.1, 11.1.3.6.2' },
    { item: 'NFPA 318 transport time', value: '≤ 60 s from the most remote port', ref: 'NFPA 318-2025 11.1.3.7' }],
  'EWFD – NFPA 76': [
    { item: 'NFPA 76 EWFD alarm sensitivity', value: 'Alarm 1.5 %/ft (5.0 %/m)', ref: 'NFPA 76-2024 8.5.3.2.1.3' },
    { item: 'NFPA 76 EWFD coverage area', value: '400 ft² per port / detector', ref: 'NFPA 76-2024 8.5.3.2.1.2' },
    { item: 'EWFD transport time', value: '≤ 43 s (UL 268, 7th Ed. Special Application Range 2 governs; NFPA 76 alone allows 90 s)', ref: 'UL 268 Range 2 per Install Manual App. A p.113; NFPA 76-2024 8.5.3.2.1.4 (90 s)' },
    { item: 'NFPA 76 EWFD manufacturer criteria', value: 'Installed per the manufacturer: ModuLaser Install Manual 04-4001-501-0803-05, App. A, printed p.113', ref: 'NFPA 76-2024 8.5.3.2.1.5' }],
  'SFD/OAP – NFPA 72': [],
  'EWFD – FM DS 5-32': [], 'SFD – FM DS 5-48': []
};
MLP.perfCodeReqs = function (id){
  const p = MLP.perfPreset(id); if (!p || p.family === 'Custom') return [];
  const rows = (MLP.PERF_CODE_CITED[id] || []).map(r => Object.assign({}, r, { src: 'cited', confirmed: false }));
  rows.push({ item: `${p.code}: further prescriptions for this application (engineer to define)`, value: '', ref: '', src: 'engineer', confirmed: false });
  return rows;
};
MLP.perfLimitBlank = () => ({ sens: null, tt: null, ref: '', confirmed: false, src: '' });
/* UL 268 compliance is never auto-confirmed: limits carry the scope's ulConfirmed flag (QA re-check 2026-10-13). */
MLP.perfUlLimits = ulConfirmed => { const o = {}; MLP.PERF_CLASSES.forEach(c => { const U = MLP.UL_LIMITS[c]; o[c] = { sens: U.sens, tt: U.tt, sensMin: U.sensMin, ttMin: U.ttMin, target: MLP.SENS_TARGETS[c], ulRange: MLP.ulRangeText(c), provisional: !!MLP.UL_RANGES[c].provisional, ref: MLP.UL_REFS[c], confirmed: !!ulConfirmed, src: 'UL' }; }); return o; };
MLP.perfPresetLimits = function (id){
  const p = MLP.perfPreset(id); const out = {};
  if (p && p.family === 'NFPA') return MLP.perfUlLimits(false);
  MLP.PERF_CLASSES.forEach(c => { out[c] = p && p.family === 'FM' ? { sens: MLP.FM_LIMITS[c].sens, tt: MLP.FM_LIMITS[c].tt, target: MLP.SENS_TARGETS[c], ref: MLP.FM_REF, confirmed: false, src: 'prefill' } : MLP.perfLimitBlank(); });
  return out;
};
MLP.perfScopeInit = (o, id) => { o.standard = id; o.ulConfirmed = false; delete o.ulOptIn; o.limits = MLP.perfPresetLimits(id); o.codeReqs = MLP.perfCodeReqs(id); return o; };
MLP.perfBlank = () => Object.assign(MLP.perfScopeInit({ standardOther: '', areas: {}, narrative: '', narrativeDraft: '', eorName: '', specRef: '', definedBy: '', definedAt: '' }, 'SFD/OAP – NFPA 72'), { statement: '', market: 'UL' });
/* migrate 1.2.0 drafts (market/basis) to presets */
MLP.perfMigrate = function (perf){
  if (!perf || perf.standard !== undefined) return perf;
  const map = b => b === 'UL' ? 'SFD/OAP – NFPA 72' : b === 'FM' ? 'EWFD – FM DS 5-32' : b === 'NFPA 76' ? 'EWFD – NFPA 76' : 'Custom';
  const one = (o, b) => { const keep = o.limits; MLP.perfScopeInit(o, map(b)); if (!MLP.perfIsUl(o.standard) && keep) o.limits = keep; if (o.standard === 'Custom') o.standardOther = o.basisOther || b || ''; };
  one(perf, perf.market === 'UL' ? 'UL' : perf.basis);
  Object.values(perf.areas || {}).forEach(o => o && one(o, o.basis));
  return perf;
};
MLP.perfScope = (perf, area) => area && perf.areas && perf.areas[area] && perf.areas[area].enabled ? perf.areas[area] : perf;
/* effective per-class limits for the project or an Area/Group override */
MLP.perfLimits = function (perf, area){
  if (!perf) return null; MLP.perfMigrate(perf);
  const o = MLP.perfScope(perf, area);
  return MLP.perfIsUl(o.standard) ? MLP.perfUlLimits(o.ulConfirmed) : (o.limits || null);
};
MLP.perfStdName = o => o.standard === 'Custom' ? (o.standardOther || 'Custom') : (o.standard || 'not selected');
function perfScopeIssues(o, tag, out){
  if (!o.standard){ out.push(`${tag}Select the referenced standard`); return; }
  if (o.standard === 'Custom' && !String(o.standardOther || '').trim()) out.push(`${tag}Name the custom standard`);
  if (MLP.perfIsUl(o.standard) && !o.ulConfirmed) out.push(`${tag}Engineer must confirm compliance with UL 268, 7th Edition before it is stated`);
  if (!MLP.perfIsUl(o.standard)) MLP.PERF_CLASSES.forEach(c => { const l = (o.limits || {})[c] || {};
    if (!(Number(l.sens) > 0)) out.push(`${tag}${c}: hole sensitivity limit — engineer to define (%obs/ft)`);
    if (!(Number(l.tt) > 0)) out.push(`${tag}${c}: transport-time limit — engineer to define (s)`);
    if (!String(l.ref || '').trim()) out.push(`${tag}${c}: record the reference for these limits`);
    if (!l.confirmed) out.push(`${tag}${c}: engineer must confirm the limits`); });
  (o.codeReqs || []).forEach((r, i) => { const n = `${tag}Code prescription ${i + 1}`;
    if (!String(r.value || '').trim()) out.push(`${n}: engineer to define`);
    if (!String(r.ref || '').trim()) out.push(`${n}: record the reference`);
    if (!r.confirmed) out.push(`${n}: engineer must confirm`); });
}
MLP.perfIssues = function (perf){
  const out = [];
  if (!perf){ out.push('Performance Criteria not defined'); return out; }
  MLP.perfMigrate(perf);
  if (!String(perf.narrative || '').trim()) out.push('Performance narrative is required (align it with the Engineer of Record\'s published intent)');
  else if (!perf.narrativeConfirmed) out.push('Engineer must confirm the performance narrative (auto-drafted from the selections)');
  perfScopeIssues(perf, '', out);
  Object.entries(perf.areas || {}).forEach(([a, o]) => { if (o && o.enabled) perfScopeIssues(o, `Area/Group "${a}" override — `, out); });
  return out;
};
MLP.perfDraft = function (perf, classesUsed){
  if (!perf) return ''; MLP.perfMigrate(perf);
  const L = MLP.perfLimits(perf) || {}; const cls = (classesUsed && classesUsed.length ? classesUsed : MLP.PERF_CLASSES);
  const std = MLP.perfStdName(perf); const ul = MLP.perfIsUl(perf.standard); const fm = (MLP.perfPreset(perf.standard) || {}).family === 'FM';
  const lim = cls.map(c => { const l = L[c] || {}; const t = l.target ?? MLP.SENS_TARGETS[c]; return `${c === 'SFD' ? 'SFD/OAP' : c}: target ${t != null ? t.toFixed(1) : '[engineer to define]'} %obs/ft; every sampling hole at or below ${l.sens ?? '[engineer to define]'} %obs/ft${ul && l.sensMin != null ? ` and not below the UL range lower limit ${l.sensMin} %obs/ft` : ''} with transport time at or below ${l.tt ?? '[engineer to define]'} s${ul && l.ttMin != null ? ` (not below ${l.ttMin} s)` : ''}${ul && l.ulRange ? ` [${l.ulRange}]` : ''}`; }).join('; ');
  const areas = Object.entries(perf.areas || {}).filter(([, o]) => o && o.enabled).map(([a, o]) => `${a} (${MLP.perfStdName(o)})`);
  return `The aspirating smoke detection system is designed to the referenced standard ${std}${perf.specRef ? ' as required by ' + perf.specRef : ''}${ul ? ', applying the UL 268, 7th Edition thresholds (Install Manual App. A, printed p.113: VEWFD Special Application Range 1, EWFD Special Application Range 2 with 1.5 %obs/ft from NFPA 76, SFD/OAP Open Area) plus the code\'s prescriptions' : fm ? ', applying FM requirements only' : ''}. Performance classes used: ${cls.join(', ')}. Design limits — ${lim}.${areas.length ? ' Area/Group overrides: ' + areas.join(', ') + '.' : ''} ${ul ? (perf.ulConfirmed ? MLP.UL_STATEMENT + '.' : 'UL 268, 7th Edition compliance to be confirmed by the engineer.') : 'Limits and references are recorded and confirmed by the engineer.'}${perf.eorName ? ' Engineer of Record: ' + perf.eorName + '.' : ''}`;
};
MLP.perfStatement = perf => { if (!perf) return ''; MLP.perfMigrate(perf); const std = MLP.perfStdName(perf);
  return MLP.perfIsUl(perf.standard) ? (perf.ulConfirmed ? `${MLP.UL_STATEMENT} · Referenced standard: ${std}` : `UL 268, 7th Edition compliance NOT YET CONFIRMED by the engineer · Referenced standard: ${std}`) : `Referenced standard: ${std}${(MLP.perfPreset(perf.standard) || {}).family === 'FM' ? ' (FM requirements; not a UL 268 listing statement)' : ' (engineer-defined limits)'}`; };
/* ---------------- MiniLaser ASD FHSD8075-ULF (1.5.0) ----------------
   Sources: MiniLaser Installation Manual 3103175-EN Rev 001 ("M p.N" = printed page), I/O module datasheet
   K85001-1064 ("DS p.N"), Brent 2026-10-16 decisions (plan-02.01.000-minilaser.md §2, §2.2). Real data only. */
MLP.DETECTOR_TYPES.SOLO = 'MiniLaser';
MLP.KNOWN_KINDS = ['detector', 'display', 'command', 'minilaser', 'asd160'];
MLP.MINILASER = {
  model: 'FHSD8075-ULF',                                   // Brent Q11: this part number only, everywhere
  fanMa: { 1: 120, 2: 134, 3: 157, 4: 180, 5: 200, 6: 230, 7: 255, 8: 285, 9: 320, 10: 365 },   // M p.65 at 24 VDC; standby = alarm (Brent)
  relays: [
    { id: 'r1', label: 'R1 Fault relay (fixed)', fn: 'Fault', fixed: true, failsafe: true },   // fail-safe per Brent Q5
    { id: 'r2', label: 'R2 Relay output 1 (Prealarm)', fn: 'Prealarm' },
    { id: 'r3', label: 'R3 Relay output 2 (Fire Alarm)', fn: 'Fire Alarm' }],
  input: { id: 'in1', label: 'IN1 Supervised input (15 kΩ EOL)', eolOhm: 15000 },            // M p.65, p.18 Table 7
  expansion: { housing: '9-30520', housingDesc: 'MiniLaser Expansion Housing', module: '9-30521', moduleDesc: 'MiniLaser I/O Expansion Module',
    maxModules: 2, outPerModule: 5, inPerModule: 2, outRating: 'latched relay, 2 A @ 30 VDC', inEol: '15 kΩ supervised' },   // DS p.1–2; no draw (Brent; not stated in DS)
  dipFan: [2, 4, 7, 10], dipAlarmFactor: [2, 4, 6, 8],     // M p.28–29: other values need Remote configuration
  remoteOnlyAlarmFactor: [0, 1, 3, 5, 7],                  // M Table 9 note [1]
  /* M p.29 Table 9 */
  table9: { 0: 'Very high · once per year · semiconductor clean room', 1: 'High · once per 5 years · computer room', 2: 'High · once per 10 years · non-smoking office',
    3: 'High · once per 50 years · clean factory', 4: 'Medium · once per 1,000 years · warehouse', 5: 'Medium · once per 5,000 years · warehouse with diesel trucks',
    6: 'Medium · once per 10,000 years · warehouse with diesel trucks', 7: 'Low · once per 20,000 years · warehouse with diesel trucks', 8: 'Low · once per 100,000 years · warehouse with diesel trucks' },
  /* Brent's Alarm Factor Calculator (af-table.xlsx): detector Fire 1 level %obs/ft per alarm factor */
  afFire1: { 8: 0.25, 7: 0.18, 6: 0.12, 5: 0.08, 4: 0.04, 3: 0.03, 2: 0.02, 1: 0.01, 0: 0.005 },
  /* Brent 2026-10-16: more restrictive of UL and NFPA (existing suite rule); UL Open Area 2.18 */
  afThresholds: { VEWFD: 1.0, EWFD: 1.5, SFD: 2.0, OAP: 2.18 },
  /* M p.72 Table 35: hole sensitivity %obs/ft and transport time s per application */
  table35: {
    'UL 268 Ed.7 OAP': { sensMin: 1.70, sensMax: 2.18, ttMin: 6, ttMax: 43 },
    'UL 268 Ed.7 SA Range 1': { sensMin: 0.05, sensMax: 1.00, ttMin: 3, ttMax: 60 },
    'UL 268 Ed.7 SA Range 2': { sensMin: 0.05, sensMax: 2.18, ttMin: 3, ttMax: 43 },
    'ULC-S529': { sensMin: 0.05, sensMax: 1.82, ttMin: 3, ttMax: 100 },
    'FM 3230 VEWFD': { sensMaxExcl: 1.00, ttMaxExcl: 60 },
    'FM 3230 EWFD': { sensMaxExcl: 1.50, ttMaxExcl: 90 },
    'FM 3230 SFD': { sensMaxExcl: 2.50, ttMaxExcl: 120 } },
  /* M p.66 */
  pipe: { maxLenFt: { NFPA: 400, 'UL OAP': 300, 'SA-R1': 300, 'SA-R2': 200, ULC: 400 }, maxHoles: { VEWFD: 10, EWFD: 20, SFD: 35, OAP: 24, 'SA-R1': 25, 'SA-R2': 25, ULC: 35 }, firstHoleFt: 16 },
  /* M p.27 Table 8, p.30 */
  local: { fan: 4, alarmFactor: 4, flowDly: [120, 240], flowLevel: [20, 40], alarmDly: [5, 30] },
  ref: 'MiniLaser Installation Manual 3103175-EN Rev 001'
};
MLP.isMiniLaser = d => !!(d && (d.kind === 'minilaser' || d.type === 'MiniLaser' || d.typeRaw === 'SOLO'));
MLP.miniLaserMa = fan => MLP.MINILASER.fanMa[fan] || 0;
/* Brent Q20/Q21: highest AF whose average hole sensitivity (Fire 1 × holes) ≤ threshold; round toward more sensitive.
   cls: VEWFD | EWFD | SFD | OAP. Returns { af, avg, threshold, cls, fail, steps }. */
MLP.deriveAlarmFactor = function (holes, cls){
  const T = MLP.MINILASER.afThresholds, n = Math.max(0, parseInt(holes, 10) || 0), c = T[cls] != null ? cls : 'SFD', thr = T[c];
  const steps = [];
  for (let af = 8; af >= 0; af--){
    const avg = +(MLP.MINILASER.afFire1[af] * n).toFixed(4); steps.push({ af, avg });
    if (avg <= thr + 1e-9) return { af, avg, threshold: thr, cls: c, holes: n, fail: false, steps };
  }
  return { af: 0, avg: +(MLP.MINILASER.afFire1[0] * n).toFixed(4), threshold: thr, cls: c, holes: n, fail: true, steps,
    msg: `Even alarm factor 0 gives ${(MLP.MINILASER.afFire1[0] * n).toFixed(3)} %obs/ft average hole sensitivity with ${n} holes — over the ${c} limit ${thr}. Use fewer holes or redesign the pipework.` };
};
/* Brent Q22 + 2026-10-16 rule: a MiniLaser is pre-engineered only when the user says so (picker, or the "Pre-engineered" override on an
   imported unit). A .pl import is NON-pre-engineered by default — pre-engineered units need no PipeCAD design — and elbow/tee counts no longer
   decide it. Pre-engineered → DIP (manual ch.5). Otherwise DIP only if fan ∈ {2,4,7,10} AND AF ∈ {2,4,6,8}, else Remote. */
MLP.miniLaserAdvice = function (o){
  const M = MLP.MINILASER, fan = parseInt(o.fan, 10), af = parseInt(o.af, 10);
  const pre = o.preEngineered === true;
  const dipOk = M.dipFan.includes(fan) && M.dipAlarmFactor.includes(af);
  const why = [];
  if (!M.dipFan.includes(fan)) why.push(`fan speed ${isFinite(fan) ? fan : '—'} is not DIP-settable (2/4/7/10)`);
  if (!M.dipAlarmFactor.includes(af)) why.push(`alarm factor ${isFinite(af) ? af : '—'} is not DIP-settable (2/4/6/8)`);
  const method = (pre || dipOk) ? 'DIP' : 'Remote';
  return { preEngineered: pre, method, why, text: method === 'DIP' ? (pre ? 'DIP (pre-engineered layout, manual ch.5)' : 'DIP (fan speed and alarm factor are DIP-settable)') : 'Remote (Remote.exe) — ' + why.join('; ') + ' · not pre-engineered' };
};
/* QA F1: M p.66 pipe limits (MLP.MINILASER.pipe). key = MiniLaser class (VEWFD|EWFD|SFD|OAP) or a Table 35 application name.
   Returns { holesMax, lenMax, holesKey, lenKey } — NFPA classes use the NFPA length (400 ft); UL OAP / SA ranges and ULC use theirs. */
MLP.miniLaserPipeLimits = function (key){
  const P = MLP.MINILASER.pipe, k = String(key || '');
  let hk, lk;
  if (/ULC/.test(k)){ hk = 'ULC'; lk = 'ULC'; }
  else if (/Range 2|SA-R2/.test(k)){ hk = 'SA-R2'; lk = 'SA-R2'; }
  else if (/Range 1|SA-R1/.test(k)){ hk = 'SA-R1'; lk = 'SA-R1'; }
  else if (/OAP/.test(k)){ hk = 'OAP'; lk = 'UL OAP'; }
  else if (/VEWFD/.test(k)){ hk = 'VEWFD'; lk = 'NFPA'; }
  else if (/EWFD/.test(k)){ hk = 'EWFD'; lk = 'NFPA'; }
  else { hk = 'SFD'; lk = 'NFPA'; }
  return { holesMax: P.maxHoles[hk], lenMax: P.maxLenFt[lk], holesKey: hk, lenKey: lk, firstHoleFt: P.firstHoleFt };
};
/* errors[] for holes over the class maximum, pipe longer than allowed, and first hole farther than 16 ft (M ch.5 / p.66).
   firstHoleFt is manual-entry only: the .pl hole records carry no position along the pipe, so no importer supplies it; callers pass it
   only when a user has entered it. (Pre-engineered picker layouts satisfy it by construction.) */
MLP.miniLaserPipeCheck = function (o){
  const L = MLP.miniLaserPipeLimits(o.key), errors = [];
  const h = Number(o.holes), len = Number(o.lengthFt), fh = Number(o.firstHoleFt);
  if (o.holes != null && o.holes !== '' && isFinite(h) && h > L.holesMax) errors.push(`${h} sampling holes exceeds the ${L.holesKey} maximum of ${L.holesMax} holes per pipe (MiniLaser manual p.66)`);
  if (o.lengthFt != null && o.lengthFt !== '' && isFinite(len) && len > L.lenMax + 1e-9) errors.push(`pipe length ${+len.toFixed(1)} ft exceeds the ${L.lenKey} maximum of ${L.lenMax} ft (MiniLaser manual p.66)`);
  if (o.firstHoleFt != null && o.firstHoleFt !== '' && isFinite(fh) && fh > L.firstHoleFt + 1e-9) errors.push(`first sampling hole ${+fh.toFixed(1)} ft from the detector — the manual specifies ${L.firstHoleFt} ft (5 m) (MiniLaser manual ch.5)`);
  return { ok: !errors.length, errors, limits: L };
};
/* M ch.5 pre-engineered tables 13–31. Row: [holes, transport s, AF2, AF4, AF6, AF8, diameters]; AF cell 'value:tags'
   (V VEWFD, E EWFD, S SFD, A SA, O OAP, C ULC) or '' (not offered). Diameters: per branch for T (holes/2), per hole for I. */
(function (){
  const TAG = { V: 'VEWFD', E: 'EWFD', S: 'SFD', A: 'SA', O: 'OAP', C: 'ULC' };
  const X = (s, n) => Array(n).fill(s);
  const T = [
    { shape: 'T', fan: 2, tables: '13–14', page: 50, lengths: [30, 60, 84, 108], rows: [
      [2, 14, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', ['19/64']],
      [4, 30, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', ['9/32', '19/64']],
      [6, 45, '0.12:VAC', '0.24:VAC', '0.72:VAC', '', ['1/4', '17/64', '5/16']],
      [8, 73, '0.17:EC', '0.34:EC', '1.02:EC', '', ['3/16', '3/16', '13/64', '15/64']]] },
    { shape: 'T', fan: 4, tables: '15–16', page: 51, lengths: [30, 60, 84, 108, 132, 156], rows: [
      [2, 18, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', ['11/64']],
      [4, 28, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', X('11/64', 2)],
      [6, 45, '0.12:VAC', '0.24:VAC', '0.72:VAC', '', X('9/64', 3)],
      [8, 63, '0.16:EAC', '0.32:EAC', '0.96:EAC', '', X('1/8', 4)],
      [10, 88, '0.21:EAC', '0.42:EAC', '1.26:EAC', '', X('7/64', 5)],
      [12, 101, '0.25:S', '0.50:S', '1.50:S', '', X('7/64', 6)]] },
    { shape: 'T', fan: 7, tables: '17–18', page: 52, lengths: [30, 60, 84, 108, 132, 156, 180], rows: [
      [2, 15, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', ['9/64']],
      [4, 15, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SA', ['17/64', '9/32']],
      [6, 32, '0.12:VAC', '0.24:VAC', '0.72:VAC', '', X('9/64', 3)],
      [8, 45, '0.16:VAC', '0.32:VAC', '0.96:VAC', '', X('1/8', 4)],
      [10, 62, '0.20:EC', '0.40:EC', '1.20:EC', '', X('7/64', 5)],
      [12, 86, '0.24:EC', '0.48:EC', '1.44:EC', '', X('3/32', 6)],
      [14, 95, '0.29:SC', '0.58:SC', '1.74:SC', '', X('3/32', 7)]] },
    { shape: 'T', fan: 10, tables: '19–20', page: 53, lengths: [30, 60, 84, 108, 132, 156, 180], rows: [
      [2, 14, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', ['5/32']],
      [4, 19, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', X('5/32', 2)],
      [6, 30, '0.12:VAC', '0.24:VAC', '0.72:VAC', '', X('1/8', 3)],
      [8, 43, '0.16:VAC', '0.32:VAC', '0.96:VAC', '', X('7/64', 4)],
      [10, 62, '0.20:EC', '0.40:EC', '1.20:EC', '', X('3/32', 5)],
      [12, 91, '0.24:SC', '0.48:SC', '1.44:SC', '', X('5/64', 6)],
      [14, 99, '0.28:SC', '0.56:SC', '1.68:SC', '', X('5/64', 7)]] },
    { shape: 'I', fan: 2, tables: '21–22', page: 55, lengths: [20, 40, 60, 80, 100, 120, 140, 160, 180, 200], rows: [
      [1, 4, '0.02:VAC', '0.04:VAC', '0.12:VAC', '0.50:VAC', ['7/16']],
      [2, 13, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', X('17/64', 2)],
      [3, 28, '0.06:VAC', '0.12:VAC', '0.36:VAC', '1.50:EAC', X('1/4', 3)],
      [4, 34, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', X('13/64', 4)],
      [5, 53, '0.10:VAC', '0.20:VAC', '0.60:VAC', '2.50:S', X('3/16', 4).concat(['13/64'])],
      [6, 66, '0.13:EC', '0.26:EC', '0.78:EC', '', X('5/32', 5).concat(['11/64'])],
      [7, 75, '0.15:EC', '0.30:EC', '0.90:EC', '', X('5/32', 6).concat(['11/64'])],
      [8, 89, '0.17:EC', '0.34:EC', '1.02:EC', '', X('9/64', 6).concat(X('5/32', 2))],
      [9, 95, '0.20:SC', '0.40:SC', '1.20:SC', '', X('1/8', 6).concat(X('9/64', 2), ['3/16'])],
      [10, 113, '0.23:S', '0.46:S', '1.38:S', '', X('1/8', 7).concat(X('9/64', 2), ['5/32'])]] },
    { shape: 'I', fan: 4, tables: '23–24', page: 56, lengths: [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220], rows: [
      [1, 3, '0.02:VAC', '0.04:VAC', '0.12:VAC', '0.50:VAC', ['7/16']],
      [2, 13, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', X('3/16', 2)],
      [3, 23, '0.06:VAC', '0.12:VAC', '0.36:VAC', '1.50:EAC', X('5/32', 3)],
      [4, 34, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', X('9/64', 4)],
      [5, 46, '0.10:VAC', '0.20:VAC', '0.60:VAC', '2.50:S', X('1/8', 5)],
      [6, 64, '0.12:EC', '0.24:EC', '0.72:EC', '', X('7/64', 6)],
      [7, 77, '0.15:EC', '0.30:EC', '0.90:EC', '', X('3/32', 6).concat(['7/64'])],
      [8, 82, '0.17:EC', '0.34:EC', '1.02:EC', '', X('3/32', 7).concat(['7/64'])],
      [9, 102, '0.19:S', '0.38:S', '1.14:S', '', X('3/32', 8).concat(['7/64'])],
      [10, 105, '0.23:S', '0.46:S', '1.38:S', '', X('3/32', 5).concat(X('7/64', 5))],
      [11, 117, '0.24:S', '0.48:S', '1.44:S', '', ['3/32'].concat(X('7/64', 9), ['1/8'])]] },
    { shape: 'I', fan: 7, tables: '25–26', page: 58, lengths: [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240], rows: [
      [1, 2, '0.02:VAC', '0.04:VAC', '0.12:VAC', '0.50:VAC', ['7/16']],
      [2, 10, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', X('3/16', 2)],
      [3, 25, '0.06:VAC', '0.12:VAC', '0.36:VAC', '1.50:EAC', X('1/8', 3)],
      [4, 37, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', X('7/64', 4)],
      [5, 56, '0.10:VAC', '0.20:VAC', '0.60:VAC', '2.50:S', X('3/32', 5)],
      [6, 60, '0.12:VC', '0.24:VC', '0.72:VC', '', X('3/32', 6)],
      [7, 74, '0.15:EC', '0.30:EC', '0.90:EC', '', X('5/64', 6).concat(['3/32'])],
      [8, 78, '0.17:EC', '0.34:EC', '1.02:EC', '', X('5/64', 7).concat(['3/32'])],
      [9, 83, '0.19:EC', '0.38:EC', '1.14:EC', '', X('5/64', 8).concat(['3/32'])],
      [10, 97, '0.21:S', '0.42:S', '1.26:S', '', X('5/64', 9).concat(['3/32'])],
      [11, 103, '0.26:S', '0.52:S', '1.56:S', '', X('3/32', 3).concat(X('7/64', 8))],
      [12, 111, '0.30:S', '0.60:S', '1.80:S', '', X('5/64', 2).concat(X('3/32', 3), X('7/64', 7))]] },
    { shape: 'I', fan: 10, tables: '27–28', page: 60, lengths: [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300], rows: [
      [1, 2, '0.02:VAC', '0.04:VAC', '0.12:VAC', '0.50:VAC', ['7/16']],
      [2, 8, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', X('3/16', 2)],
      [3, 21, '0.06:VAC', '0.12:VAC', '0.36:VAC', '1.50:EAC', X('1/8', 3)],
      [4, 32, '0.08:VAC', '0.16:VAC', '0.48:VAC', '2.00:SAO', X('7/64', 4)],
      [5, 44, '0.10:VAC', '0.20:VAC', '0.60:VAC', '2.50:S', X('3/32', 5)],
      [6, 68, '0.12:EC', '0.24:EC', '0.72:EC', '', X('5/64', 6)],
      [7, 73, '0.14:EC', '0.28:EC', '0.84:EC', '', X('5/64', 7)],
      [8, 82, '0.16:EC', '0.32:EC', '0.96:EC', '', X('5/64', 8)],
      [9, 90, '0.18:EC', '0.36:EC', '1.08:EC', '', X('5/64', 9)],
      [10, 98, '0.21:SC', '0.42:SC', '1.26:SC', '', X('5/64', 10)],
      [11, 94, '0.24:SC', '0.48:SC', '1.44:SC', '', X('3/32', 11)],
      [12, 105, '0.27:S', '0.54:S', '1.62:S', '', X('3/32', 12)],
      [13, 111, '0.35:S', '0.70:S', '2.10:S', '', X('5/64', 5).concat(X('3/32', 8))],
      [14, 113, '0.32:S', '0.64:S', '1.92:S', '', X('5/64', 2).concat(X('3/32', 2), ['7/64'], X('1/8', 8), ['9/64'])],
      [15, 113, '0.35:S', '0.70:S', '2.10:S', '', X('5/64', 3).concat(['3/32', '7/64'], X('1/8', 8), X('9/64', 2))]] },
    { shape: 'I225', fan: 10, tables: '29–31', page: 62, lengths: Array.from({ length: 25 }, (_, i) => 9 * (i + 1)), rows: [
      [1, 2, '0.02:VAC', '0.04:VAC', '0.12:VAC', '0.50:VAC', ['5/16']],
      [2, 2, '0.04:VAC', '0.08:VAC', '0.24:VAC', '1.00:VAC', ['19/64', '5/16']],
      [3, 3, '0.06:VAC', '0.12:VAC', '0.36:VAC', '1.50:EAC', ['17/64', '19/64', '5/16']],
      [4, 5, '0.09:VAC', '0.18:VAC', '0.54:VAC', '2.25:S', ['15/64', '17/64', '5/16', '5/16']],
      [5, 6, '0.14:VAC', '0.28:VAC', '0.84:VAC', '', ['3/16', '3/16', '3/16', '1/4', '5/16']],
      [6, 8, '0.19:VAC', '0.38:VAC', '1.14:EAC', '', X('3/16', 4).concat(['17/64', '5/16'])],
      [7, 10, '0.21:VAC', '0.42:VAC', '1.26:EAC', '', X('11/64', 4).concat(['7/32', '5/16', '5/16'])],
      [8, 13, '0.26:VAC', '0.52:VAC', '1.56:SAC', '', X('9/64', 4).concat(['13/64'], X('5/16', 3))],
      [9, 16, '0.30:VAC', '0.60:VAC', '1.80:SAC', '', X('9/64', 5).concat(['13/64'], X('5/16', 3))],
      [10, 18, '0.26:VAC', '0.52:VAC', '1.56:SAC', '', ['1/8', '9/64', '9/64', '5/32', '11/64', '3/16', '7/32', '7/32', '15/64', '5/16']],
      [11, 20, '0.30:VAC', '0.60:VAC', '1.80:SAO', '', ['7/64', '1/8', '1/8', '9/64', '5/32', '11/64', '3/16', '13/64', '13/64', '13/64', '5/16']],
      [12, 21, '0.32:VAC', '0.64:VAC', '1.92:SAO', '', X('7/64', 3).concat(['1/8', '9/64', '9/64', '5/32'], X('11/64', 4), ['1/4'])],
      [13, 25, '0.34:VAC', '0.68:VAC', '2.04:SAO', '', ['3/32', '7/64', '7/64', '7/64', '1/8', '9/64', '9/64', '5/32', '11/64', '11/64', '11/64', '3/16', '9/32']],
      [14, 28, '0.38:VAC', '0.76:VAC', '2.28:S', '', ['3/32'].concat(X('7/64', 3), ['1/8', '1/8', '9/64', '5/32', '11/64', '3/16', '3/16', '3/16', '13/64', '5/16'])],
      [15, 31, '0.49:VAC', '0.98:VAC', '', '', ['3/32', '3/32', '7/64', '7/64', '1/8', '1/8', '9/64', '5/32'].concat(X('13/64', 4), ['7/32', '15/64', '5/16'])],
      [16, 34, '0.44:VAC', '0.88:VAC', '', '', X('3/32', 4).concat(['7/64', '7/64', '1/8', '9/64', '5/32', '5/32'], X('11/64', 4), ['3/16', '5/16'])],
      [17, 37, '0.46:VAC', '0.92:VAC', '', '', ['5/64'].concat(X('3/32', 4), ['7/64', '7/64', '1/8', '9/64'], X('5/32', 4), ['11/64', '11/64', '3/16', '5/16'])],
      [18, 36, '0.49:VAC', '0.98:VAC', '', '', X('5/64', 3).concat(X('3/32', 4), ['7/64', '7/64'], X('9/64', 5), ['5/32', '5/32', '5/32', '17/64'])],
      [19, 47, '0.54:VAC', '1.08:EC', '', '', X('5/64', 3).concat(X('3/32', 3), ['7/64', '7/64', '1/8', '9/64', '9/64'], X('5/32', 4), ['11/64', '11/64', '3/16', '5/16'])],
      [20, 47, '0.54:VAC', '1.08:EC', '', '', X('5/64', 4).concat(X('3/32', 4), ['7/64', '1/8'], X('9/64', 5), ['9/64', '5/32', '5/32', '11/64', '5/16'])],
      [21, 52, '0.58:VAC', '1.16:EC', '', '', X('5/64', 5).concat(X('3/32', 3), ['7/64'], X('1/8', 3), X('9/64', 3), X('9/64', 3), ['5/32', '11/64', '5/16'])],
      [22, 52, '0.59:VAC', '1.18:EC', '', '', X('5/64', 6).concat(X('3/32', 3), ['7/64', '1/8', '1/8'], X('9/64', 3), X('9/64', 3), ['5/32', '11/64', '3/16', '5/16'])],
      [23, 58, '0.69:VAC', '1.38:EC', '', '', X('5/64', 7).concat(['3/32', '3/32'], X('7/64', 3), X('1/8', 3), X('1/8', 3), X('9/64', 3), ['5/32', '5/16'])],
      [24, 59, '0.70:VAC', '1.40:EC', '', '', X('5/64', 8).concat(['3/32', '3/32'], X('7/64', 5), X('1/8', 6), ['9/64', '9/64', '5/16'])],
      [25, 59, '0.85:VAC', '1.70:SC', '', '', X('5/64', 9).concat(['3/32', '3/32'], X('7/64', 4), X('7/64', 6), ['1/8', '1/8', '3/16', '5/16'])]] }
  ];
  const cell = s => { if (!s) return null; const [v, t] = s.split(':'); return { avg: Number(v), classes: t.split('').map(c => TAG[c]) }; };
  MLP.MINILASER.preEngineered = T.map(t => ({ shape: t.shape, fan: t.fan, tables: t.tables, page: t.page, rows: t.rows.map(r => {
    const perBranch = t.shape === 'T' ? r[0] / 2 : r[0];
    return { holes: r[0], transport: r[1], af: { 2: cell(r[2]), 4: cell(r[3]), 6: cell(r[4]), 8: cell(r[5]) }, diameters: r[6],
      lengthFt: t.lengths[perBranch - 1], lengthNote: t.shape === 'T' ? 'per branch' : 'total' }; }) }));
})();
MLP.preEngTable = (shape, fan) => MLP.MINILASER.preEngineered.find(t => t.shape === shape && t.fan === +fan) || null;
MLP.preEngLookup = function (shape, fan, holes, af){
  const t = MLP.preEngTable(shape, fan); if (!t) return null;
  const r = t.rows.find(x => x.holes === +holes); if (!r) return null;
  const a = af != null ? r.af[af] : null;
  return { table: t, row: r, af: a, dip: { fan: +fan, alarmFactor: af != null ? +af : null }, cite: `M Tables ${t.tables}, printed p.${t.page}` };
};
/* parsed .pl detector → MiniLaser design fields (Brent Q18/Q20/Q22). cls = intended performance class or null. */
/* Brent-approved (2026-10-16) class order for the alarm-factor rule: Area/Group class → project class → SFD.
   perf = Performance Criteria (perf.standard + optional perf.areas[a] override). Returns { cls, src }. */
MLP.miniLaserClass = function (perf, area){
  const clsOf = id => { const p = MLP.perfPreset(id); return p && p.cls && MLP.MINILASER.afThresholds[p.cls] != null ? p.cls : ''; };
  const a = perf && area && perf.areas && perf.areas[area];
  if (a && a.enabled && clsOf(a.standard)) return { cls: clsOf(a.standard), src: 'area' };
  if (perf && clsOf(perf.standard)) return { cls: clsOf(perf.standard), src: 'project' };
  return { cls: 'SFD', src: 'default SFD' };
};
MLP.miniLaserFromPl = function (rec, cls){
  const p = rec.pipe || {}, holes = (p.holes || []).length;
  const ci = cls && typeof cls === 'object' ? cls : (cls ? { cls, src: 'project' } : { cls: 'SFD', src: 'default SFD' });
  const useCls = MLP.MINILASER.afThresholds[ci.cls] != null ? ci.cls : 'SFD';
  const clsSrc = useCls === ci.cls ? ci.src : 'default SFD';
  let af, afSrc, derivation = null;
  if (p.afActivatedRaw === 'true' && p.af != null){ af = p.af; afSrc = 'pl'; }
  else { derivation = MLP.deriveAlarmFactor(holes, useCls); af = derivation.af; afSrc = 'derived'; }
  const advice = MLP.miniLaserAdvice({ fan: rec.fan, af, preEngineered: false });   // .pl import: non-pre-engineered by default (Brent)
  const pipeCheck = MLP.miniLaserPipeCheck({ key: useCls, holes, lengthFt: p.lengthFt });   // QA F1: M p.66
  return { fan: rec.fan, alarmFactor: af, alarmFactorSrc: afSrc, derivation, perfClass: useCls, perfClassSrc: clsSrc, holes, advice, pipeCheck,
    configMethod: advice.method, expansionInPl: !!p.expansionInPl };
};

/* ======================= 1.6.0: brand catalog (plan rev 4.23b §B3/B4/B5) ======================= */
MLP.BRAND_DEFAULT = 'edwards';
MLP.BRANDS = {
  'edwards': { id: 'edwards', label: 'Edwards', manufacturer: 'Edwards', supplyLabel: 'Edwards A/BPS',
    reportTitle: 'Edwards ModuLaser MASD — Field Report', chip: 'EDWARDS', cabinetDefault: 'edwards' },
  'kidde-commercial': { id: 'kidde-commercial', label: 'Kidde Commercial', manufacturer: 'Kidde Commercial', supplyLabel: 'Kidde Commercial APS/EBPS',
    reportTitle: 'Kidde Commercial ModuLaser MASD — Field Report', chip: 'KIDDE COMMERCIAL', cabinetDefault: 'spaceage' }
};
MLP.brandOf = b => (b && MLP.BRANDS[b]) ? b : MLP.BRAND_DEFAULT;      // missing/unknown → Edwards (old files)
MLP.PARTS = {
  minDisplay: { edwards: 'FHSD8300-ULF', 'kidde-commercial': '9-30780-KID-ULF', desc: 'Minimum Display' },
  stdDisplay: { edwards: 'FHSD8310-ULF', 'kidde-commercial': '9-30781-KID-ULF', desc: 'Standard Display' },
  cmdDisplay: { edwards: 'FHSD8320-ULF', 'kidde-commercial': '9-30782-KID-ULF', desc: 'Command Display' },
  detector:   { edwards: 'FHSD8330-ULF', 'kidde-commercial': '9-30783-KID-ULF', desc: 'Detector Module' },
  minilaser:  { edwards: 'FHSD8075-ULF', 'kidde-commercial': '9-30501-KID-ULF', desc: 'MiniLaser aspirating smoke detector' },
  asd160:     { edwards: 'FHSD8025-7-ULF', 'kidde-commercial': '9-30671-7-KID-ULF', desc: 'ASD-160 aspirating smoke detector (Micra25 / Senator 25)' },
  mlHousing:  { both: '9-30520', desc: 'MiniLaser expansion housing', fixedMfr: '—' },
  mlIo:       { both: '9-30521', desc: 'MiniLaser I/O module', fixedMfr: '—' },
  asdRelay:   { both: '33-30436A', desc: 'ASD-160 relay card (Pre-Alarm, Aux, Fire 2)' },
  tamper:     { both: '3-TAMP', desc: 'Tamper switch' },
  apsEq:      { both: 'APSEQ', desc: 'Seismic kit (APS)' },
  bpsEq:      { both: 'BPSEQ', desc: 'Seismic kit (BPS)' },
  bc1Eq:      { both: 'BC-1EQ', desc: 'Seismic kit (BC-1)' },
  bc1:        { both: 'BC-1', desc: 'Battery cabinet (2 batteries up to 40 Ah)' },
  bc2:        { both: 'BC-2', desc: 'Battery cabinet (up to 17 Ah)' },
  ssu00507:   { both: 'SSU00507', desc: 'Battery cabinet', fixedMfr: 'Space Age Electronics' },
  rcc7r:      { both: '3-RCC7R', desc: 'Battery cabinet', fixedMfr: 'Edwards' },
  bats:       { both: '3-BATS', desc: 'Battery shelf', fixedMfr: 'Edwards' },
  // catalog only — never in a BOM (B3)
  grommets: { both: '9-30794', catalogOnly: true }, angled: { both: '9-30795', catalogOnly: true }, straight: { both: '9-30796', catalogOnly: true },
  filter6: { both: '9-30699N-P', catalogOnly: true }, bpsCvr: { both: 'BPS-CVR', catalogOnly: true }, mnBrkt: { both: 'MN-BRKT3F', catalogOnly: true }
};
MLP.MODULE_PART_KEY = { 'Minimum Display': 'minDisplay', 'Standard Display': 'stdDisplay', 'Command Display': 'cmdDisplay', 'Detector': 'detector' };
MLP.partFor = function (brand, key){ const p = MLP.PARTS[key]; if (!p) return ''; return p.both || p[MLP.brandOf(brand)]; };
MLP.manufacturerFor = function (brand, key){ const p = MLP.PARTS[key]; if (p && p.fixedMfr) return p.fixedMfr; return MLP.BRANDS[MLP.brandOf(brand)].manufacturer; };
/* Translate any brand-catalog P/N to the other brand (used on brand switch and by the Report's part-number basis). */
MLP.translatePart = function (pn, toBrand){
  const s = String(pn || '').trim(); if (!s) return s;
  for (const k of Object.keys(MLP.PARTS)){ const p = MLP.PARTS[k]; if (p.both) continue;
    if (p.edwards === s || p['kidde-commercial'] === s) return p[MLP.brandOf(toBrand)]; }
  for (const fam of ['APS', 'BPS']) for (const a of [6, 10]) for (const v of MLP.SUPPLY_VARIANTS){
    for (const b of Object.keys(MLP.BRANDS)) if (MLP.supplyPart(b, fam, a, v).pn === s) return MLP.supplyPart(toBrand, fam, a, v).pn; }
  return s;
};
MLP.SUPPLY_VARIANTS = ['120', '220', 'ulc'];
MLP.SUPPLY_VARIANT_LABELS = { '120': '120V', '220': '220V', 'ulc': 'ULC' };
/* B4 table. Explicit lookup — replaces supply.replace('6A','10A'). */
MLP.supplyPart = function (brand, family, amps, variant){
  const b = MLP.brandOf(brand), a = Number(amps) === 10 ? 10 : 6, v = MLP.SUPPLY_VARIANTS.indexOf(variant) >= 0 ? variant : '120';
  const fam = String(family || 'BPS').toUpperCase().indexOf('APS') >= 0 ? 'APS' : 'BPS';
  let pn, note = '';
  if (fam === 'APS'){ pn = v === '220' ? `APS${a}A/230` : `APS${a}A`; if (v === 'ulc') note = 'No ULC variant listed'; }
  else pn = v === '220' ? `BPS${a}A/230` : v === 'ulc' ? `BPS${a}AC` : (b === 'kidde-commercial' ? `EBPS${a}A` : `BPS${a}A`);
  return { pn, note, family: fam, amps: a, variant: v, desc: `Power supply (${a} A)` + (v === '120' ? '' : ' ' + MLP.SUPPLY_VARIANT_LABELS[v]) };
};
MLP.supplyCapacityLabel = (brand, amps, variant) => `${MLP.supplyPart(brand, 'APS', amps, variant).pn} / ${MLP.supplyPart(brand, 'BPS', amps, variant).pn}`;
/* Batteries (two per supply). Ah from the catalog, never parsed from the P/N (C5). 12V6A5 manual-only (C1 #58). */
MLP.BATTERIES = {
  '12V6A5': { ah: 7.2, family: 'BPS', fit: 'supply', manualOnly: true },
  '12V10A': { ah: 10.5, family: 'BPS', fit: 'supply' },
  '12V17A': { ah: 18, family: 'APS', fit: 'supply' },
  '12V24A': { ah: 26, family: 'APS', fit: 'supply' },
  '12V40A': { ah: 40, family: 'BPS', fit: 'bc1' },
  '12V50A': { ah: 50, family: 'BPS', fit: 'cabinet' },
  '12V65A': { ah: 65, family: 'BPS', fit: 'cabinet' }
};
MLP.batteries = MLP.BATTERIES;
MLP.BATTERY_SMALL_ADVISORY = '12V6A5 is likely too small for ASD projects';
MLP.KIDDE_DM_NOTICE = 'Ordering requires authorization from the Kidde District Manager first.';
MLP.FACU_ADVISORY = 'FACU powers the ASDs — confirm the FACU power supply and batteries carry this load (not sized here).';
/* Enclosure for a battery: in-supply / BC-1 / cabinet (SSU00507 or 3-RCC7R[+3-BATS]); cabinet default by brand. */
MLP.enclosureFor = function (brand, model, cabinet){
  const bt = MLP.BATTERIES[model]; if (!bt) return null;
  if (bt.fit === 'supply') return { key: null, label: 'None — fits in supply enclosure', parts: [] };
  if (bt.fit === 'bc1') return { key: 'bc1', label: 'BC-1', parts: ['bc1'] };
  const c = cabinet === 'edwards' || cabinet === 'spaceage' ? cabinet : MLP.BRANDS[MLP.brandOf(brand)].cabinetDefault;
  if (c === 'spaceage') return { key: 'spaceage', label: 'SSU00507', parts: ['ssu00507'] };
  return model === '12V65A' ? { key: 'edwards', label: '3-RCC7R + 3-BATS (battery shelf)', parts: ['rcc7r', 'bats'], kiddeDm: MLP.brandOf(brand) === 'kidde-commercial' }
                            : { key: 'edwards', label: '3-RCC7R', parts: ['rcc7r'], kiddeDm: MLP.brandOf(brand) === 'kidde-commercial' };
};
/* Per-supply BOM lines (B5). opts: { brand, battery, amps, family, variant, cabinet, tamper, seismic, supplies } */
MLP.supplyBom = function (o){
  const brand = MLP.brandOf(o.brand), n = o.supplies || 1, out = [], mf = MLP.BRANDS[brand].manufacturer;
  const bt = MLP.BATTERIES[o.battery];
  const fam = o.family || (bt ? bt.family : 'BPS');
  const sp = MLP.supplyPart(brand, fam, o.amps, o.variant);
  out.push({ qty: n, manufacturer: mf, partNumber: sp.pn, description: sp.desc, note: sp.note });
  const enc = bt ? MLP.enclosureFor(brand, o.battery, o.cabinet) : null;
  if (enc) enc.parts.forEach(k => out.push({ qty: n, manufacturer: MLP.manufacturerFor(brand, k), partNumber: MLP.partFor(brand, k), description: MLP.PARTS[k].desc }));
  if (bt) out.push({ qty: 2 * n, manufacturer: mf, partNumber: o.battery, description: `Standby battery, 12 VDC, ${bt.ah} Ah` });
  if (o.tamper) out.push({ qty: n, manufacturer: mf, partNumber: '3-TAMP', description: MLP.PARTS.tamper.desc });
  if (o.seismic){ out.push({ qty: n, manufacturer: mf, partNumber: sp.family === 'APS' ? 'APSEQ' : 'BPSEQ', description: MLP.PARTS[sp.family === 'APS' ? 'apsEq' : 'bpsEq'].desc });
    if (enc && enc.key === 'bc1') out.push({ qty: n, manufacturer: mf, partNumber: 'BC-1EQ', description: MLP.PARTS.bc1Eq.desc }); }
  return out;
};
/* B4a price rule BPS6A + BC-2 → APS6A: ships OFF, prices blank (C1 #52). */
MLP.PRICES = {};
MLP.priceRuleBps6aBc2 = function (){ return null; };

/* ======================= 1.6.0: ASD-160 (Micra25 / Senator 25), kind 'asd160' ======================= */
MLP.ASD160 = { model: 'ASD-160', aliases: ['ASD-160', 'ASD160', 'Micra25', 'MICRA25', 'Senator 25'], ma: 250, voltsMin: 21.6, voltsMax: 26.4,
  ulSens: 1.28, ulTt: 120, ulHoles: 10, ulLengthFt: 160, maxLengthFt: 165, maxTt: 120,
  rangeMin: 0.00914, rangeMax: 7.62, tol: 0.00023, ref: 'Senator 25 Installers Handbook 10-3511-505-SN25-10 REV 010',
  relayBase: ['Fire', 'Fault'], relayCard: ['Pre-Alarm', 'Aux', 'Fire 2'] };
MLP.isAsd160Label = s => /^(asd-?160|micra ?25|senator ?25)$/i.test(String(s || '').trim());
MLP.ASD160_FM_LIMITS = { VEWFD: { sens: 1.00, tt: 60 }, EWFD: { sens: 1.50, tt: 90 }, SFD: { sens: 3.5, tt: 120 } };
MLP.ASD160_LEVELS = [
  { key: 'alert', label: 'Aux', setting: 'E17', list: [10, 9, 8, 7, 6, 5, 4, 3, 2], def: 2 },
  { key: 'action', label: 'Pre-Alarm', setting: 'E16', list: [8, 7, 6, 5, 4, 3], def: 5 },
  { key: 'fire1', label: 'Fire', setting: 'E15', list: [10, 9, 8], def: 10 },
  { key: 'fire2', label: 'Fire 2', setting: null, list: null, def: null }
];
MLP.ASD160_WORKSHEET = "Brent's Alarm Factor Calculator (af-table.xlsx) H12/H13";
MLP.asd160ToM = v => v / 0.3048;
MLP.asd160InRange = v => v != null && isFinite(v) && v >= MLP.ASD160.rangeMin - MLP.ASD160.tol - 1e-12 && v <= MLP.ASD160.rangeMax + MLP.ASD160.tol + 1e-12;
/* §7b trigger (C1 #28/#29): NFPA-family preset, or FM/Custom with ulOptIn. No perf → perfBlank (SFD/OAP – NFPA 72, C1 #30). */
MLP.asd160Scope = function (perf, area){
  const p = perf || MLP.perfBlank(); const s = MLP.perfScope(p, area);
  return { standard: s.standard, ulOptIn: !!s.ulOptIn, limits: s.limits || null, isDefault: !perf, preset: MLP.perfPreset(s.standard) || null };
};
MLP.asd160IsUl = function (perf, area){
  const sc = MLP.asd160Scope(perf, area);
  if (MLP.perfIsUl(sc.standard)) return true;
  const fam = sc.preset && sc.preset.family;
  return !!sc.ulOptIn && (fam === 'FM' || fam === 'Custom');
};
const ASD_CLS_FROM_PRESET = id => /VEWFD/.test(id) ? 'VEWFD' : /EWFD/.test(id) ? 'EWFD' : /SFD|OAP/.test(id) ? 'SFD' : null;
/* Description token (suggestion only) */
MLP.asd160DescHint = function (desc){
  const d = String(desc || '').toUpperCase(), r = {};
  if (/UL ?268/.test(d)) r.standard = 'UL 268'; else if (/FM ?3230/.test(d)) r.standard = 'FM 3230'; else if (/ULC-?S529/.test(d)) r.standard = 'ULC-S529';
  if (/VEWFD/.test(d)) r.cls = 'VEWFD'; else if (/EWFD/.test(d)) r.cls = 'EWFD'; else if (/SFD|STANDARD FIRE|OAP/.test(d)) r.cls = 'SFD';
  return r;
};
/* Class source order (C1 #50): maxTransitTime (exact 60/90/120) → Description hint → user pick. */
MLP.asd160Class = function (pipe, userCls){
  if (userCls) return { cls: userCls, src: 'user' };
  const t = pipe && pipe.maxTransit; const c = (t === 60 || t === 90 || t === 120) ? MLP.TT_TO_CLASS[t] : null;
  if (c) return { cls: c === 'OAP' ? 'SFD' : c, src: `maxTransitTime ${t} s` };
  const h = MLP.asd160DescHint(pipe && pipe.description);
  if (h.cls) return { cls: h.cls, src: 'Description (suggestion)' };
  return { cls: null, src: 'none' };
};
/* R-AF4 / G6a hole counts */
MLP.asd160Holes = function (pipe){
  const holes = (pipe && pipe.holes) || [], tps = (pipe && pipe.testPoints) || [];
  const isTp = h => /test ?point/i.test(h.name || '');
  const sampling = holes.filter(h => !(h.size === 0) && !isTp(h));
  const tpAll = tps.concat(holes.filter(isTp)).filter(h => h.size !== 0);
  return { sampling, testPoints: tpAll, all: holes.length + tps.length };
};
/* §8a transport: field target = longest sampling hole; benchmark = slowest test point (else the field target hole) */
MLP.asd160Transport = function (pipe){
  const h = MLP.asd160Holes(pipe), mx = arr => arr.filter(x => x.tt != null).reduce((a, x) => (!a || x.tt > a.tt) ? x : a, null);
  const tgt = mx(h.sampling), bench = mx(h.testPoints) || tgt;
  return { target: tgt ? tgt.tt : (pipe && pipe.tt != null ? pipe.tt : null), targetHole: tgt ? tgt.i : '', bench: bench ? bench.tt : null, benchHole: bench ? bench.i : '' };
};
/* Limits for this unit's scope (§7b table) */
MLP.asd160Limits = function (perf, area, cls){
  const A = MLP.ASD160, ul = MLP.asd160IsUl(perf, area), sc = MLP.asd160Scope(perf, area);
  if (ul){
    if (MLP.perfIsUl(sc.standard)){ const c = ASD_CLS_FROM_PRESET(sc.standard) || 'SFD', n = MLP.NFPA_LIMITS[c] || {};
      const sens = n.sens != null ? Math.min(A.ulSens, n.sens) : A.ulSens, tt = n.tt != null ? Math.min(A.ulTt, n.tt) : A.ulTt;
      return { ul: true, cls: c, sens, tt, sensBy: sens < A.ulSens ? 'nfpa' : 'ul', ttBy: tt < A.ulTt ? 'nfpa' : 'ul', nfpaRef: c === 'SFD' ? 'NFPA 72' : 'NFPA 76', nfpaCite: n.ref, standard: sc.standard, isDefault: sc.isDefault }; }
    return { ul: true, cls: cls || null, sens: A.ulSens, tt: A.ulTt, sensBy: 'ul', ttBy: 'ul', optIn: true, standard: sc.standard, isDefault: sc.isDefault };
  }
  const fam = sc.preset && sc.preset.family;
  if (fam === 'FM'){ const l = cls && MLP.ASD160_FM_LIMITS[cls]; return { ul: false, fm: true, cls, sens: l ? l.sens : null, tt: l ? l.tt : null, standard: sc.standard }; }
  const ul2 = sc.limits && cls && sc.limits[cls];
  return { ul: false, cls, sens: ul2 && ul2.sens != null ? ul2.sens : null, tt: ul2 && ul2.tt != null ? ul2.tt : null, custom: true, standard: sc.standard };
};
/* R-AF2/R-AF3: AF nearest the .pl sensitivity without exceeding it, then step down until AF × sampling holes ≤ cap. */
MLP.asd160DeriveAf = function (sens, nHoles, cap){
  const t = MLP.MINILASER.afFire1; let af = null;
  for (let a = 8; a >= 0; a--) if (sens == null || t[a] <= sens + 1e-12){ af = a; break; }
  if (af == null) af = 0;
  if (cap != null) while (af > 0 && t[af] * nHoles > cap + 1e-12) af--;
  const fail = cap != null && t[af] * nHoles > cap + 1e-12;
  return { af, fire1: t[af], holeSens: +(t[af] * nHoles).toFixed(4), fail };
};
const r2 = v => v == null ? '—' : (+v).toFixed(v < 0.1 ? 4 : 2).replace(/0+$/, '').replace(/\.$/, '');
/* Full evaluation of one ASD-160 (rec from parsePl, or a device with .pipe). Issues: level 'error' | 'warn' | 'advisory' | 'incomplete'. */
MLP.asd160Evaluate = function (rec, perf, area, opts){
  const A = MLP.ASD160, o = opts || {}, pipe = rec.pipe || {}, issues = [];
  const counts = MLP.asd160Holes(pipe), n = counts.sampling.length;
  const worstH = counts.sampling.filter(h => h.sens != null).reduce((a, h) => (!a || h.sens > a.sens) ? h : a, null);
  const worst = worstH ? worstH.sens : null;
  const cls = MLP.asd160Class(pipe, o.cls);
  const lim = MLP.asd160Limits(perf, area, cls.cls);
  const transport = MLP.asd160Transport(pipe);
  const sens = pipe.designSens;
  const plAf = pipe.af, activated = String(pipe.afActivatedRaw || '').toLowerCase() === 'true';
  let af;
  if (o.af != null && MLP.MINILASER.afFire1[o.af] != null) af = { af: +o.af, src: 'manual', fire1: MLP.MINILASER.afFire1[o.af], fail: lim.sens != null && MLP.MINILASER.afFire1[o.af] * n > lim.sens + 1e-12 };   // 02.02.000: a manual AF on the row is what gets validated
  else if (activated && plAf != null) af = { af: plAf, src: '.pl', fire1: MLP.MINILASER.afFire1[plAf], fail: lim.sens != null && MLP.MINILASER.afFire1[plAf] * n > lim.sens + 1e-12 };
  else { const d = MLP.asd160DeriveAf(sens, n, lim.sens); af = Object.assign(d, { src: 'derived per Brent rule' }); }
  const len = pipe.lengthFt != null ? pipe.lengthFt : null;
  const tt = transport.target;
  const gov = by => by === 'nfpa' ? `UL 268 7th edition / ${lim.nfpaRef}` : 'UL 268 7th edition';
  const rafs = [];
  if (lim.ul){
    const sensName = lim.sensBy === 'nfpa' ? `${lim.nfpaRef} ${lim.cls} ${r2(lim.sens)} %obs/ft` : 'UL 268 7th edition 1.28 %obs/ft';
    const ttName = lim.ttBy === 'nfpa' ? `${lim.nfpaRef} ${lim.cls} ${lim.tt} s` : 'UL 268 7th edition 120 s';
    if (worst != null && worst > lim.sens + 1e-12){ const m = `worst hole ${r2(worst)} %obs/ft exceeds ${sensName}`; issues.push({ level: 'error', msg: m }); rafs.push([lim.sensBy, m]); }
    if (counts.all > A.ulHoles){ const m = `${counts.all} holes incl. end cap exceeds the UL maximum of 10 (Senator 25 Handbook p11)`; issues.push({ level: 'error', msg: m }); rafs.push(['ul', m]); }
    if (len != null && len > A.ulLengthFt){ const m = `pipe length ${r2(len)} ft exceeds the UL 160 ft test length`; issues.push({ level: 'error', msg: m }); rafs.push(['ul', m]); }
    if (tt != null && tt > lim.tt + 1e-9){ const m = `transport ${r2(tt)} s exceeds ${ttName}`; issues.push({ level: 'error', msg: m }); rafs.push([lim.ttBy, m]); }
    if (af.fail){ const m = af.src === 'manual' ? `alarm factor ${af.af} (${af.fire1} × ${n} holes) exceeds ${r2(lim.sens)} %obs/ft — lower the alarm factor` : `even AF 0 (${MLP.MINILASER.afFire1[0]} × ${n} holes) exceeds ${r2(lim.sens)} %obs/ft — use fewer holes or redesign`; issues.push({ level: 'error', msg: m }); rafs.push([lim.sensBy, m]); }
    const h = MLP.asd160DescHint(pipe.description);
    if (h.standard && h.standard !== 'UL 268') rafs.push(['ul', `the .pl Description points to ${h.standard}`]);
    rafs.forEach(([by, m]) => issues.push({ level: 'warn', msg: `This project is set to UL 268 7th edition, but this ASD-160 does not meet ${gov(by)} (Senator 25 Handbook p.vii): ${m}. Redesign, or set the project standard to the one the design follows.` }));
  } else {
    if (sens != null && !MLP.asd160InRange(sens)) issues.push({ level: 'error', msg: `Detector sensitivity ${r2(sens)} %obs/ft (${r2(MLP.asd160ToM(sens))} %obs/m) is outside the ASD-160 range 0.00914–7.62 %obs/ft (Senator 25 Handbook p3)` });
    counts.sampling.forEach(hh => { if (hh.sens != null && hh.sens > A.rangeMax + A.tol + 1e-12) issues.push({ level: 'error', msg: `Hole ${hh.i} sensitivity ${r2(hh.sens)} %obs/ft is above the ASD-160 range 7.62 %obs/ft (Senator 25 Handbook p3)` }); });
    if (tt != null && tt > A.maxTt + 1e-9) issues.push({ level: 'error', msg: `transport ${r2(tt)} s exceeds the ASD-160 maximum 120 s (Senator 25 Handbook p11)` });
    if (!cls.cls) issues.push({ level: 'incomplete', msg: 'Class not stated in the .pl — pick one' });
    else if (lim.sens == null) issues.push({ level: 'incomplete', msg: `No ${cls.cls} limits entered for ${lim.standard || 'this standard'} — enter and confirm them` });
    if (lim.sens != null && worst != null && worst > lim.sens + 1e-12) issues.push({ level: 'error', msg: `worst hole ${r2(worst)} %obs/ft exceeds ${lim.fm ? 'FM' : lim.standard} ${cls.cls} ${r2(lim.sens)} %obs/ft` });
    if (lim.tt != null && tt != null && tt > lim.tt + 1e-9) issues.push({ level: 'error', msg: `transport ${r2(tt)} s exceeds ${lim.fm ? 'FM' : lim.standard} ${cls.cls} ${lim.tt} s` });
    if (af.fail) issues.push({ level: 'error', msg: af.src === 'manual' ? `alarm factor ${af.af} (${af.fire1} × ${n} holes) exceeds the ${cls.cls} limit ${r2(lim.sens)} %obs/ft — lower the alarm factor` : `even AF 0 exceeds the ${cls.cls} limit ${r2(lim.sens)} %obs/ft — use fewer holes or redesign` });
    if (len != null && len > A.maxLengthFt) issues.push({ level: 'warn', msg: `pipe length ${r2(len)} ft exceeds the ASD-160 general maximum 165 ft (still air, Senator 25 Handbook p3)` });
    if (counts.all > A.ulHoles){ const v = MLP.asd160PipecadValid(rec, lim);
      if (v.ok) issues.push({ level: 'advisory', msg: `${counts.all} holes on one pipe run — Senator 25 Handbook p11 says each pipe run 'should not have more than 10 holes (including the end cap hole)'; accepted because the PipeCAD design validates` });
      else issues.push({ level: 'error', msg: `${counts.all} holes on one pipe run and the PipeCAD design does not validate (${v.reason}) — Senator 25 Handbook p11` }); }
  }
  return { af, cls, ul: lim.ul, limits: lim, counts: { sampling: n, all: counts.all }, worst, worstHole: worstH ? worstH.i : '', transport, issues };
};
/* C1 #35 "PipeCAD proves validity" — criteria (1)–(5) */
MLP.asd160PipecadValid = function (rec, lim){
  const p = rec.pipe || {}, h = MLP.asd160Holes(p), tr = MLP.asd160Transport(p);
  if (String(p.resultsValid).toLowerCase() !== 'true') return { ok: false, reason: 'resultsValid is not true' };
  if (!p.hasResults) return { ok: false, reason: 'no PipeCAD results for this detector' };
  if (p.balance == null || p.balanceMinLimit == null || p.balance < p.balanceMinLimit) return { ok: false, reason: 'hole balance below balanceMinLimit' };
  if (h.sampling.some(x => x.sens != null && ((lim && lim.sens != null && x.sens > lim.sens + 1e-12) || !MLP.asd160InRange(x.sens)))) return { ok: false, reason: 'a hole sensitivity exceeds the class limit or detector range' };
  if (tr.target != null && ((p.maxTransit != null && tr.target > p.maxTransit) || (lim && lim.tt != null && tr.target > lim.tt))) return { ok: false, reason: 'transport exceeds maxTransitTime or the class limit' };
  return { ok: true };
};
/* §7d level prefill and checks (Aux/Pre-Alarm/Fire/Fire 2 — detector levels, %obs/ft) */
MLP.asd160ConfigSeed = function (af, settings){
  const s = Object.assign({ fire1: 10, action: 5, alert: 2 }, settings || {}), f1 = MLP.MINILASER.afFire1[af == null ? 0 : af];
  const T = MLP.TYPICAL_DEFAULTS || {}, pick = k => (T[k] != null ? T[k] : (MLP.CONFIG_FIELDS.find(f => f.k === k || f.key === k) || {}).def);
  return { fire1: f1, action: +((s.action / s.fire1) * f1).toFixed(5), alert: +((s.alert / s.fire1) * f1).toFixed(5), fire2: null,
    actionDly: pick('actionDly') != null ? pick('actionDly') : 5, fire1Dly: pick('fire1Dly') != null ? pick('fire1Dly') : 5,
    flowLow: 20, flowHigh: 20, flowDly: 120, seeded: 'worksheet default — verify (' + MLP.ASD160_WORKSHEET + ')' };
};
MLP.asd160ConfigIssues = function (v){
  const out = [], num = x => (x === '' || x == null) ? null : +x;
  const a = num(v.alert), p = num(v.action), f1 = num(v.fire1), f2 = num(v.fire2);
  const seq = [['Aux', a], ['Pre-Alarm', p], ['Fire', f1], ['Fire 2', f2]].filter(x => x[1] != null);
  for (let i = 1; i < seq.length; i++) if (!(seq[i][1] > seq[i - 1][1])) out.push({ level: 'error', msg: `${seq[i][0]} (${seq[i][1]}) must be above ${seq[i - 1][0]} (${seq[i - 1][1]}) — Aux < Pre-Alarm < Fire < Fire 2` });
  if (f2 == null) out.push({ level: 'incomplete', msg: 'Fire 2 not set — enter it (detector level, %obs/ft)' });
  else if (!MLP.asd160InRange(f2)) out.push({ level: 'error', msg: `ASD-160 Fire 2 ${f2} %obs/ft is outside the detector range 0.00914–7.62 (D4 Table 1 p3)` });
  [['actionDly', 'Pre-Alarm delay', 0, 90], ['fire1Dly', 'Fire delay', 0, 90], ['flowLow', 'Flow low', 0, 20], ['flowHigh', 'Flow high', 0, 20], ['flowLow2', 'Flow low 2', 0, 30], ['flowHigh2', 'Flow high 2', 0, 30], ['flowDly', 'Flow fault delay', 0, 240]]
    .forEach(([k, l, lo, hi]) => { const x = num(v[k]); if (x != null && (x < lo || x > hi)) out.push({ level: 'error', msg: `${l} ${x} is outside ${lo}–${hi}` }); });
  return out;
};

root.MLP = MLP;
if (typeof module !== 'undefined' && module.exports) module.exports = MLP;
})(typeof window !== 'undefined' ? window : globalThis);
