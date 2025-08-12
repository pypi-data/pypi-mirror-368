#LabelPrint by Pecacheu; MIT License

import json, base64
from io import BytesIO
import inspect as ins
from os import path
from PIL.Image import Image
from selenium.common import TimeoutException
import win32print as wprint
from pycolorutils.color import *
from .web import *

try: from ghostscript import Ghostscript as Gs
except RuntimeError:
	err("Ghostscript is not installed.\nPlease install the 64-bit"
		" version from https://ghostscript.com/releases/gsdnld",9)

#--- Label Generator ---

#Load label.js
_dir = path.dirname(path.abspath(ins.getfile(ins.currentframe())))
_ljs = path.join(_dir, "label.js")
with open(_ljs,'r') as f: _ljs = f.read()

def make(html, outfile=None, data=None):
	if not data: data={}
	drv = getDriver()
	try:
		#Encode PIL images
		for k in data:
			d=data[k]
			if isinstance(d, Image):
				fp=BytesIO(); d.save(fp, "png")
				fp.seek(0); d=fp.read(); fp.close()
				data[k] = "data:image/png;base64,"+base64.b64encode(d).decode('utf8')
		#Export PDF
		drv.get(f"file://{html}", 5)
		try:
			r=drv.execute_script(f"{_ljs}\nreturn await lblData({json.dumps(data)})")
			if r != 'lbl': raise AssertionError("Bad script return value")
		except TimeoutException: raise TimeoutError("Failed to load script")
		pdf = drv.execute_cdp_cmd('Page.printToPDF', {
			'printBackground':True, 'preferCSSPageSize':True
		})
		pdf = base64.b64decode(pdf['data'])
		if not outfile: return pdf
		if isinstance(outfile, str):
			with open(outfile,'wb') as f: f.write(pdf)
		else: outfile.write(pdf)
	finally:
		drv.stop()

#--- Printer Support ---

def getPrinters():
	pl = wprint.EnumPrinters(wprint.PRINTER_ENUM_NAME, None, 2)
	for p in pl: p['Offline'] = p['Attributes'] & wprint.PRINTER_ATTRIBUTE_WORK_OFFLINE
	return pl

OptsToDM = {
	'width':'PaperWidth', 'length':'PaperLength', 'size':'PaperSize',
	'orientation':'Orientation', 'dpi':'PrintQuality', 'dpiX':'PrintQuality',
	'dpiY':'YResolution', 'color':'Color', 'scale':'Scale', 'copies':'Copies'
}

def printPDF(fn, ptrName, opts=None):
	if opts is None: opts = {}
	p = wprint.OpenPrinter(ptrName)
	try:
		#Defaults
		dm = wprint.GetPrinter(p, 2)['pDevMode']
		dm.Copies = 1; dm.Color = 1; dm.Scale = 100
		#Set Opts
		for k,o in OptsToDM.items():
			if k in opts:
				v = opts[k]
				if k == 'orientation': v = 2 if v == 'landscape' else 1
				else: v = int(v)
				if k == 'dpi': dm.YResolution = v
				dm.__setattr__(o,v)
		wprint.SetPrinter(p, 9, {'pDevMode':dm}, 0)
	finally:
		wprint.ClosePrinter(p)

	Gs("gs", "-q", "-dBATCH", "-dNOSAFER", "-dNOPAUSE", "-dNOPROMPT",
		"-dPDFFitPage", "-dHWMargins=0 0 0 0", "-sDEVICE=mswinpr2",
		f"-sOutputFile=%printer%{ptrName}", fn)