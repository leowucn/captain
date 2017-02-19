# -*- coding:utf-8 -*-
import platform
import os
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def show_notification(title, msg):
	if platform.system() == 'Darwin':
		strippend_msg = msg.strip()
		if strippend_msg == "":
			return
		command = "osascript -e \'tell app \"System Events\" to display notification \"" + strippend_msg.encode('utf-8') + "\" with title \"" + title.encode('utf-8') + "\"\'"
		os.system(command)
	return


def test_network():
	code = urllib.urlopen("http://dict.youdao.com/").getcode()
	if code != 200:
		return False
	return True
