# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word


class ClipboardWatcher:
	def __init__(self, pause=5.):
		self._pause = pause

	def watcher(self):
		last_result = ''
		while True:
			result = pyperclip.paste()
			word_list = re.compile('\w+').findall(result)
			if len(word_list) > 0:
				print("result = " + result + ', last_word = ' + last_result)
				if last_result != '' and result.find(last_result) >= 0 and len(result) > len(last_result):
					# in this case, result might be a sentence containing the corresponding last-result which was supposed to be a word or phrase.
					# legal sentence
					print('-------------')
					word = tackle_word.TackleWords()
					m = word.query(last_result, result)
					print(m)
					last_result = ''
				else:
					if len(word_list) < 4:  # this may be a word or regular phrase
						last_result = result.strip()
					else:
						last_result = ''
			else:
				last_result = ''

			time.sleep(self._pause)

clip = ClipboardWatcher()
clip.watcher()
