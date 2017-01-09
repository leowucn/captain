# -*- coding:utf-8 -*-
import time
import pyperclip


class ClipboardWatcher:
	def __init__(self, callback, pause=5.):
		self._callback = callback
		self._pause = pause
		self._stopping = False
		self.clipboard_content = ''

	def watcher(self):
		while not self._stopping:
			self.clipboard_content = pyperclip.paste()
			time.sleep(self._pause)

	def stop(self):
		self._stopping = True

