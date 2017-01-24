# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
import urllib
from time import gmtime, strftime
import os

interval = 2


def watcher():
	last_result = ''
	try:
		while True:
			result = pyperclip.paste().strip()
			word_list = re.compile('\w+').findall(result)
			if len(word_list) > 0:
				if last_result != '' and result.find(last_result) >= 0 and len(result) > len(last_result):
					# in this case, result might be a usage containing the
					# corresponding last-result which was supposed to be a word or phrase.
					# legal usage
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
			time.sleep(interval)
	except:
		show_notification('Some error may happened! Please check error message!')


def show_notification(msg):
	command = "osascript -e \'tell app \"System Events\" to display notification \"" + msg.encode('utf-8') + "\" with title \"Captain Info\"\'"
	os.system(command)


def test_network():
	code = urllib.urlopen("http://dict.youdao.com/").getcode()
	if code != 200:
		return False
	return True

watcher()
