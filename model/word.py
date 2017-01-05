# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import re
import requests
import bs4
import json
import collections
import os
import codecs

words_index = './words_index.json'

# key of xxx.json item
meaning_type = ('word', 'basic', 'phrase', 'synonyms', 'rel_word_tab', 'discriminate', 'collins')

# index introduction
# tmp = dict()
# t = dict()
# t['line_index'] = 1
# t['line_num'] = 1   # the line num in which the content takes
# t['file_name'] = 1.json
# tmp['word'] = t

class TackleWord:
	def __init__(self):
		self.index_dict = dict()
		self.load_index_file()

	def get_word_meaning(self, word):
		url = 'http://dict.youdao.com/w/eng/' + word
		res = requests.get(url)
		soup = bs4.BeautifulSoup(res.content, 'lxml')
		word_meaning_dict = collections.OrderedDict()

		# ----------------------word-----------------------
		word_meaning_dict['word'] = word
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

		#for key, value in word_meaning_dict.items():
		#	print(value.encode('utf-8'))
		#	print('-------------')
		return word_meaning_dict

	def query_word(self, word):
		meaning = ''
		if word in self.index_dict:
			with open(self.index_dict[word]['file_name']) as f:
				i = 0
				tmp_file_name = './tmp.json'
				fp = file(tmp_file_name, 'wb')
				for line_content in f:
					i += 1
					if self.index_dict[word]['line_index'] <= i <= self.index_dict[word]['line_index'] + self.index_dict[word]['line_num']:
						fp.write(line_content)

				with codecs.open(tmp_file_name, 'r', encoding='utf-8') as data_file:
					meaning = json.loads(data_file.read())
				#with open(tmp_file_name) as data_file:
				#	meaning = json.load(data_file)
				# try:
				# 	os.remove(tmp_file_name)
				# except OSError:
				# 	pass
		else:
			meaning = self.get_word_meaning(word)
			self.update(meaning)
		return meaning

	def get_latest_file_digit_name(self):
		files = [f for f in os.listdir('.') if os.path.isfile(f)]

		max_num = 1
		for filename in files:
			name = os.path.splitext(filename)[0]
			if not name.isdigit():
				continue
			num = int(name)
			if num > max_num:
				max_num = num
		return max_num

	def update(self, data):
		digit_name = self.get_latest_file_digit_name()
		file_name = str(digit_name) + '.json'
		print(file_name)

		num_lines = sum(1 for line in open(file_name, 'w+'))
		if num_lines >= 5000:   # restraint file size, if not, the speed may descend
			file_name = str(digit_name + 1) + '.json'

		num_lines_before = sum(1 for line in open(file_name))
		self.write_to_json_file(file_name, data)
		num_lines_after = sum(1 for line in open(file_name))

		index_info = dict()
		index_info['line_index'] = num_lines_before + 1
		index_info['file_name'] = file_name
		index_info['line_num'] = num_lines_after
		self.index_dict[data['word']] = index_info
		self.write_to_json_file(words_index, self.index_dict)

	def write_to_json_file(self, file_name, data):
		if not os.path.isfile(file_name):
			with open(file_name, mode='w') as f:
				f.write(json.dumps(data, indent=2))
		else:
			num_lines = sum(1 for line in open(file_name))
			feeds = collections.OrderedDict()
			if num_lines > 0:
				with codecs.open(file_name, 'r', encoding='gbk') as feedsjson:
					feeds = json.load(feedsjson)

			feeds.update(data)
			with codecs.open(file_name, 'w+', encoding='gbk') as f:
				f.write(json.dumps(feeds, indent=2))

	def load_index_file(self):
		if os.path.isfile(words_index):
			with open(words_index, 'r') as fp:
				self.index_dict = json.load(fp)

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


word = TackleWord()
#word.get_word_meaning('get')
m = word.query_word('get')
print(m)
#word_meaning_dict = word.get_word_meaning('get')
#word.write_to_json_file('1.json', word_meaning_dict)

#word.generate_new_filename()
