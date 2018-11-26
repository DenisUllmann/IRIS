import os
from pathlib import Path

inpmargin = 8
parpoolnb = 4

hmargin = 0
lmargin = 0
timeseq = 10
hseq = 20
lseq = 20;


parent = Path(os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))).parent

downsize = False
ds_ratio = 1
doInp = True
loadInp = False
loadm = False
loadmc = False
loadM = False
loadDCTCV = False
writeImH = True
writeOrgCV = True
writeInpCV = True
writeMcInpCV = True
writeMInpCV = True
writeOrgDCT = True
writeInpDCT = True
writeMcInpDCT = True
writeMInpDCT = True
writeFrames = True
videoOriDCT = True
videoOriCV = True
videoInpDCT = True
videoInpCV = True
loadGP = False
writeOrgGP = True
writeInpGP = True
writeFrames2 = True
videoOriGP = True
videoInpGP = True

