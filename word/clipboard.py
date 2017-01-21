# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
import urllib
from time import gmtime, strftime

class ClipboardWatcher:
	def __init__(self, pause=3):
		self._pause = pause

	def watcher(self):
		last_result = ''
		while True:
			result = pyperclip.paste().strip()
			word_list = re.compile('\w+').findall(result)
			if len(word_list) > 0:
				if last_result != '' and result.find(last_result) >= 0 and len(result) > len(last_result):
					# in this case, result might be a sentence containing the corresponding last-result which was supposed to be a word or phrase.
					# legal sentence
					tackle = tackle_word.TackleWords()
					tackle.query(last_result + '-1', result, strftime("%Y-%m-%d", gmtime()))
					last_result = ''
				else:
					if len(word_list) < 4:  # this may be a word or regular phrase
						last_result = result
					else:
						last_result = ''
			else:
				last_result = ''
			time.sleep(self._pause)


def test_network():
	code = urllib.urlopen("http://dict.youdao.com/").getcode()
	if code != 200:
		return False
	return True

clip = ClipboardWatcher()
clip.watcher()

