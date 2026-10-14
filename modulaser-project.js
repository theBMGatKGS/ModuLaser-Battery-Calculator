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
MLP.VERSION = '1.3.0';
MLP.FORMAT = 'modulaser-project';
MLP.SCHEMA_VERSION = 1;
MLP.EXT = '.mlproj.json';
MLP.NAME_MAX = 16;                 // ModuLaser display shows 16 characters, spaces included
MLP.M_TO_FT = 3.28084;
MLP.DETECTOR_TYPES = { MULTISENSE: 'Detector', MODULASER_DETECTOR: 'Detector' };
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
      const rec = { key, ord: di, kind: 'detector', origName: name, typeRaw, type: MLP.DETECTOR_TYPES[typeRaw],
        fan: (fanN >= 1 && fanN <= 16) ? fanN : null, address: txt(d, 'address'), partNumber: txt(d, 'partNumber'),
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
          const o = { i: txt(h, 'index'), size: num(h, 'holeSize'), flow: num(h, 'holeFlowRate'), tt: num(h, 'transitTime'), sens: num(h, 'holeSensitivity') == null ? null : num(h, 'holeSensitivity') * sensScale };
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
    project: { name: '', location: '', designer: '', company: '', building: '', networkNumber: '', preparedBy: '', date: '' },
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
MLP.designHash = function (design){ return design ? 'sha256:' + sha256hex(canon(design, MLP.HASH_DROP)) : ''; };
MLP.siteHash = function (site){ return site ? 'sha256:' + sha256hex(canon(site, ['hash', 'updatedAt'])) : ''; };
MLP.designId = function (design){
  if (!design) return '';
  const strip = { psus: (design.psus || []).map(p => [p.id, p.name, p.area, p.location, p.model, p.battery && p.battery.ah, p.battery && p.battery.qty, p.requiredAh]),
    devices: (design.devices || []).map(d => [d.id, d.name, d.type, d.area, d.address, d.psuId, d.fan, d.pl && d.pl.fp].concat(d.config ? [JSON.stringify(d.config.values || {}), d.config.perfClass || ''] : [])) };
  return fnv(JSON.stringify(strip));
};

/* Build a design section straight from parsed .pl files (Field Report without a calc file).
   PSUs come only from the Battery Calculator; .pl PSU/Battery entries are placement only. */
MLP.designFromPl = function (parsedList, links){
  const devices = [], areas = [];
  parsedList.forEach((pc, fi) => {
    const link = links[fi];
    pc.groups.forEach(g => {
      if (!areas.includes(g.name)) areas.push(g.name);
      g.displays.concat(g.detectors).forEach(d => devices.push(MLP.deviceFromPl(d, g.name, link)));
    });
  });
  return { owner: 'pl-import', rev: '', updatedAt: new Date().toISOString(), plLinks: links, areas, psus: [], devices,
    placement: parsedList.map((pc, fi) => ({ link: links[fi].id, groups: pc.groups.map(g => ({ area: g.name, psus: g.psus, batteries: g.batteries })) })) };
};
MLP.deviceFromPl = function (d, area, link, extra){
  const dev = { id: (link ? link.id : 'pl') + '|' + d.key, kind: d.kind, type: d.type, partNumber: d.partNumber || '',
    model: d.kind === 'display' ? MLP.DISPLAY_MODELS[d.type] || '' : 'FHSD8330',
    name: d.origName, plName: d.origName, area, address: '', psuId: '', fan: d.fan || null, cluster: '',
    pos: { x: +(d.x || 0).toFixed(2), y: +(d.y || 0).toFixed(2), z: +(d.z || 0).toFixed(2) },
    pl: link ? { link: link.id, file: link.name, key: d.key, fp: d.fp } : null, pipe: d.pipe || null };
  return Object.assign(dev, extra || {});
};
MLP.linkFromParsed = function (pc, sha, size, lastModified){
  return { id: 'pl-' + String(sha).slice(0, 12), name: pc.fileName, sha256: sha, size: size || null, lastModified: lastModified || null,
    version: pc.version, unit: pc.unitLabel, project: pc.project.name, groups: pc.groups.map(g => g.name), importedAt: new Date().toISOString() };
};

/* ---------------- validation ---------------- */
MLP.validateDesign = function (design){
  const issues = [];
  if (!design) return issues;
  const byAddr = {};
  (design.devices || []).forEach(d => {
    if (!MLP.nameOk(d.name)) issues.push({ id: d.id, level: 'error', msg: `“${d.name}” is ${MLP.nameLen(d.name)} characters — the ModuLaser display shows ${MLP.NAME_MAX}.` });
    const a = String(d.address == null ? '' : d.address).trim();
    if (a && a !== '0'){ (byAddr[a] = byAddr[a] || []).push(d); const n = Number(a); if (!(n >= 1 && n <= 127)) issues.push({ id: d.id, level: 'error', msg: `${d.name}: address ${a} is outside 1–127.` }); }
  });
  Object.entries(byAddr).forEach(([a, list]) => { if (list.length > 1) list.forEach(d => issues.push({ id: d.id, level: 'error', msg: `Address ${a} is used by ${list.map(x => x.name).join(', ')}.` })); });
  return issues;
};

/* ---------------- diff ----------------
   Compares two design sections. Returns {project:[], psus:{added,removed,changed}, devices:{added,removed,changed}, count}. */
const DEV_FIELDS = [['name', 'Name'], ['type', 'Type'], ['area', 'Area/Group'], ['address', 'Address'], ['psuId', 'Power supply'], ['fan', 'Fan speed'], ['cluster', 'Cluster'], ['model', 'Model'], ['pipeTT', 'PipeCAD transport time (s)'], ['pipeHoles', 'Sampling holes'], ['pipeLen', 'Pipe length (ft)'], ['af', 'Alarm Factor']];
const PSU_FIELDS = [['name', 'Name'], ['area', 'Area/Group'], ['location', 'Location'], ['model', 'Model'], ['batteryModel', 'Battery'], ['batteryAh', 'Battery Ah'], ['batteryQty', 'Battery qty'], ['requiredAh', 'Required Ah'], ['standbyHours', 'Standby (h)'], ['alarmMinutes', 'Alarm (min)'], ['status', 'Calculator result']];
function devFlat(d){ const p = d.pipe || {}; return { name: d.name, type: d.type, area: d.area, address: d.address || '', psuId: d.psuId || '', fan: d.fan == null ? '' : String(d.fan), cluster: d.cluster || '', model: d.model || '',
  pipeTT: p.tt == null ? '' : (+p.tt).toFixed(1), pipeHoles: p.holes ? String(p.holes.length) : '', pipeLen: p.lengthFt == null ? '' : (+p.lengthFt).toFixed(1), af: p.af == null ? '' : String(p.af) }; }
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
  const keys = ['name', 'location', 'designer', 'company', 'building', 'networkNumber'];
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
MLP.UL_LIMITS = { VEWFD: { sens: 1.0, tt: 60, sensMin: 0.05, ttMin: 3 }, EWFD: { sens: 1.5, tt: 43, sensMin: 0.05, ttMin: 3 }, SFD: { sens: 2.18, tt: 43, sensMin: 1.70, ttMin: 6 } };   // SFD = SFD/OAP
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
MLP.perfScopeInit = (o, id) => { o.standard = id; o.ulConfirmed = false; o.limits = MLP.perfPresetLimits(id); o.codeReqs = MLP.perfCodeReqs(id); return o; };
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
root.MLP = MLP;
if (typeof module !== 'undefined' && module.exports) module.exports = MLP;
})(typeof window !== 'undefined' ? window : globalThis);
