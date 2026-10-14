/* =====================================================================
   MASD ENGINE — shared calculation + PipeCAD .pl import
   Used byte-for-byte by the ModuLaser Battery Calculator and the
   MASD Engineering Toolbox. Harmonization rule: any change here bumps
   MASD_ENGINE_VERSION and the revision of BOTH apps, with matching
   Revision-log notes that name the engine version.
   ===================================================================== */
const MASD_ENGINE_VERSION = '1.0.0';
const MASD_ENGINE = {
  version: MASD_ENGINE_VERSION,
  /* BS 5839-1 Annex E: D = 1 when the battery 20-hour rate (Ah / 20) meets the alarm current, else 1.75. */
  bs5839D(batteryAh, totalMa){ return (batteryAh > 0 && (batteryAh / 20) >= (totalMa / 1000)) ? 1 : 1.75; },
  /* NFPA 72 minimum safety margin by edition: 20 % (2019 and earlier) / 25 % (2022 and later). */
  marginMinimum(edition){ return edition === '2019minus' ? 0.20 : 0.25; },
  temperatureMultiplier(t){ return TEMPERATURE_MULTIPLIERS[parseInt(t)] || 1.0; },
  /* Standby Ah = I × T_standby; Alarm Ah = I × T_alarm × D; Required = (Standby + Alarm) × (1 + margin) × temperature. */
  batteryAh({ standbyHours, alarmMinutes, totalMa, derating = 1, margin = 0, temperatureF = 77 }){
    const standbyAh = standbyHours * (totalMa / 1000);
    const alarmAh = ((alarmMinutes / 60) * (totalMa / 1000)) * derating;
    const initialAh = standbyAh + alarmAh;
    const tempMultiplier = this.temperatureMultiplier(temperatureF);
    return { standbyAh, alarmAh, initialAh, marginAh: initialAh * (1 + margin), tempMultiplier, requiredAh: initialAh * (1 + margin) * tempMultiplier };
  },
  /* Per-group estimate used by the arrangement suggestions (no derating or temperature, as before). */
  groupAh({ standbyHours, alarmMinutes, totalMa, margin = 0 }){
    return ((standbyHours * (totalMa / 1000)) + ((alarmMinutes / 60) * (totalMa / 1000))) * (1 + margin);
  },
  suppliesRequired(requiredAh, sizeAh){ return sizeAh > 0 ? Math.max(1, Math.ceil(requiredAh / sizeAh)) : 1; },
  detectorMa(fan, psuVolts){ return (psuVolts === 18 ? FAN_SPEED_MA_18V : FAN_SPEED_MA)[fan] || 0; }
};

/* ---------------- reference data ---------------- */
const MODULE_TYPES = {
  "Minimum Display":  { model: "FHSD8300-ULF", kind: "display", ma: 210 },
  "Standard Display": { model: "FHSD8310-ULF", kind: "display", ma: 232 },
  "Command Display":  { model: "FHSD8320-ULF", kind: "command", ma: 232 },
  "Detector":         { model: "FHSD8330-ULF", kind: "detector", ma: null }
};
const FAN_SPEED_MA = {1:218,2:234,3:255,4:279,5:301,6:330,7:363,8:393,9:431,10:471,11:506,12:552,13:602,14:646,15:712,16:762};
// 18V reference figures from the manufacturer's current-draw worksheet, for the Help menu's
// reference table only — not used in any calculation (the calculator's own math always uses
// FAN_SPEED_MA above). Does not match either the 18.0V or 20.4V rows exactly in every case;
// see the Help menu's Module Current Draw Reference for the documented sourcing.
const FAN_SPEED_MA_18V = {1:250,2:279,3:305,4:330,5:358,6:380,7:430,8:465,9:517,10:566,11:615,12:685,13:733,14:786,15:872,16:1021};

