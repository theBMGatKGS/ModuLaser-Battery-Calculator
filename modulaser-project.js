/* ModuLaser project file — shared module (modulaser-project.js)
   Used by the ModuLaser Battery Calculator and the ModuLaser MASD Field Report.
   Keep the two repos' copies identical (MLP.VERSION below). No dependencies, no network.

   File: *.mlproj.json  { format:'modulaser-project', schemaVersion:1, ... }
   Ownership: the Battery Calculator owns `design`; the Field Report owns `site`.
   Each app keeps the other app's section as-is and never overwrites it without a diff prompt. */
(function (root) {
'use strict';
const MLP = {};
MLP.VERSION = '1.0.0';
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
  // Fire 1 matches the Table 45 (p.112) per-hole limit and VEWFD Alert the NFPA 76 0.2 %obs/ft stage; flow limits are the
  // manual default (Table 29, 20%). Action, Fire 2 and the delays are typical starting points only — confirm on site.
  VEWFD: { alert: 0.2, action: 0.5, fire1: 1.0, fire2: 2.0, actionDly: 5, fire1Dly: 5, flowLow: 20, flowHigh: 20, flowDly: 60 },
  EWFD:  { alert: 0.5, action: 1.0, fire1: 1.5, fire2: 3.0, actionDly: 5, fire1Dly: 5, flowLow: 20, flowHigh: 20, flowDly: 60 },
  SFD:   { alert: 1.0, action: 1.5, fire1: 2.5, fire2: 5.0, actionDly: 5, fire1Dly: 5, flowLow: 20, flowHigh: 20, flowDly: 60 }
};

/* ---------------- small helpers ---------------- */
function kid(el, tag){ if (!el) return null; for (const c of el.children) if (c.localName === tag || c.tagName === tag) return c; return null; }
function kids(el, tag){ return el ? Array.from(el.children).filter(c => c.localName === tag || c.tagName === tag) : []; }
function txt(el, tag){ const k = kid(el, tag); return k ? k.textContent.trim() : ''; }
function num(el, tag){ const t = txt(el, tag); if (t === '') return null; const n = Number(t); return isFinite(n) ? n : null; }
function num0(el, tag){ const n = num(el, tag); return n == null ? 0 : n; }
function first(el, tag){ const a = kid(el, tag); const c = a && a.children[0]; if (!c) return null; const n = Number(c.textContent); return isFinite(n) ? n : null; }
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
  const pipeProps = kid(rootEl, 'pipeType') ? rootEl : null;
  const projectName = txt(props, 'ProjectName');
  const results = {};
  kids(kid(rootEl, 'resultsDatabase'), 'SavedDatabase').forEach(sd => { results[txt(sd, 'detectorId')] = sd; });
  const out = {
    fileName: fileName || '', version: txt(rootEl, 'pipecadVersion'), unitRaw, imperial,
    unitLabel: imperial ? 'Imperial (ft)' : `Metric (m, unit ${unitRaw || '?'}) — converted to ft`,
    project: { name: projectName || MLP.baseName(fileName), location: txt(props, 'Location'), designer: txt(props, 'Designer'), company: txt(props, 'CompanyName') },
    projectFromFile: !projectName,
    pipe: { innerDiameter: num(rootEl, 'innerDiameter'), outerDiameter: num(rootEl, 'outerDiameter'), material: txt(rootEl, 'material') },
    groups: [], skipped: []
  };
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
          const o = { i: txt(h, 'index'), size: num(h, 'holeSize'), flow: num(h, 'holeFlowRate'), tt: num(h, 'transitTime'), sens: num(h, 'holeSensitivity') };
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

/* ---------------- project document ---------------- */
MLP.blank = function (){
  return { format: MLP.FORMAT, schemaVersion: MLP.SCHEMA_VERSION, savedAt: '', savedBy: null,
    project: { name: '', location: '', designer: '', company: '', building: '', networkNumber: '', preparedBy: '', date: '' },
    design: null, site: null };
};
MLP.isProject = o => !!(o && o.format === MLP.FORMAT && typeof o.schemaVersion === 'number');
MLP.parse = function (text){
  let o; try { o = JSON.parse(text); } catch (e){ throw new Error('Not a JSON file.'); }
  if (!MLP.isProject(o)) throw new Error('Not a ModuLaser project file (format must be “modulaser-project”).');
  if (o.schemaVersion > MLP.SCHEMA_VERSION) throw new Error(`This project file uses schema ${o.schemaVersion}; this app reads up to ${MLP.SCHEMA_VERSION}. Update the app.`);
  return o;
};
MLP.stringify = function (doc, app, rev){
  doc.format = MLP.FORMAT; doc.schemaVersion = MLP.SCHEMA_VERSION; doc.savedAt = new Date().toISOString(); doc.savedBy = { app, rev };
  if (doc.design) doc.design.hash = MLP.designHash(doc.design);
  return JSON.stringify(doc, null, 1);
};
/* hash of the identity-relevant design content (ignores timestamps and calc internals) */
MLP.designHash = function (design){
  if (!design) return '';
  const strip = { psus: (design.psus || []).map(p => [p.id, p.name, p.area, p.location, p.model, p.battery && p.battery.ah, p.battery && p.battery.qty, p.requiredAh]),
    devices: (design.devices || []).map(d => [d.id, d.name, d.type, d.area, d.address, d.psuId, d.fan, d.pl && d.pl.fp]) };
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
  const devices = diffList(oldD && oldD.devices, newD && newD.devices, devFlat, DEV_FIELDS);
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

root.MLP = MLP;
if (typeof module !== 'undefined' && module.exports) module.exports = MLP;
})(typeof window !== 'undefined' ? window : globalThis);
