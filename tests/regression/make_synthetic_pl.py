"""Synthetic PipeCAD-style .pl fixtures for the regression suites (same approach as make_nfpa318_pl.py).

synthetic_pl_specs.json holds numbers-only layout skeletons: detector types, fan speeds, hole sizes / flows /
sensitivities / transit times, pipe geometry on an arbitrary origin, PSU / battery / display counts. It holds no
names, addresses, file paths, labels, outlines or project properties. This script adds fictional names
(Example-*, "Example Engineer", "Example Co.") and writes the .pl files to the external fixture folder at test time.
Never commit generated .pl files.

  Example-Campus-PSU.pl       1 area, 3 ModuLaser detectors, 2 PSUs + 2 batteries in the file
  Example-Tunnel-5Area.pl     5 areas, 9 ModuLaser detectors
  Example-Deck-14Area.pl      14 areas, 88 ModuLaser detectors, 5 displays, no pipe network (lone detectors -> Unassigned tray)
  Example-Warehouse-OAP.pl    1 area, 4 ModuLaser detectors
  Example-Shaft-MiniLaser.pl  1 MiniLaser (SOLO), fan 6, 8 holes, PipeCAD results
  Example-Shaft-ASD160.pl     1 ASD-160 (MICRA25), 8 holes, PipeCAD results
  Example-EN54-Metric.pl      metric (unit 0) file, 2 ModuLaser detectors with hole data (EN 54-20 work)
"""
import os, sys, json
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = json.load(open(os.path.join(HERE, 'synthetic_pl_specs.json')))
DEFAULT_DIR = '/workspace/plbuild/t'
AREA_WORDS = 'Alpha Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliet Kilo Lima Mike November Oscar Papa'.split()   # distinct initials per area
def _xml(spec):
    cnt = {}
    def name_for(parent):
        cnt[parent] = cnt.get(parent, 0) + 1; n = cnt[parent]
        if parent == 'Detector': return f'Det {n:02d}'
        if parent == 'Piperun': return f'Pipe {n}'
        if parent == 'pipeType': return 'Example Pipe'
        return f'{parent} {n}'
    nfloors = json.dumps(spec['tree']).count('"@name:Floor"')
    def emit(node, ind):
        tag, at, body = node
        a = ''.join(f' xsi:{k}="{escape(v)}"' for k, v in at.items())
        if tag == 'PipeLayout':
            a += ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        pad = '  ' * ind
        if isinstance(body, list):
            inner = [emit(c, ind + 1) for c in body]
            if tag == 'PipeLayout':
                inner.insert(0, f"""{pad}  <properties>
{pad}    <FileName>{escape(spec['file'])}</FileName>
{pad}    <Location>{escape(spec['project'])}</Location>
{pad}    <Designer>Example Engineer</Designer>
{pad}    <CompanyName>Example Co.</CompanyName>
{pad}    <ProjectName>{escape(spec['project'])}</ProjectName>
{pad}  </properties>
{pad}  <pipecadVersion>0.0.0-example</pipecadVersion>""")
            return f'{pad}<{tag}{a}>\n' + '\n'.join(inner) + f'\n{pad}</{tag}>'
        if body == '@exhaust': body = 'Exhaust Pipe'
        elif isinstance(body, str) and body.startswith('@name:'):
            p = body[6:]
            if p == 'Floor':
                cnt['Floor'] = cnt.get('Floor', 0) + 1
                body = spec['floor'] if nfloors == 1 else f"{spec['floor']} {AREA_WORDS[cnt['Floor'] - 1]}"
            else: body = name_for(p)
        return f'{pad}<{tag}{a}>{escape(body)}</{tag}>' if body != '' else f'{pad}<{tag}{a} />'
    return '<?xml version="1.0" encoding="utf-8"?>\n' + emit(spec['tree'], 0) + '\n'
def ensure(key, folder=DEFAULT_DIR):
    spec = SPECS[key]; os.makedirs(folder, exist_ok=True); p = os.path.join(folder, spec['file'])
    s = _xml(spec)
    if not os.path.exists(p) or open(p).read() != s: open(p, 'w').write(s)
    return p
def ensure_all(folder=DEFAULT_DIR, keys=None):
    return {k: ensure(k, folder) for k in (keys or SPECS)}
FILE = {k: v['file'] for k, v in SPECS.items()}
if __name__ == '__main__':
    for k, p in ensure_all(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR).items(): print(k, p)
