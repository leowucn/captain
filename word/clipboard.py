# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
import urllib


class ClipboardWatcher:
	def __init__(self, pause=5.):
		self._pause = pause

	def watcher(self):
		last_result = ''
		while True:
			result = pyperclip.paste()
			word_list = re.compile('\w+').findall(result)
			if len(word_list) > 0:
				if last_result != '' and result.find(last_result) >= 0 and len(result) > len(last_result):
					# in this case, result might be a sentence containing the corresponding last-result which was supposed to be a word or phrase.
					# legal sentence
					word = tackle_word.TackleWords()
					m = word.query(last_result, result)
					last_result = ''
				else:
					if len(word_list) < 4:  # this may be a word or regular phrase
						last_result = result.strip()
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


#if __name__ == "__main__":
try_times = 0
while True:
	ok = test_network()
	if ok:
		clip = ClipboardWatcher()
		clip.watcher()
	time.sleep(60)
	try_times += 1
	if try_times == 10:
		break

