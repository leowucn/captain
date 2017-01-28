# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
from time import gmtime, strftime
import pronunciation
import os
import utility

interval = 2.5    # interval seconds for scanning clipboard
times = 3   # the times of repeating word pronunciation
max_length = 400    # the maximum length of word usage.


def watcher():
	word = ''
	i = 0
	while True:
		result = pyperclip.paste().strip()
		if len(result) >= max_length:
			continue
		word_list = re.compile('\w+').findall(result)
		if len(word_list) == 1 and len(result) != 0 and word != result:
			word = result
			i = 0
		# print('word = ' + word + ', result = ' + result + ', i = ' + str(i))
		if word != '' and result.find(word) >= 0 and len(word_list) > len(word):
			# in this case, result should be a usage containing the
			# corresponding result which was supposed to be a word or phrase.
			tackle = tackle_word.TackleWords()
			tackle.query(word + '-1', result, strftime("%Y-%m-%d", gmtime()))
			os.system("echo '' | pbcopy")
		if word != '':
			if i >= times:
				if result == word:
					os.system("echo '' | pbcopy")
				i = 0
				word = ''
				continue
			i += 1
			pronunciation.show_literal_pronunciation(word)
			pronunciation.launch_pronunciation(word)
		time.sleep(interval)
	utility.show_notification('Captain Info', 'Sorry, some error may happened! Please check the error message!')


watcher()
