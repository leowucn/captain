# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
from time import gmtime, strftime
import pronunciation
import utility

interval = 2


def watcher():
	word = ''
	i = 0
	while True:
		result = pyperclip.paste().strip()
		word_list = re.compile('\w+').findall(result)
		if word != '' and result.find(word) >= 0 and len(word_list) > len(word):
			# in this case, result should be a usage containing the
			# corresponding result which was supposed to be a word or phrase.
			tackle = tackle_word.TackleWords()
			tackle.query(word + '-1', result, strftime("%Y-%m-%d", gmtime()))
			word = ''
		else:
			if len(word_list) < 4:  # this may be a word or regular phrase
				word = result
				pronunciation.show_literal_pronunciation(word)
				pronunciation.launch_pronunciation(word)
		time.sleep(interval)
	utility.show_notification('Captain Info', 'Some error may happened! Please check error message!')


watcher()