const QUIESCENT_MA = 70;
const AUX_MA_PER_CIRCUIT = 35;
const MAX_AUX_BUILTIN = 4;
const CHARGER_MAX_AH = 65;
const DEFAULT_SAFETY_MARGIN = 0.25;
const DESIGN_BASIS_PRESETS = {
  "NFPA 72 Standard": { standby: 24, alarm: 5, formula: "standard",
    citation: "NFPA 72 (2022 Edition), Section 10.6.7.2 — secondary power supply capacity for standard (non-voice) protected premises fire alarm systems (10.6.7.2.1: 24-hour minimum standby under quiescent load)." },
  "NFPA 72 Voice": { standby: 24, alarm: 15, formula: "standard",
    citation: "NFPA 72 (2022 Edition), Section 10.6.7.2 — secondary power supply capacity for systems with in-building fire emergency voice/alarm communications (10.6.7.2.1: 24-hour minimum standby under quiescent load)." },
  "NFPA 72 + NFPA 110 Generator Backup (Non-Voice)": { standby: 4, alarm: 5, formula: "standard",
    citation: "NFPA 72 (2022 Edition), Section 10.6.7.2 — 4-hour standby permitted where secondary power is provided by an automatic-starting, engine-driven generator meeting NFPA 110 (Type 10, Class 24, Level 1) with the entire power path qualifying as NFPA 70 Article 700 emergency power. If any part of the downstream distribution does not qualify, the full 24-hour battery standby applies regardless." },
  "NFPA 72 + NFPA 110 Generator Backup (Voice)": { standby: 4, alarm: 15, formula: "standard",
    citation: "NFPA 72 (2022 Edition), Section 10.6.7.2 — 4-hour standby permitted where secondary power is provided by an automatic-starting, engine-driven generator meeting NFPA 110 (Type 10, Class 24, Level 1) with the entire power path qualifying as NFPA 70 Article 700 emergency power. If any part of the downstream distribution does not qualify, the full 24-hour battery standby applies regardless." },
  "UFC 3-600-01 Hydro (Voice Evacuation)": { standby: 24, alarm: 15, formula: "standard",
    citation: "UFC 3-600-01, Fire Protection Engineering for Facilities (8 August 2016, w/ Change 6 dated 6 May 2021), Paragraph 4-24.7 — Hydroelectric Power Plant voice evacuation requirements, following NFPA 72 in-building fire alarm voice evacuation secondary power provisions." },
  "UFC 3-600-01 FA/MNS": { standby: 48, alarm: 15, formula: "standard",
    citation: "UFC 3-600-01, Fire Protection Engineering for Facilities (8 August 2016, w/ Change 6 dated 6 May 2021), Paragraph 9-18.11.3 — Fire Alarm and Mass Notification System secondary power capacity." },
  "AWS": { standby: 24, alarm: 120, formula: "standard",
    citation: "Complies with AWS specification 283116, 25H1B — NFPA 72 (2022 Edition), Section 10.6.7.2 secondary power capacity requirements, with an Owner-specified enhanced 120-minute alarm period in place of the 5/15-minute code minimum. Also compliant with NFPA 855." },
  "CAN/ULC-S524:2024 Standard": { standby: 24, alarm: 5, formula: "standard", fixedMargin: 0.25,
    citation: "CAN/ULC-S524:2024, Standard for the Installation of Fire Alarm Systems — secondary (battery) power capacity for 24-hour standby plus 5 minutes of alarm operation, with the 1.25 safety factor introduced in the 2024 edition." },
  "CAN/ULC-S524:2024 Voice": { standby: 24, alarm: 15, formula: "standard", fixedMargin: 0.25,
    citation: "CAN/ULC-S524:2024, Standard for the Installation of Fire Alarm Systems — secondary (battery) power capacity for 24-hour standby plus 15 minutes of alarm operation where voice communication is installed, with the 1.25 safety factor introduced in the 2024 edition." },
  "BS 5839-1 Category M/L": { standby: 24, alarm: 30, formula: "bs5839", derating: 1.75,
    citation: "BS 5839-1:2025, Annex E — Category M (Manual) or L (Life Safety) system secondary power capacity." },
  "BS 5839-1 Category M/L + Generator": { standby: 6, alarm: 30, formula: "bs5839", derating: 1.75,
    citation: "BS 5839-1:2025, Annex E — Category M/L system secondary power capacity where an automatic-starting generator serves as secondary power." },
  "BS 5839-1 Category P (Staffed)": { standby: 24, alarm: 30, formula: "bs5839", derating: 1.75,
    citation: "BS 5839-1:2025, Annex E — Category P (staffed / ARC-monitored premises) secondary power capacity." },
  "BS 5839-1 Category P (Unstaffed)": { standby: 24, alarm: 30, formula: "bs5839", derating: 1.75, editableStandby: true, maxStandby: 72,
    citation: "BS 5839-1:2025, Annex E — Category P (unstaffed premises) secondary power capacity: 24 hours plus the unoccupied period, up to a maximum of 72 hours total standby." }
};
const TEMPERATURE_MULTIPLIERS = { 77: 1.00, 68: 1.04, 50: 1.14, 32: 1.30, 14: 1.61 };


