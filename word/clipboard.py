# -*- coding:utf-8 -*-
import time
import pyperclip
import re
import tackle_word
import urllib
from time import gmtime, strftime
import os
# from AppKit import NSWorkspace
# from selenium import webdriver
# import os
# import request
# from openerp import http

interval = 3


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

# # used to get the relational web title or pdf file name.
# def get_relational_title():
# 	return NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
#
# # get current url from browser
# def get_url():
# 	# chromedriver = "/usr/local/Cellar/chromedriver/2.27/bin/chromedriver"
# 	# os.environ["webdriver.chrome.driver"] = chromedriver
# 	# driver = webdriver.Chrome(chromedriver)
# 	# print(driver.current_url)
# 	# driver.quit()
# 	path_info = request.META.get('PATH_INFO')
# 	print(path_info)
# 	http_host = request.META.get('HTTP_HOST')
# 	print(http_host)


def test_network():
	code = urllib.urlopen("http://dict.youdao.com/").getcode()
	if code != 200:
		return False
	return True

watcher()
# time.sleep(6)
# get_url()
