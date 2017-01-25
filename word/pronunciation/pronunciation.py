# -*- coding: utf-8 -*-
import requests
import re
import urllib
import subprocess
import time
import bs4


# include british and american pronunciation.
def pronunciation(word):
	word_url = 'http://dictionary.cambridge.org/dictionary/english/' + word.strip()
	content = requests.get(word_url).content
	soup = bs4.BeautifulSoup(content, 'lxml')

	# ----------------------basic-----------------------
	block = soup.find('div', attrs={'class': 'entry-body__el clrd js-share-holder'})
	block_str = ''
	if block is not None:
		block_str += ' '.join(list(block.stripped_strings)) + '\n'
		print(block_str)
	# basic = soup.find("div", id="phrsListTab")
	# if basic is not None:
	# 	result = basic.find('div', attrs={'class': 'trans-container'})
	# 	if result is not None:
	# 		basic_str += result.ul.get_text().strip('\n')
	#
	# # if basic_str of word is '', we can make sure that this word or phrase does not exist.
	# if basic_str == '':
	# 	return None
	# word_meaning_dict['basic'] = basic_str

	# 'data-src-mp3' is the flag where valid word pronunciation url will appear in following position.
	mp3_pos_lst = [m.start() for m in re.finditer('data-src-mp3', content)]
	ogg_pos_lst = [m.start() for m in re.finditer('data-src-ogg', content)]
	if len(mp3_pos_lst) == 0:
		return
	if len(mp3_pos_lst) > 2 and len(ogg_pos_lst) > 2:
		mp3_pos_lst = mp3_pos_lst[:3]
		ogg_pos_lst = ogg_pos_lst[:3]

	url_lst = []
	try:
		offset = 14     # len('data-src-mp3') + 2 and len('data-src-ogg') + 2
		url_lst.append(content[mp3_pos_lst[0] + offset: ogg_pos_lst[0] - 2])
		url_lst.append(content[mp3_pos_lst[1] + offset: ogg_pos_lst[1] - 2])
	except:
		return

	mp3_lst = []
	for url in url_lst:
		name = url.rsplit('/', 1)[-1]
		mp3_lst.append(name)
		urllib.urlretrieve(''.join(url), name)

	for name in mp3_lst:
		subprocess.Popen(['mpg123', '-q', name]).wait()
		time.sleep(1)


pronunciation('get')
