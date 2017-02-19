# -*- coding: utf-8 -*-
import re
import urllib
import subprocess
import time
import os
from mechanize import Browser
import bs4
import requests
import json
import utility
import string

# the interval time of British pronunciation and American pronunciation
pronunciation_interval = 0.7

basic_dict_file = os.path.join(os.getcwd(), 'core/asset/pronunciation/basic.json')
pronunciation_dir_pre = os.path.join(os.getcwd(), 'core/asset/pronunciation')
basic_dict = dict()


def show(word):
	if not word[0].startswith(tuple(string.ascii_letters)):
		return
	show_literal_pronunciation(word)
	launch_pronunciation(word)


def launch_pronunciation(word):
	stripped_word = word.strip().lower()
	if len(stripped_word) == 0:
		return
	dst_dir = os.path.join(pronunciation_dir_pre, stripped_word[0])
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)
		get_pronunciation(stripped_word, dst_dir)
		return
	else:
		files = [f for f in os.listdir(dst_dir) if os.path.isfile(os.path.join(dst_dir, f))]
		d = dict()
		for filename in files:
			if os.path.splitext(filename)[0] == stripped_word + '-uk':
				d['uk'] = os.path.join(dst_dir, filename)
			if os.path.splitext(filename)[0] == stripped_word + '-us':
				d['us'] = os.path.join(dst_dir, filename)
		if len(d) > 0:
			if 'uk' in d:
				subprocess.Popen(['mpg123', '-q', d['uk']]).wait()
				time.sleep(pronunciation_interval)
			if 'us' in d:
				subprocess.Popen(['mpg123', '-q', d['us']]).wait()
		else:
			get_pronunciation(stripped_word, dst_dir)
			return
	return


# include British and American pronunciation.
def get_pronunciation(word, dst_dir):
	url = 'http://dictionary.cambridge.org/'
	browser = Browser()
	browser.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	browser.set_handle_equiv(True)
	browser.set_handle_redirect(True)
	browser.set_handle_referer(True)
	browser.set_handle_robots(False)
	browser.open(url)
	browser.select_form(nr=0)
	browser['q'] = word
	try:
		response = browser.submit()
	except:
		return
	content = response.read()

	mp3_pos_lst = [m.start() for m in re.finditer('data-src-mp3', content)]
	ogg_pos_lst = [m.start() for m in re.finditer('data-src-ogg', content)]
	if len(mp3_pos_lst) == 0 or len(ogg_pos_lst) == 0:
		return
	if len(mp3_pos_lst) >= 2 and len(ogg_pos_lst) >= 2:
		mp3_pos_lst = mp3_pos_lst[:2]
		ogg_pos_lst = ogg_pos_lst[:2]
	else:
		min_len = min(len(mp3_pos_lst), len(ogg_pos_lst))
		mp3_pos_lst = mp3_pos_lst[:min_len]
		ogg_pos_lst = ogg_pos_lst[:min_len]

	url_lst = []
	try:
		offset = 14     # len('data-src-mp3') + 2 or len('data-src-ogg') + 2
		for i in range(len(mp3_pos_lst)):
			url_lst.append(content[mp3_pos_lst[i] + offset: ogg_pos_lst[i] - 2])
	except:
		return

	mp3_name_lst = []
	if len(url_lst) == 1:
		file_extension_uk = os.path.splitext(url_lst[0])[1]
		name_uk = os.path.join(dst_dir, word + '-uk' + file_extension_uk)
		mp3_name_lst.append(name_uk)
		urllib.urlretrieve(''.join(url_lst[0]), name_uk)
	else:
		file_extension_uk = os.path.splitext(url_lst[0])[1]
		name_uk = os.path.join(dst_dir, word + '-uk' + file_extension_uk)
		mp3_name_lst.append(name_uk)
		urllib.urlretrieve(''.join(url_lst[0]), name_uk)

		file_extension_us = os.path.splitext(url_lst[0])[1]
		name_us = os.path.join(dst_dir, word + '-us' + file_extension_us)
		mp3_name_lst.append(name_us)
		urllib.urlretrieve(''.join(url_lst[1]), name_us)

	for name in mp3_name_lst:
		if os.path.isfile(name):
			subprocess.Popen(['mpg123', '-q', name]).wait()
			time.sleep(pronunciation_interval)


def show_literal_pronunciation(word):
	stripped_word = word.strip()
	if not stripped_word.isalpha():
		return
	global basic_dict
	load_basic_dict()

	basic = dict()
	if stripped_word in basic_dict:
		basic = basic_dict[stripped_word]
	else:
		result = dl_pronunciation(stripped_word)
		if len(result) == 0:
			return
		basic['pronun'] = result['pronun']
		basic['basic'] = result['basic']
		basic_dict[stripped_word] = basic
		write_basic_dict()

	literal = basic['pronun'].replace("'", ".")
	literal = literal.replace("ˈ", ".")
	utility.show_notification(word + ' ☞ ' + literal.encode('utf-8'), basic['basic'].encode('utf-8'))
	return


def dl_pronunciation(word):
	basic = dict()
	url = 'http://dict.youdao.com/w/eng/' + word.lower().strip()
	print(url)
	res = requests.get(url)
	soup = bs4.BeautifulSoup(res.content, 'lxml')
	pronunciation = soup.find('div', attrs={'class': 'baav'})
	if pronunciation is not None:
		basic['pronun'] = ' '.join(list(pronunciation.stripped_strings))
	else:
		basic['pronun'] = ''

	# ----------------------basic definition-----------------------
	basic_soup = soup.find("div", id="phrsListTab")
	if basic_soup is not None:
		result = basic_soup.find('div', attrs={'class': 'trans-container'})
		if result is not None:
			basic['basic'] = result.ul.get_text().strip('\n')
		else:
			basic['basic'] = ''
	else:
		basic['basic'] = ''
	return basic


def load_basic_dict():
	if not os.path.isfile(basic_dict_file):
		return
	global basic_dict
	with open(basic_dict_file, 'r') as fp:
		basic_dict = json.load(fp)


def write_basic_dict():
	global basic_dict
	with open(basic_dict_file, mode='w') as f:
		f.write(json.dumps(basic_dict, indent=2))


# launch_pronunciation('congregate')
# show_literal_pronunciation('dilemma')
