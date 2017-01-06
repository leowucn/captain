# -*- coding: utf-8 -*-
import re
import requests
import bs4
import json
import os
from time import gmtime, strftime

dict_dir = './dict'
words_dir = './words'
words_index_file = './words_index.json'   # index file

# all types that might appear in querying result.
# 'basic'       ------>基本释义
# 'phrase'      ------>词组短语
# 'synonyms'    ------>同近义词
# 'rel_word_tab'------>同根词
# 'discriminate'------>词语辨析
# 'collins'     ------>柯林斯
# 'date'        ------>单词录入时间


class TackleWords:
	def __init__(self):
		self.index_dict = dict()
		if self.get_file_line_count(words_index_file):
			with open(words_index_file, 'r') as fp:
				self.index_dict = json.load(fp)

	def get_word_meaning(self, word):
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
		if result is not None:
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
		if result is not None:
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
		if result is not None:
			rel_word_tab = result.find('div', id='relWordTab')
			if rel_word_tab is not None:
				rel_word_tab_str = ''

				is_found = False
				for i, s in enumerate(rel_word_tab.stripped_strings):
					if s == u'词根：':
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
		if result is not None:
			discriminate = result.find('div', id='discriminate')
			if discriminate is not None:
				discriminate_str = ''
				is_found = False
				for i, s in enumerate(discriminate.stripped_strings):
					if is_found:
						is_found = False
						continue
					if self.is_alpha_and_x(s, ','):
						discriminate_str += '\n' + s + '\n'
						attach = list(discriminate.stripped_strings)[i+1] + '\n'
						is_found = True
						if self.whether_start_with_alpha(attach):
							continue
						else:
							discriminate_str += attach
						continue
					if self.whether_only_alpha(s):
						discriminate_str += s + '   '
					if self.whether_has_non_alpha_symbol(s) and s != u'以上来源于' and s != u'网络':
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

		# ---------------------date---------------------
		word_meaning_dict['date'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())

		result = dict()
		result[word] = word_meaning_dict
		return result

	def query_word(self, word):
		meaning = dict()
		if word in self.index_dict:
			file_name = self.index_dict[word]['file_name']
			with open(os.path.join(dict_dir, file_name)) as f:
				i = 0
				for line_content in f:
					i += 1
					if self.index_dict[word]['line_index'] > i:
						continue
					if line_content.strip() != u'}' and line_content.strip() != u'},':
						res = self.extract_content(line_content)
						if len(res) != 2:
							continue
						meaning[res[0]] = res[1]
					else:
						meaning[word] = meaning
						break
		else:
			meaning = self.get_word_meaning(word)
			self.update(meaning)
		return meaning

	def import_word_build_list(self):
		files = [f for f in os.listdir(words_dir) if os.path.isfile(os.path.join(words_dir, f))]
		for filename in files:
			extend_formt = os.path.splitext(filename)[1]
			#print('filename = ' + filename + ', extend_format = ' + extend_formt)
			if extend_formt != '.txt':
				pass


	def get_latest_file_digit_name(self):
		files = [f for f in os.listdir(dict_dir) if os.path.isfile(os.path.join(dict_dir, f))]

		max_num = 1
		for filename in files:
			name = os.path.splitext(filename)[0]
			if not name.isdigit():
				continue
			num = int(name)
			if num > max_num:
				max_num = num
		return max_num

	def get_all_dict_file_list(self):
		lst = []
		files = [f for f in os.listdir(dict_dir) if os.path.isfile(os.path.join(dict_dir, f))]

		for filename in files:
			name = os.path.splitext(filename)[0]
			if not name.isdigit():
				continue
			lst.append(os.path.join(dict_dir, filename))
		return lst

	def update(self, data):
		digit_name = self.get_latest_file_digit_name()
		file_name = str(digit_name) + '.json'

		num_lines = self.get_file_line_count(file_name)
		if num_lines >= 5000:   # restraint file size, if not, the dict file may be too huge.
			file_name = str(digit_name + 1) + '.json'
		self.write_to_json_file(os.path.join(dict_dir, file_name), data)
		self.update_index_dict()

	def write_to_json_file(self, file_name, data):
		feeds = dict()
		if not os.path.isfile(file_name):
			with open(file_name, mode='w') as f:
				for key, value in data.iteritems():
					feeds[key] = value
				f.write(json.dumps(feeds, indent=2))
		else:
			num_lines = self.get_file_line_count(file_name)
			feeds = dict()
			if num_lines > 0:
				with open(file_name) as feedsjson:
					feeds = json.load(feedsjson)

			for key, value in data.iteritems():
				feeds[key] = value
			with open(file_name, mode='w') as f:
				f.write(json.dumps(feeds, indent=2))

	def update_index_dict(self):
		dict_index_dict = dict()
		dict_file_lst = self.get_all_dict_file_list()

		print(dict_file_lst)
		for file_name in dict_file_lst:
			with open(file_name) as f:
				i = 0
				for line in f:
					i += 1
					if i == 1:
						continue
					if line.strip('\n').endswith('{'):
						word = re.sub(r'\W+', '', line)
						word_index_info = dict()
						word_index_info['line_index'] = i
						word_index_info['file_name'] = file_name
						dict_index_dict[word] = word_index_info
		try:
			os.remove(words_index_file)
		except OSError:
			pass
		self.write_to_json_file(words_index_file, dict_index_dict)
		self.index_dict = dict_index_dict

		# extract content exactly from quotation mark
	def extract_content(self, string):
		lst = []
		src = string.strip()
		i_next_pos = 0
		for i, c in enumerate(src):
			if i < i_next_pos:
				continue
			if c == '\"':
				j_next_pos = 0
				j_begin = i + 1
				for j, d in enumerate(src[j_begin:]):
					if j < j_next_pos:
						continue
					if d == '\"':
						lst.append(src[j_begin: j_begin+j])
						i_next_pos = j_begin + j + 1
						if i_next_pos >= len(src):
							return lst
						break
					elif d == '\\':
						j_next_pos = j + 2
			elif c == '\\':
					i_next_pos = i + 2
		return lst


	def is_alpha_and_x(self, src_str, x):
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

	def whether_start_with_alpha(self, src_str):
		for s in src_str.encode('utf-8'):
			if s.isalpha():
				return True
		return False

	def whether_has_non_alpha_symbol(self, src_str):
		for s in src_str.encode('utf-8'):
			if not s.isalpha():
				return True
		return False

	def whether_only_alpha(self, src_str):
		for s in src_str.encode('utf-8'):
			if not s.isalpha():
				return False
		return True

	def get_file_line_count(self, file_name):
		if not os.path.isfile(file_name):
			return 0
		f = open(file_name, 'r')
		num_lines = sum(1 for line in f)
		f.close()
		return num_lines

def test(fname):
	if not os.path.isfile(fname):
		return ''
	with open(fname, 'r') as fin:
		print(fin.read())
		print('---------')


tackle_words = TackleWords()
#m = tackle_words.get_word_meaning('get')
#m = tackle_words.query_word('get')
m = tackle_words.query_word('boa')
#m = tackle_words.query_word('love')
#m = tackle_words.query_word('wikipedia')
#print(m)

tackle_words.import_word_build_list()
