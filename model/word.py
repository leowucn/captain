# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import re
import requests
import bs4
import json

json_words_meaning = './json_words_meaning'

meaning_type = ('basic', 'phrase', 'synonyms', 'rel_word_tab', 'discriminate', 'collins')

class Word:
	def __init__(self):
		pass

	def query_word_meaning(self, word):
		url = 'http://dict.youdao.com/w/eng/' + word
		res = requests.get(url)
		soup = bs4.BeautifulSoup(res.content, 'lxml')
		word_meaning_dict = dict()

		# ----------------------basic-----------------------
		pronunciation = soup.find('div', attrs={'class': 'baav'})
		pronunciation_str = ''
		if pronunciation is not None:
			pronunciation_str += ' '.join(list(pronunciation.stripped_strings)) + '\n'
		basic = soup.find("div", id="phrsListTab")
		if basic is not None:
			result = basic.find('div', attrs={'class': 'trans-container'})
			pronunciation_str += result.ul.get_text().strip('\n')
		word_meaning_dict['basic'] = pronunciation_str

		# -------------------词组短语---------------------
		result = soup.find('div', id='transformToggle')
		phrase = result.find('div', id='wordGroup')
		if phrase is not None:
			phrase_str = ''
			for i, s in enumerate(phrase.stripped_strings):
				r = s.replace('\n', '')
				if r.find(word) >= 0:
					phrase_str += r + '     ' + re.sub('\s*', '', list(phrase.stripped_strings)[i+1]) + '\n'
			word_meaning_dict['phrase'] = phrase_str.strip('\n')

		# -------------------同近义词---------------------
		result = soup.find('div', id='transformToggle')
		synonyms = result.find('div', id='synonyms')
		if synonyms is not None:
			synonyms_str = ''
			lst = []
			for s in synonyms.stripped_strings:
				lst.append(s)
			tmp = []
			for i, s in enumerate(lst):
				if s.isalpha() or s == ',':
					tmp.append(s)
				else:
					synonyms_str += ' '.join(tmp) + '\n' + s + '\n'
					tmp[:] = []
			word_meaning_dict['synonyms'] = synonyms_str.strip('\n')

		# -------------------同根词---------------------
		result = soup.find('div', id='transformToggle')
		rel_word_tab = result.find('div', id='relWordTab')
		if rel_word_tab is not None:
			rel_word_tab_str = ''

			is_found = False
			for i, s in enumerate(rel_word_tab.stripped_strings):
				if s == '词根：':
					rel_word_tab_str += s + ' ' + list(rel_word_tab.stripped_strings)[i+1] + '\n'
					is_found = True
					continue
				if is_found:
					is_found = False
					continue
				if s.find('.') >= 0:
					rel_word_tab_str += s + '\n'
				elif s.encode('utf-8').isalpha():  # without "encode('utf-8')", the Chinese symbol is recognized as alpha
					rel_word_tab_str += s + '   '
				else:
					if len(rel_word_tab_str) > 0:
						rel_word_tab_str += s + '\n'
					else:
						rel_word_tab_str += s
			word_meaning_dict['rel_word_tab'] = rel_word_tab_str.strip('\n')

		# -------------------词语辨析---------------------
		result = soup.find('div', id='transformToggle')
		discriminate = result.find('div', id='discriminate')
		if discriminate is not None:
			discriminate_str = ''
			is_found = False
			for i, s in enumerate(discriminate.stripped_strings):
				if is_found:
					is_found = False
					continue
				if is_alpha_and_x(s, ','):
					discriminate_str += '\n' + s + '\n'
					attach = list(discriminate.stripped_strings)[i+1] + '\n'
					is_found = True
					if whether_start_with_alpha(attach):
						continue
					else:
						discriminate_str += attach
					continue
				if whether_only_alpha(s):
					discriminate_str += s + '   '
				if whether_has_non_alpha_symbol(s) and s != '以上来源于' and s != '网络':
					discriminate_str += s + '\n'
			word_meaning_dict['discriminate'] = discriminate_str.strip('\n')

		# ---------------------collins---------------------
		collins = soup.find('div', id="collinsResult")
		if collins is not None:
			text_list = []
			for i, s in enumerate(collins.stripped_strings):
				text_list.append(' '.join(s.split()))   # tackle special formation problem

			line = ' '.join(text_list[3:])
			collins_str = re.sub('例：', '\n例：', line)
			collins_str = re.sub("\d+\.", "\n*", collins_str)
			collins_str = collins_str[collins_str.find('*'):]
			word_meaning_dict['collins'] = collins_str

		for key, value in word_meaning_dict.items():
			print(value.encode('utf-8'))
			print('-------------')
		return word_meaning_dict


	def write(self, word_meaning):
		f = open(json_words_meaning, 'w+')
		json.dump(word_meaning, f)


def is_alpha_and_x(src_str, x):
	has_alpha = False
	has_x = False

	for s in src_str.encode('utf-8'):
		if s.isalpha():
			has_alpha = True
			continue
		elif s == str(x):
			has_x = True
			continue
		elif s == str(' '):
			continue
		else:
			return False
	if has_alpha and has_x:
		return True
	return False


def whether_start_with_alpha(src_str):
	for s in src_str.encode('utf-8'):
		if s.isalpha():
			return True
	return False


def whether_has_non_alpha_symbol(src_str):
	for s in src_str.encode('utf-8'):
		if not s.isalpha():
			return True
	return False

def whether_only_alpha(src_str):
	for s in src_str.encode('utf-8'):
		if not s.isalpha():
			return False
	return True



word = Word()
t = word.query_word_meaning('get')
