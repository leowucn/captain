# -*- coding: utf-8 -*-
import re
import requests
import bs4
import json
import os
from time import gmtime, strftime
from dateutil.parser import parse
import datetime
import collections

absolute_prefix = '/Users/leo/work/captain/word'
dict_dir = '/Users/leo/work/captain/word/dict'
words_dir = '/Users/leo/work/captain/word/words'
words_index_file = '/Users/leo/work/captain/word/words_index.json'   # index file

max_line = 5000  # restraint single file line, if not, the dict file may be too huge.

word_type = ('n.', 'v.', 'pron.', 'adj.', 'adv.', 'num.', 'art.', 'prep.', 'conj.', 'int.', 'vi.', 'vt.', 'aux.', 'aux.v')

# all types might reside in querying result.
# 'basic'       ------>基本释义
# 'phrase'      ------>词组短语
# 'synonyms'    ------>同近义词
# 'rel_word_tab'------>同根词
# 'discriminate'------>词语辨析
# 'collins'     ------>柯林斯
# 'sentence'    ------>出现的语句
# 'date'        ------>单词录入时间
# 'index'       ------>index


class TackleWords:
	def __init__(self):
		self.index_dict = collections.OrderedDict()
		if self.get_file_line_count(words_index_file):
			with open(words_index_file, 'r') as fp:
				self.index_dict = json.load(fp)

	def get_word_meaning(self, raw_string):         # raw_string may be a word or phrase
		word_list = re.compile('\w+').findall(raw_string)
		post_fix = '%20'.join(word_list)

		url = 'http://dict.youdao.com/w/eng/' + post_fix
		res = requests.get(url)
		soup = bs4.BeautifulSoup(res.content, 'lxml')
		word_meaning_dict = collections.OrderedDict()

		# ----------------------basic-----------------------
		basic = soup.find('div', attrs={'class': 'baav'})
		basic_str = ''
		if basic is not None:
			basic_str += ' '.join(list(basic.stripped_strings)) + '\n'
		basic = soup.find("div", id="phrsListTab")
		if basic is not None:
			result = basic.find('div', attrs={'class': 'trans-container'})
			basic_str += result.ul.get_text().strip('\n')

		# if basic_str of word is '', we can make sure that this does not exist.
		if basic_str == '':
			return None
		word_meaning_dict['basic'] = basic_str

		# -------------------词组短语---------------------
		result = soup.find('div', id='transformToggle')
		if result is not None:
			phrase = result.find('div', id='wordGroup')
			if phrase is not None:
				phrase_str = ''
				# for i, s in enumerate(phrase.stripped_strings):
				# 	print('------------')
				# 	print(s)
				for i, s in enumerate(phrase.stripped_strings):
					r = s.replace('\n', '')
					if r.find(raw_string) >= 0:
						if i+1 >= len(list(phrase.stripped_strings)):
							break
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

				i_next_index = 0
				for i, s in enumerate(lst):
					if i < i_next_index:
						continue

					if self.is_start_word_type(s):
						synonyms_str += s + '\n'

						j_next_index = 0
						j_begin = i + 1
						for j, d in enumerate(lst[j_begin:]):
							if j < j_next_index:
								continue
							if self.is_start_word_type(d):
								i_next_index = j_begin + j
								synonyms_str += '\n'
								break
							if d == ',':
								synonyms_str += ', '
							else:
								synonyms_str += d
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
			word_meaning_dict['collins'] = collins_str.encode('utf-8')

		# ---------------------date---------------------
		word_meaning_dict['date'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())

		result = collections.OrderedDict()
		result[raw_string] = word_meaning_dict
		return result

	def is_start_word_type(self, src):
		for w_type in word_type:
			if src.strip().startswith(w_type):
				return True
		return False

	def query(self, word, sentence=None, date=None):
		result = collections.OrderedDict()
		meaning = collections.OrderedDict()
		if word in self.index_dict:
			file_name = self.index_dict[word]['file_name']
			is_ok = False
			with open(os.path.join(absolute_prefix, file_name)) as f:
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
						result[word] = meaning
						is_ok = True
						break
			if is_ok:
				if sentence is not None:
					result[word]['sentence'] += '||' + sentence
				if date is not None:
					result[word]['date'] = date
				self.update(result)
		else:
			result = self.get_word_meaning(word)
			if result is None:
				return None

			if sentence is not None:
				result[word]['sentence'] = sentence
			if date is not None:
				result[word]['date'] = date
			self.insert(result)
		return result

	def import_list(self):
		files = [f for f in os.listdir(words_dir) if os.path.isfile(os.path.join(words_dir, f))]
		for file_name in files:
			extend_formt = os.path.splitext(file_name)[1]
			if extend_formt != '.txt':
				continue

			pure_file_name = os.path.splitext(file_name)[0]
			word = ''
			with open(os.path.join(words_dir, file_name)) as f:
				for line in f:
					stripped_line = line.strip()
					if len(stripped_line) == 0:
						continue

					if self.is_word_line(stripped_line):
						word = line[line.find("(") + 1:line.find(")")]
					else:
						if self.is_date(pure_file_name):
							self.query(word, stripped_line, pure_file_name)
							continue
						self.query(word, stripped_line, None)

	def is_date(self, string):
		try:
			parse(string)
			return True
		except ValueError:
			return False

	def is_word_line(self, line):
		is_number = False
		for i, c in enumerate(line):
			if c.isdigit():
				is_number = True
			elif is_number and c == '.':
				return True
			else:
				return False


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

	def insert(self, data):
		digit_name = self.get_latest_file_digit_name()
		file_name = str(digit_name) + '.json'

		num_lines = self.get_file_line_count(file_name)
		if num_lines >= max_line:
			file_name = str(digit_name + 1) + '.json'
		self.write_to_json_file(os.path.join(dict_dir, file_name), data)
		self.update_index_dict()

	def update(self, data):
		for key, value in data.iteritems():
			file_name = self.index_dict[key]['file_name']
			self.write_to_json_file(file_name, data)
			self.update_index_dict()

	def write_to_json_file(self, file_name, data):
		feeds = collections.OrderedDict()
		num_lines = self.get_file_line_count(file_name)
		if num_lines > 0:
			with open(file_name) as feedsjson:
				feeds = json.load(feedsjson)
		for key, value in data.iteritems():
			feeds[key] = value
		i = 1
		for key, value in feeds.iteritems():
			value['index'] = str(i)
			i += 1
			feeds[key] = value
		with open(os.path.join(absolute_prefix, file_name), mode='w+') as f:
			f.write(json.dumps(feeds, indent=2))


	def update_index_dict(self):
		dict_index_dict = collections.OrderedDict()
		dict_file_lst = self.get_all_dict_file_list()

		for file_name in dict_file_lst:
			with open(file_name) as f:
				i = 0
				for line in f:
					i += 1
					if i == 1:
						continue
					if line.strip('\n').endswith('{'):
						word = re.sub(r'\W+', '', line)
						word_index_info = collections.OrderedDict()
						word_index_info['line_index'] = i
						word_index_info['file_name'] = file_name
						dict_index_dict[word] = word_index_info
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

	# return value: dict() -------- key: year->week->word  value: word_verbose_info
	def get_classified_dict(self):
		classified_dict = collections.OrderedDict()
		dict_file_lst = self.get_all_dict_file_list()

		for file_name in dict_file_lst:
			with open(file_name) as feedsjson:
				feeds = json.load(feedsjson)
				for word, verbose_info in feeds.iteritems():
					date_list = verbose_info[u'date'].split('-')
					year = date_list[0]
					week = str(datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2])).isocalendar()[1])

					if year in classified_dict:
						if week not in classified_dict[year]:
							classified_dict[year][week] = collections.OrderedDict()
					else:
						classified_dict[year] = collections.OrderedDict()
						classified_dict[year][week] = collections.OrderedDict()

					tmp = collections.OrderedDict()
					for t, meaning in verbose_info.iteritems():
						tmp[t] = meaning.encode('utf-8')
					classified_dict[year][week][word] = tmp
		return classified_dict


def test(fname):
	if not os.path.isfile(fname):
		return ''
	with open(fname, 'r') as fin:
		print(fin.read())
		print('---------')


if __name__ == "__main__":
	tackle_words = TackleWords()
	m = tackle_words.get_word_meaning('blink')
	#m = tackle_words.query('get')
	#m = tackle_words.query('boa')
	#m = tackle_words.query('love')
	#m = tackle_words.query('wikipedia')
	#print(m)
	tackle_words.import_list()
	#tackle_words.get_classified_dict()