const BATTERY_SIZE_OPTIONS = [10, 12, 18, 26, 40, 50, 65];
const BATTERY_MODELS = [
  { model: "12V10A", ah: 10.5, supply: "BPS6A", enclosure: "None — fits in supply enclosure", cls: "good" },
  { model: "12V17A", ah: 18,   supply: "APS6A", enclosure: "None — fits in supply enclosure", cls: "good" },
  { model: "12V24A", ah: 26,   supply: "APS6A", enclosure: "None — fits in supply enclosure", cls: "good" },
  { model: "12V40A", ah: 40,   supply: "BPS6A", enclosure: "BC-1", cls: "good" },
  { model: "12V50A", ah: 50,   supply: "BPS6A", enclosure: "SSU00507", cls: "good",
    cabinetOptions: [
      { value: "edwards", label: "Edwards 3-RCC7R", enclosure: "3-RCC7R" },
      { value: "spaceage", label: "Space Age SSU00507", enclosure: "SSU00507" }
    ] },
  { model: "12V65A", ah: 65,   supply: "BPS6A", enclosure: "SSU00507", cls: "good",
    cabinetOptions: [
      { value: "edwards", label: "Edwards 3-RCC7R with 3-BATS (battery shelf)", enclosure: "3-RCC7R + 3-BATS (battery shelf)" },
      { value: "spaceage", label: "Space Age SSU00507", enclosure: "SSU00507" }
    ] }
];
const MAX_DETECTORS_PER_CLUSTER = 8;
const MAX_COMMAND_DISPLAYS = 2;
const MAX_MODULES_PER_NETWORK = 127;
const MAX_DISPLAYS_PER_NETWORK = 63;
function pad2(n){ return String(n).padStart(2, "0"); }

// Resolves a desired/required Ah value to the next-larger available battery model (never smaller)
function pickBatteryModel(requiredAh){
  for (const b of BATTERY_MODELS) if (b.ah >= requiredAh) return b;
  return null;
}
function hardwareFromModel(batteryModel, capacity, cabinetChoice){
  if (!batteryModel){
    return { supply: null, enclosure: null, batteryPart: null, cls: "danger", error: `Exceeds largest available battery model (12V65A, 65 Ah) — add power supplies or reduce battery size` };
  }
  const supplyName = (capacity === 10) ? batteryModel.supply.replace('6A', '10A') : batteryModel.supply;
  let enclosureLabel = batteryModel.enclosure;
  if (batteryModel.cabinetOptions){
    const chosen = batteryModel.cabinetOptions.find(o => o.value === cabinetChoice) || batteryModel.cabinetOptions[0];
    enclosureLabel = chosen.enclosure;
  }
  return {
    supply: supplyName,
    enclosure: enclosureLabel,
    batteryPart: `2 × ${batteryModel.model} per ${supplyName}${enclosureLabel.indexOf("None") !== 0 ? " (" + enclosureLabel + ")" : ""} — ${batteryModel.ah} Ah rated`,
    cls: batteryModel.cls,
    cabinetOptions: batteryModel.cabinetOptions || null
  };
}


/* ---------- PipeCAD .pl import: constants ---------- */
const PL_NAME_MAX = 16;
const PL_CLUSTER_FT = 3;
const PL_MAX_DET_PER_PSU = 4;
const PL_MAX_DISP_PER_PSU = 1;
const PL_DETECTOR_TYPES = { MULTISENSE: 'Detector', MODULASER_DETECTOR: 'Detector' };
const PL_DISPLAY_PARTS = { '0': 'Standard Display', '1': 'Minimum Display', '2': 'Command Display' };
const PL_M_TO_FT = 3.28084;

