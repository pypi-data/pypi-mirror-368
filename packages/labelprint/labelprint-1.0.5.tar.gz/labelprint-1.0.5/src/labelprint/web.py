#LabelPrint by Pecacheu; MIT License

import json, time, os
import subprocess as sp
from threading import Timer
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.chromium.options import ChromiumOptions
from pycolorutils.color import *

#--- Global WebDriver ---

Options = {
	'timeout': 120, 'engine': "Edge",
	'opts': None, 'headless': True,
	'silent': False
}

_GetPerf = ("let n=new URL({}).pathname,l=[],p=performance.getEntries(),"
	"i=p.length-1; for(; i>=0; --i) try {{if(new URL(p[i].name)"
	".pathname===n) return p[i]}} catch(e){{}}")

#Override Popen for Selenium
def newStart(*args, **kwargs):
	defaultPopen = sp.Popen
	def popen(*args, **kwargs):
		if os.name == 'nt': #Windows
			kwargs['creationflags'] = sp.CREATE_NEW_PROCESS_GROUP
		else: #Linux
			kwargs['process_group'] = 0
		return defaultPopen(*args, **kwargs)

	sp.Popen = popen
	try: newStart.defaultStart(*args, **kwargs)
	finally: sp.Popen = defaultPopen

newStart.defaultStart = webdriver.common.service.Service.start
webdriver.common.service.Service.start = newStart

class ProxyDriver:
	def __init__(self):
		self.drv = self.tmr = None

	def _start(self):
		if self.tmr: self.tmr.cancel(); self.tmr=None
		if self.drv is False: raise BlockingIOError("WebDriver busy")
		if self.drv: return
		self.drv = False
		opt = Options['opts'] or getattr(webdriver, Options['engine']+'Options', ChromiumOptions)()
		if Options['headless']: opt.arguments.append("--headless")
		state = {
			'recentDestinations':[{'id':"Save as PDF", 'origin':"local", 'account':""}],
			'selectedDestinationId':"Save as PDF", 'version':2
		}
		prefs = {'printing.print_preview_sticky_settings.appState':json.dumps(state)}
		opt.add_experimental_option('prefs', prefs)
		opt.add_experimental_option('excludeSwitches', ['enable-logging'])
		try:
			self.drv = getattr(webdriver, Options['engine'])(opt)
		except AttributeError:
			self.drv = ChromiumDriver(opt, browser_name=Options['engine'])

	def _chkRdy(self):
		if self.tmr or not self.drv:
			raise AssertionError("WebDriver not in ready mode")

	def get(self, uri, timeout):
		self._chkRdy()
		st=time.monotonic(); self.drv.get(uri)
		while time.monotonic()-st < timeout:
			pf = self.drv.execute_script(_GetPerf.format(json.dumps(uri)))
			if not pf: continue
			res = pf['responseStatus']
			if res != 200: raise ConnectionError(res)
			return res
		raise TimeoutError(uri)

	def execute_script(self, script, *args):
		self._chkRdy()
		return self.drv.execute_script(script, *args)

	def execute_cdp_cmd(self, cmd, args):
		self._chkRdy()
		return self.drv.execute_cdp_cmd(cmd, args)

	def stop(self, force=False):
		if self.tmr: self.tmr.cancel(); self.tmr=None
		if force:
			d=self.drv; self.drv=False
			if d:
				if not Options['silent']:
					msg(C.Di+"[Shutting down WebDriver in background]")
				d.quit()
				if not Options['silent']:
					msg(C.Di+"[WebDriver stopped]")
				self.drv = None
		elif self.drv:
			self.tmr = Timer(Options['timeout'], self.stop, [True])
			self.tmr.start()

_Drv: ProxyDriver|None = None

def getDriver():
	global _Drv
	if not _Drv: _Drv = ProxyDriver()
	_Drv._start()
	return _Drv

def _exit():
	if _Drv: _Drv.stop(True)

atexit(_exit)