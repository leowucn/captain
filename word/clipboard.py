# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
import urllib
from time import gmtime, strftime
import os
import pronunciation
import platform

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
				pronunciation.launch_pronunciation(word)
		time.sleep(interval)
	show_notification('Some error may happened! Please check error message!')


def show_notification(msg):
	if platform.system() == 'Darwin':
		command = "osascript -e \'tell app \"System Events\" to display notification \"" + msg.encode('utf-8') + "\" with title \"Captain Info\"\'"
		os.system(command)
	return


def test_network():
	code = urllib.urlopen("http://dict.youdao.com/").getcode()
	if code != 200:
		return False
	return True

watcher()