function plKid(el, tag){ if (!el) return null; for (const c of el.children) if (c.tagName === tag) return c; return null; }
function plTxt(el, tag){ const k = plKid(el, tag); return k ? k.textContent.trim() : ''; }
function plNum(el, tag){ const v = parseFloat(plTxt(el, tag)); return isFinite(v) ? v : 0; }
function plFnv(str){ let h = 0x811c9dc5; for (let i = 0; i < str.length; i++){ h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h.toString(16).padStart(8, '0'); }
async function plSha256(text){
  try {
    if (window.crypto && crypto.subtle){
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
      return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
    }
  } catch (e){}
  return 'fnv-' + plFnv(text);
}

function plBaseName(n){ return String(n || '').replace(/^.*[\\/]/, '').replace(/\.pl$/i, ''); }

/* ---------- parser ---------- */
function plParse(text, fileName){
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  if (doc.getElementsByTagName('parsererror').length) throw new Error('Not a valid PipeCAD .pl (XML) file.');
  const root = doc.documentElement;
  if (!root || root.tagName !== 'PipeLayout') throw new Error('Not a PipeCAD project (no <PipeLayout> root).');
  const props = plKid(root, 'properties');
  const unitRaw = plTxt(root, 'unit');
  const imperial = unitRaw === '1';
  const scale = imperial ? 1 : PL_M_TO_FT;
  const projectName = plTxt(props, 'ProjectName');
  const out = {
    fileName, projectName, project: projectName || plBaseName(fileName),
    projectFromFile: !projectName,
    unitRaw, unitLabel: imperial ? 'Imperial (ft)' : `Metric (m, unit ${unitRaw || '?'}) — converted to ft`,
    version: plTxt(root, 'pipecadVersion'), groups: [], skipped: []
  };
  const floorDb = plKid(root, 'floorDatabase');
  const floors = floorDb ? Array.from(floorDb.children).filter(c => c.tagName === 'Floor') : [];
  floors.forEach((fl, gi) => {
    const gname = plTxt(fl, 'name') || `Area ${gi + 1}`;
    const g = { idx: gi, origName: gname, name: gname, include: true, detectors: [], displays: [], psus: [] };
    const seen = {};
    const ddb = plKid(fl, 'detectorDatabase');
    (ddb ? Array.from(ddb.children).filter(c => c.tagName === 'Detector') : []).forEach((d, di) => {
      const name = plTxt(d, 'name') || `Detector ${di + 1}`;
      const typeRaw = plTxt(d, 'type');
      const idTxt = plTxt(d, 'id');
      let key = `${gname}#${idTxt !== '' ? 'id' + idTxt : 'n' + name}`;
      if (seen[key]) key += '~' + (++seen[key]); else seen[key] = 1;
      const fan = parseInt(plTxt(d, 'aspiratorSpeed'), 10);
      const rec = { key, ord: di, kind: 'detector', origName: name, typeRaw,
        type: PL_DETECTOR_TYPES[typeRaw], fan: (fan >= 1 && fan <= 16) ? fan : null,
        address: plTxt(d, 'address'),
        x: plNum(d, 'startX') * scale, y: plNum(d, 'startY') * scale, z: plNum(d, 'startZ') * scale };
      rec.fp = plFnv([rec.origName, rec.typeRaw, rec.fan, rec.x.toFixed(2), rec.y.toFixed(2)].join('|'));
      if (!rec.type){ out.skipped.push(`${gname}: “${name}” has unknown type “${typeRaw || 'blank'}” — skipped`); return; }
      g.detectors.push(rec);
    });
    const disDb = plKid(fl, 'displayDatabase');
    (disDb ? Array.from(disDb.children).filter(c => c.tagName === 'Display') : []).forEach((d, i) => {
      const pn = plTxt(d, 'partNumber');
      const type = PL_DISPLAY_PARTS[pn];
      if (!type){ out.skipped.push(`${gname}: display ${i + 1} has unknown partNumber “${pn}” — skipped`); return; }
      g.displays.push({ key: `${gname}#disp${i}`, ord: i, kind: 'display', origName: `${type} ${i + 1}`, type, partNumber: pn,
        x: plNum(d, 'startX') * scale, y: plNum(d, 'startY') * scale, z: plNum(d, 'startZ') * scale,
        fp: plFnv([pn, plNum(d,'startX'), plNum(d,'startY')].join('|')) });
    });
    const psuDb = plKid(fl, 'psuDatabase');
    (psuDb ? Array.from(psuDb.children).filter(c => c.tagName === 'PSU') : []).forEach(p => {
      g.psus.push({ x: plNum(p, 'startX') * scale, y: plNum(p, 'startY') * scale });
    });
    out.groups.push(g);
  });
  return out;
}

/* ---------- battery math (mirrors recalcLocationInner, Edwards A/BPS, 1 AUX circuit) ---------- */
function plDeviceMa(dev){
  if (dev.kind === 'display') return (MODULE_TYPES[dev.type] || {}).ma || 0;
  return FAN_SPEED_MA[dev.fan] || FAN_SPEED_MA[16];
}
function plRequiredAh(devices, s){
  const set = s || plWiz.settings;
  if (!devices.length) return 0;
  const preset = DESIGN_BASIS_PRESETS[set.designBasis] || {};
  const devMa = devices.reduce((a, d) => a + plDeviceMa(d), 0);
  const totalMa = devMa + (set.mode === 'thirdparty' ? 0 : QUIESCENT_MA + AUX_MA_PER_CIRCUIT);
  const d = preset.formula === 'bs5839' ? (preset.derating || 1.75) : 1;
  const margin = preset.formula === 'bs5839' ? 0.25 : (preset.fixedMargin !== undefined ? preset.fixedMargin : parseFloat(set.margin));
  return MASD_ENGINE.batteryAh({ standbyHours: parseFloat(set.standbyHours) || 0, alarmMinutes: parseFloat(set.alarmMinutes) || 0, totalMa, derating: d, margin, temperatureF: set.temperature }).requiredAh;
}
function plPsuCheck(psu){
  const dets = psu.devices.filter(d => d.kind === 'detector').length;
  const disp = psu.devices.filter(d => d.kind === 'display').length;
  const ah = plRequiredAh(psu.devices);
  const v = [];
  if (dets > PL_MAX_DET_PER_PSU) v.push(`${dets} detectors — max ${PL_MAX_DET_PER_PSU} per power supply`);
  if (disp > PL_MAX_DISP_PER_PSU) v.push(`${disp} displays — max ${PL_MAX_DISP_PER_PSU} per power supply`);
  if (ah > CHARGER_MAX_AH) v.push(`${ah.toFixed(1)} Ah required — over the ${CHARGER_MAX_AH} Ah charger limit`);
  return { dets, disp, ah, violations: v };
}
function plFits(devs){
  const dets = devs.filter(d => d.kind === 'detector').length, disp = devs.filter(d => d.kind === 'display').length;
  return dets <= PL_MAX_DET_PER_PSU && disp <= PL_MAX_DISP_PER_PSU && plRequiredAh(devs) <= CHARGER_MAX_AH;
}
const plDist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

/* ---------- PSU suggestion ---------- */
function plSplitByDistance(devs){
  // Greedy: seed with the left-/bottom-most device, grow with nearest-neighbour while rules allow.
  const rest = devs.slice().sort((a, b) => a.x - b.x || a.y - b.y);
  const groups = [];
  while (rest.length){
    const cur = [rest.shift()];
    let grew = true;
    while (grew && rest.length){
      grew = false;
      let best = -1, bestD = Infinity;
      rest.forEach((d, i) => {
        const dd = Math.min(...cur.map(c => plDist(c, d)));
        if (dd < bestD && plFits(cur.concat([d]))){ bestD = dd; best = i; }
      });
      if (best >= 0){ cur.push(rest.splice(best, 1)[0]); grew = true; }
    }
    groups.push(cur);
  }
  return groups;
}
function plClusterDevices(devs){
  // Single-linkage clusters of devices within 3 ft (plan view X/Y).
  const n = devs.length, parent = devs.map((_, i) => i);
  const find = i => parent[i] === i ? i : (parent[i] = find(parent[i]));
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++)
    if (plDist(devs[i], devs[j]) <= PL_CLUSTER_FT) parent[find(i)] = find(j);
  const map = {};
  devs.forEach((d, i) => { (map[find(i)] = map[find(i)] || []).push(d); });
  const out = [];
  Object.values(map).forEach(c => { if (plFits(c)) out.push(c); else plSplitByDistance(c).forEach(s => out.push(s)); });
  return out;
}
function plSuggestForGroup(g, devs){
  const psus = [];
  let left = devs.slice();
  if (g.psus.length){
    g.psus.forEach((p, i) => psus.push({ id: 'p' + Math.random().toString(36).slice(2, 8), seed: p, fromFile: true, devices: [] }));
    const pairs = [];
    left.forEach(d => psus.forEach(p => pairs.push({ d, p, dist: plDist(d, p.seed) })));
    pairs.sort((a, b) => a.dist - b.dist);
    const placed = new Set();
    pairs.forEach(({ d, p }) => {
      if (placed.has(d.key)) return;
      if (plFits(p.devices.concat([d]))){ p.devices.push(d); placed.add(d.key); }
    });
    left = left.filter(d => !placed.has(d.key));
  }
  // Only real 3 ft clusters (2+ devices) are pre-suggested; lone devices go to the Unassigned tray for the user to group.
  const unassigned = [];
  plClusterDevices(left).forEach(c => {
    if (c.length > 1) psus.push({ id: 'p' + Math.random().toString(36).slice(2, 8), devices: c });
    else unassigned.push(...c);
  });
  const out = psus.filter(p => p.devices.length || p.fromFile);
  out.unassigned = unassigned;
  return out;
}

