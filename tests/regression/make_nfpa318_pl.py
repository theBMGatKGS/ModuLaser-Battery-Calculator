"""Synthetic PipeCAD-style .pl fixture: 'NFPA318-Fab-Ceiling.pl' (NFPA 318 fab ceiling, 6 detectors, 1 display).
Written from the importer's schema (same approach as the Example-Tower.pl generator). All names, coordinates and
fan speeds are fictional; nothing is taken from any real project file. Written to the external fixture folder at
test time; never commit generated .pl files."""
import os, sys
NAME = 'NFPA318-Fab-Ceiling.pl'
# (id, name, fan, x, y) -- fab-ceiling return-air zone: 4 bay detectors on a 1 ft pitch plus a 2-detector chase cluster
DETS = [(0,'FC Bay 1 RA',14,20,40),(1,'FC Bay 2 RA',6,21,40),(2,'FC Bay 3 RA',6,22,40),
        (3,'FC Bay 4 RA',5,23,40),(4,'FC Chase N',9,40,60),(5,'FC Chase S',9,41,60)]
DISPLAY = (1, 19.5, 39.5)   # partNumber 1 = Minimum Display
def xml():
    d = '\n'.join(f"        <Detector><id>{i}</id><name>{n}</name><type>MULTISENSE</type><aspiratorSpeed>{f}</aspiratorSpeed>"
                  f"<address></address><startX>{x}</startX><startY>{y}</startY><startZ>14</startZ></Detector>" for i,n,f,x,y in DETS)
    pn, dx, dy = DISPLAY
    return f"""<?xml version="1.0" encoding="utf-8"?>
<PipeLayout>
  <properties>
    <FileName>{NAME}</FileName>
    <Location>NFPA 318 Fab Ceiling</Location>
    <Designer>Example Engineer</Designer>
    <CompanyName>Example Co.</CompanyName>
    <ProjectName>NFPA 318 Fab Ceiling</ProjectName>
  </properties>
  <pipecadVersion>0.0.0-example</pipecadVersion>
  <unit>1</unit>
  <floorDatabase>
    <Floor>
      <name>Fab Ceiling RA</name>
      <detectorDatabase>
{d}
      </detectorDatabase>
      <displayDatabase>
        <Display><partNumber>{pn}</partNumber><startX>{dx}</startX><startY>{dy}</startY><startZ>5</startZ></Display>
      </displayDatabase>
      <psuDatabase />
    </Floor>
  </floorDatabase>
</PipeLayout>
"""
def ensure(folder):
    os.makedirs(folder, exist_ok=True); p = os.path.join(folder, NAME)
    s = xml()
    if not os.path.exists(p) or open(p).read() != s: open(p, 'w').write(s)
    return p
if __name__ == '__main__': print(ensure(sys.argv[1] if len(sys.argv) > 1 else '/workspace/plbuild/t'))
