// 02.02.001 (Brent 2026-10-20): SFD/OAP design target — defaults, overrides, rejection, Fire 1 seed, reference/initials, older projects.
// Shared engine test: identical copy in the Toolbox, Calculator and Report (modulaser-project.js must be byte-identical).
const path = require('path'), fs = require('fs'); const M = require(path.join(__dirname, '..', 'modulaser-project.js'));
let pass = 0, fail = 0; const t = (n, c) => { c ? pass++ : fail++; console.log((c ? 'PASS ' : 'FAIL ') + n); };
const ok = { ref: 'Spec 28 31 00 2.4.B', initials: 'BW' };
// defaults
const P = M.perfBlank();
t('UL default target 2.0 (SFD/OAP – NFPA 72)', M.sfdTarget(P, '').value === 2.0 && M.sfdTarget(P, '').family === 'UL' && M.perfLimits(P).SFD.target === 2.0);
t('UL pass/fail unchanged: 1.70–2.18 %obs/ft, ≤43 s', M.perfLimits(P).SFD.sens === 2.18 && M.perfLimits(P).SFD.sensMin === 1.7 && M.perfLimits(P).SFD.tt === 43 && M.sensPass(2.18, M.perfLimits(P).SFD) && !M.sensPass(2.19, M.perfLimits(P).SFD));
const F = M.perfScopeInit({ areas: {}, sfdSchema: 1 }, 'SFD – FM DS 5-48');
t('FM default target 2.5, FM pass/fail 2.50/120 unchanged', M.sfdTarget(F, '').value === 2.5 && M.perfLimits(F).SFD.target === 2.5 && M.FM_LIMITS.SFD.sens === 2.5 && M.FM_LIMITS.SFD.tt === 120);
const C = M.perfScopeInit({ areas: {}, sfdSchema: 1 }, 'Custom');
t('other (Custom/BS) target stays 2.5 and is not adjustable', M.sfdTarget(C, '').value === 2.5 && !M.sfdTargetSet(C, '', 2.4, ok).ok);
t('SENS_TARGETS VEWFD/EWFD unchanged', M.SENS_TARGETS.VEWFD === 1.0 && M.SENS_TARGETS.EWFD === 1.5);
// project-wide set + rejection
t('UL 1.90 without reference rejected with a message', (r => !r.ok && /reference/.test(r.msg))(M.sfdTargetSet(P, '', 1.9, {})) && !P.sfdTarget);
t('UL 1.90 without initials rejected', (r => !r.ok && /initials/.test(r.msg))(M.sfdTargetSet(P, '', 1.9, { ref: 'x' })) && !P.sfdTarget);
t('UL 2.19 rejected (above ModuLaser 2.18), not clamped', (r => !r.ok && /2\.19.*1\.70–2\.18/.test(r.msg))(M.sfdTargetSet(P, '', 2.19, ok)) && !P.sfdTarget);
t('UL 1.69 rejected (below 1.70)', !M.sfdTargetSet(P, '', 1.69, ok).ok && !P.sfdTarget);
t('non-numeric and 3-decimal input rejected', !M.sfdTargetSet(P, '', 'abc', ok).ok && !M.sfdTargetSet(P, '', '1.955', ok).ok && !M.sfdTargetSet(P, '', '', ok).ok);
t('UL bounds 1.70 and 2.18 accepted', M.sfdTargetSet(P, '', 1.70, ok).ok && M.sfdTargetSet(P, '', 2.18, ok).ok);
t('UL 1.90 with reference + initials saved project-wide', M.sfdTargetSet(P, '', '1.90', { ref: 'EOR letter 10/20', initials: 'bw' }).ok && P.sfdTarget.value === 1.9 && P.sfdTarget.initials === 'BW' && M.perfLimits(P).SFD.target === 1.9 && M.perfLimits(P).SFD.sens === 2.18);
t('a rejected entry leaves the saved value untouched', !M.sfdTargetSet(P, '', 2.5, ok).ok && P.sfdTarget.value === 1.9);
t('default value needs no reference; returns to default', M.sfdTargetSet(P, '', 2.0, {}).ok && !P.sfdTarget && M.sfdTarget(P, '').src === 'default');
t('FM 2.6 rejected (above FM 3230 2.50); FM 2.2 with ref saved', !M.sfdTargetSet(F, '', 2.6, ok).ok && M.sfdTargetSet(F, '', 2.2, ok).ok && M.sfdTarget(F, '').value === 2.2);
t('ASD-160 present: not in the UL envelope (1.28 cap governs), 2.0 accepted', M.sfdCheck(2.0, 'UL', ['detector', 'asd160']).ok && /1\.28/.test(M.sfdEnvelope('UL', ['asd160']).text));
t('ASD-160 limits unchanged by a project target (UL 1.28)', (() => { const Q = M.perfBlank(); M.sfdTargetSet(Q, '', 1.8, ok); return M.asd160Limits(Q, '', 'SFD').sens === 1.28; })());
t('MiniLaser envelope applies (UL 1.70–2.18, FM ≤2.50)', !M.sfdCheck(2.2, 'UL', ['minilaser']).ok && M.sfdCheck(2.5, 'FM', ['minilaser']).ok && !M.sfdCheck(2.51, 'FM', ['minilaser']).ok);
// overrides
const Q = M.perfBlank(); M.sfdTargetSet(Q, '', 1.9, ok);
Q.areas = { Hall: { enabled: true }, Store: { enabled: true }, Off: { enabled: false } };
M.perfScopeInit(Q.areas.Hall, 'SFD/OAP – NFPA 72'); M.perfScopeInit(Q.areas.Store, 'SFD – FM DS 5-48'); M.perfScopeInit(Q.areas.Off, 'SFD – FM DS 5-48');
t('UL Area inherits the project UL target', M.sfdTarget(Q, 'Hall').value === 1.9 && M.sfdTarget(Q, 'Hall').src === 'project');
t('FM Area does not inherit a UL target (FM default 2.5)', M.sfdTarget(Q, 'Store').value === 2.5 && M.sfdTarget(Q, 'Store').family === 'FM');
t('Area override 2.1 saved and validated separately', M.sfdTargetSet(Q, 'Hall', 2.1, { ref: 'Hall spec', initials: 'JD' }).ok && M.sfdTarget(Q, 'Hall').value === 2.1 && M.sfdTarget(Q, 'Hall').src === 'area' && M.sfdTarget(Q, '').value === 1.9);
t('Area override out of range rejected', !M.sfdTargetSet(Q, 'Store', 2.7, ok).ok && !Q.areas.Store.sfdTarget);
t('disabled Area rejected', !M.sfdTargetSet(Q, 'Off', 2.2, ok).ok);
t('changing a scope standard clears its target', (M.perfScopeInit(Q.areas.Hall, 'SFD – FM DS 5-48'), !Q.areas.Hall.sfdTarget && M.sfdTarget(Q, 'Hall').value === 2.5));
// Fire 1 seed
const S = M.perfBlank();
t('Fire 1 seed on UL project = target (2.0 default)', M.configSeed('SFD', 'detector', S, '').values.fire1 === 2.0 && M.configSeed('SFD', 'detector', S, '').src.fire1 === 'design');
M.sfdTargetSet(S, '', 1.85, ok);
t('Fire 1 seed follows a set UL target (1.85)', M.configSeed('SFD', 'detector', S, '').values.fire1 === 1.85);
t('Fire 1 seed on FM project stays 2.5', M.configSeed('SFD', 'detector', F, '').values.fire1 === 2.5);
t('Fire 1 seed without a project (Calculator path) stays 2.5', M.configSeed('SFD', 'detector').values.fire1 === 2.5);
S.areas = { A: { enabled: true } }; M.perfScopeInit(S.areas.A, 'SFD – FM DS 5-48');
t('Fire 1 seed in an FM Area of a UL project stays 2.5', M.configSeed('SFD', 'detector', S, 'A').values.fire1 === 2.5);
t('VEWFD/EWFD seeds unchanged', M.configSeed('VEWFD', 'detector', S, '').values.fire1 === 1.0 && M.configSeed('EWFD', 'detector', S, '').values.fire1 === 1.5);
// reference/initials audit of stored values
const H = M.perfBlank(); H.sfdTarget = { value: 1.9, ref: '', initials: '', family: 'UL' };
t('stored non-default without ref/initials is flagged (blocks export)', M.sfdTargetIssues(H).some(i => /reference and the engineer's initials/.test(i)) && M.perfIssues(H).some(i => /SFD\/OAP target/.test(i)));
H.sfdTarget = { value: 2.4, ref: 'x', initials: 'BW', family: 'UL' };
t('stored out-of-range is flagged, never clamped', M.sfdTargetIssues(H).some(i => /outside/.test(i)) && M.sfdTarget(H, '').value === 2.4);
H.sfdTarget = { value: 2.1, ref: 'x', initials: 'BW', family: 'UL' };
t('stored 2.10 is valid for ModuLaser and MiniLaser (no issue)', M.sfdTargetIssues(H, ['detector', 'minilaser']).length === 0);
t('narrative prints the target (two decimals kept)', (M.sfdTargetSet(H, '', 1.95, ok), /SFD\/OAP: target 1\.95 %obs\/ft/.test(M.perfDraft(H, ['SFD']))));
// older projects
const old = { standard: 'SFD/OAP – NFPA 72', ulConfirmed: true, areas: {}, limits: {}, codeReqs: [] };
const L0 = M.perfLimits(old);
t('older project loads: adopts 2.0, one-time notice flagged, no stored target', old.sfdSchema === 1 && old.sfdNotice === true && !old.sfdTarget && L0.SFD.target === 2.0 && L0.SFD.sens === 2.18);
t('notice not raised again after acknowledgment', (old.sfdNotice = false, M.perfMigrate(old), old.sfdNotice === false));
const legacy = { market: 'UL', limits: {} }; M.perfMigrate(legacy);
t('1.2.0 draft (market/basis) migrates and adopts 2.0', legacy.standard === 'SFD/OAP – NFPA 72' && M.sfdTarget(legacy, '').value === 2.0 && legacy.sfdNotice === true);
t('new project raises no notice', M.perfBlank().sfdNotice !== true);
const fmOld = { standard: 'EWFD – FM DS 5-32', areas: {}, limits: M.perfPresetLimits('EWFD – FM DS 5-32'), codeReqs: [] };
t('older FM project adopts 2.5', M.perfLimits(fmOld).SFD.target === 2.5);
t('no pass/fail regression: UL_RANGES.SFD 1.70–2.18, MiniLaser table35 OAP 1.70–2.18, afThresholds unchanged', M.UL_RANGES.SFD.sensMin === 1.7 && M.UL_RANGES.SFD.sensMax === 2.18 && M.MINILASER.table35['UL 268 Ed.7 OAP'].sensMax === 2.18 && M.MINILASER.afThresholds.OAP === 2.18 && M.MINILASER.afThresholds.SFD === 2.0);
// shared copies identical (whichever repo this runs in)
const me = fs.readFileSync(path.join(__dirname, '..', 'modulaser-project.js'), 'utf8');
const others = ['/workspace/MASD-Engineering-Toolbox', '/workspace/ModuLaser-Battery-Calculator', '/workspace/ModuLaser-Commisioning-Report'].map(r => path.join(r, 'modulaser-project.js')).filter(f => fs.existsSync(f));
t('modulaser-project.js byte-identical across Toolbox, Calculator, Report', others.every(f => fs.readFileSync(f, 'utf8') === me));
console.log(`\n${pass} passed, ${fail} failed`); process.exit(fail ? 1 : 0);
