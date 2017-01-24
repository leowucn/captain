# -*- coding: utf-8 -*-
import re
import requests
import bs4
import json
import os
from time import gmtime, strftime
from dateutil.parser import parse
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf8')

absolute_prefix = '/Users/leo/work/captain/word'
dict_dir = '/Users/leo/work/captain/word/dict'
words_dir = '/Users/leo/work/captain/word/words'
clipboard_dir = '/Users/leo/work/captain/word/clipboard'
words_index_file = '/Users/leo/work/captain/word/words_index.json'   # index file

max_line = 5000  # restraint line amount of single file, if not, the dict file may be too huge.

word_type = ('n.', 'v.', 'pron.', 'adj.', 'adv.', 'num.', 'art.', 'prep.', 'conj.', 'int.', 'vi.', 'vt.', 'aux.', 'aux.v')

# all types might reside in querying result.
# 'basic'           ------>基本释义
# 'usage'           ------>出现的语句
# 'phrase'          ------>词组短语
# 'synonyms'        ------>同近义词
# 'rel_word_tab'    ------>同根词
# 'discriminate'    ------>词语辨析
# 'collins'         ------>柯林斯
# 'date'            ------>单词录入时间
# 'index'           ------>index

# word-0         represent word from word builder
# word-1         represent word from clipboard


class TackleWords:
	def __init__(self):
		self.index_dict = dict()
		if self.get_file_line_count(words_index_file):
			with open(words_index_file, 'r') as fp:
				self.index_dict = json.load(fp)

	def get_word_meaning(self, raw_string):         # raw_string may be a word or phrase
		valid_string = raw_string[:-2].strip()
		word_list = re.compile('\w+').findall(valid_string)
		post_fix = '%20'.join(word_list)

		url = 'http://dict.youdao.com/w/eng/' + post_fix
		res = requests.get(url)
		soup = bs4.BeautifulSoup(res.content, 'lxml')
		word_meaning_dict = dict()

		# ----------------------basic-----------------------
		basic = soup.find('div', attrs={'class': 'baav'})
		basic_str = ''
		if basic is not None:
			basic_str += ' '.join(list(basic.stripped_strings)) + '\n'
		basic = soup.find("div", id="phrsListTab")
		if basic is not None:
			result = basic.find('div', attrs={'class': 'trans-container'})
			if result is not None:
				basic_str += result.ul.get_text().strip('\n')

		# if basic_str of word is '', we can make sure that this word or phrase does not exist.
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

					if r.find(valid_string) >= 0:
						if i+1 >= len(list(phrase.stripped_strings)):
							break
						phrase_str += r + '     ' + re.sub('\s*', '', list(phrase.stripped_strings)[i+1]) + '\n'
				if len(phrase_str) != 0:
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
		word_meaning_dict['date'] = strftime("%Y-%m-%d", gmtime())

		result = dict()
		result[raw_string] = word_meaning_dict
		return result

	def is_start_word_type(self, src):
		for w_type in word_type:
			if src.strip().startswith(w_type):
				return True
		return False

	def fix_encoding_issue(self, src_string):
		if src_string.count('\\') > 0:
			return src_string.decode('unicode-escape').encode('utf-8')
		return src_string

	def query(self, word, usage=None, date=None, book=None):
		result = dict()
		meaning = dict()
		if word.split('-')[1] == '1':
			self.store_clipboard(word[:-2], usage)
		if word in self.index_dict:
			file_name = self.index_dict[word]['file_name']
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
						# This is essential, without fix encoding issue, the exported dict file encoding wound have problem.
						meaning[res[0]] = self.fix_encoding_issue(res[1])
					else:
						result[word] = meaning
						break

				if date is not None:
					result[word]['date'] = date
				if result[word]['usage'].find(usage) < 0 and usage is not None:
					if 'usage' in result[word]:
						all_usage = self.fix_encoding_issue(result[word]['usage'])
						if all_usage.find(usage) >= 0:
							return
						else:
							all_usage += '\n* ' + usage
						result[word]['usage'] = all_usage
					else:
						result[word]['usage'] = '\n* ' + usage
				if book is not None:
					result[word]['book'] += book + '\n'
				self.update(result)
		else:
			result = self.get_word_meaning(word)
			if result is None:
				return None

			if usage is not None:
				result[word]['usage'] = '* ' + str(usage)
			if date is not None:
				result[word]['date'] = date
			if book is not None:
				result[word]['book'] = book + '\n'
			self.insert(result)
		return result

	def import_all_dir(self):
		self.import_word_builder()
		self.import_clipboard_words()
		show_notification('Importing words completely finished!')

	def import_word_builder(self):
		files = [f for f in os.listdir(words_dir) if os.path.isfile(os.path.join(words_dir, f))]
		for file_name in files:
			if os.path.splitext(file_name)[1] != '.txt':
				continue
			file_path = os.path.join(words_dir, file_name)
			with open(file_path) as f:
				lines = (line.rstrip() for line in f)  # All lines including the blank ones
				lines = list(line for line in lines if line)  # Non-blank lines
				for index, line in enumerate(lines):
					if line[0].isdigit():
						word = line[line.find('.') + 2:]
						usage = lines[index + 1][lines[index + 1].find(':') + 1:]
						book = lines[index + 2][lines[index + 2].find(':') + 2:]
						date = lines[index + 3][lines[index + 3].find(':') + 1:]
						self.query(word + '-0', usage, date, book)

	def import_clipboard_words(self):
		files = [f for f in os.listdir(clipboard_dir) if os.path.isfile(os.path.join(clipboard_dir, f))]
		for file_name in files:
			if os.path.splitext(file_name)[1] != '.txt':
				continue

			word = ''
			usage = ''
			with open(os.path.join(clipboard_dir, file_name)) as f:
				lines = (line.rstrip() for line in f)  # All lines including the blank ones
				lines = (line for line in lines if line)  # Non-blank lines
				for line in lines:
					if self.is_word_line(line):
						word = line[line.find('.') + 1:].strip()
					if line.find('usage') == 0:
						usage = line[line.find(':') + 1:].strip()
					if line.find('date') == 0:
						date = line[line.find(':') + 1:].strip()
						self.query(word + '-1', usage, date)
						word = ''
						usage = ''

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

	def get_latest_file_digit_name(self, src_dir):
		files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
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
		digit_name = self.get_latest_file_digit_name(dict_dir)
		file_name = str(digit_name) + '.json'

		num_lines = self.get_file_line_count(file_name)
		if num_lines >= max_line:
			file_name = str(digit_name + 1) + '.json'
		self.write_to_dict_file(os.path.join(dict_dir, file_name), data)
		self.update_index_dict()

	def delete(self, from_where, delete_word):
		if from_where != '0' and from_where != '1':
			return

		wrapped_word = delete_word + '-' + from_where
		# ----------------delete from dict----------------------
		try:
			file_name = self.index_dict[wrapped_word]['file_name']
			line_index = self.index_dict[wrapped_word]['line_index']
		except KeyError:
			return

		lines_lst = []
		last_inex = 0
		with open(file_name) as f:
			i = 0
			for line in f:
				i += 1
				if i < line_index:
					continue
				stripped_line = line.strip('\n| ')
				if stripped_line == '},' or stripped_line == '}':
					last_inex = i
					break
		with open(file_name) as f:
			i = 0
			for line in f:
				i += 1
				if line_index - 1 <= i <= last_inex:
					continue
				if last_inex + 1 == i:
					if line.strip() == '}':
						lines_lst.append('}\n')
					else:
						lines_lst.append('},\n')
				lines_lst.append(line)
		f = open(file_name, "w")
		for line in lines_lst:
			f.write(line)
		f.close()
		self.update_index_dict()

		# ----------------delete from word builder----------------------
		if from_where == '0':
			for file_name in os.listdir(words_dir):
				if file_name.endswith(".txt"):
					file_path = os.path.join(words_dir, file_name)
					if '. ' + delete_word in open(file_path).read():
						valid_lines_lst = []
						with open(file_path) as f:
							lines = (line.rstrip() for line in f)  # All lines including the blank ones
							lines = list(line for line in lines if line)  # Non-blank lines
							for index, line in enumerate(lines):
								if line[0].isdigit():
									word = line[line.find('.') + 2:].strip()
									if word == delete_word:
										continue
									valid_lines_lst.append(line + '\n')
									valid_lines_lst.append(lines[index + 1] + '\n')
									valid_lines_lst.append(lines[index + 2] + '\n')
									valid_lines_lst.append(lines[index + 3] + '\n')
									valid_lines_lst.append('\n')
						with open(file_path, "w") as f:
							for line in valid_lines_lst:
								f.write(line)

		# ----------------delete from clipboard----------------------
		else:
			for file_name in os.listdir(clipboard_dir):
				if file_name.endswith(".txt"):
					file_path = os.path.join(clipboard_dir, file_name)
					if '. ' + delete_word in open(file_path).read():
						valid_lines_lst = []
						with open(file_path) as f:
							lines = (line.rstrip() for line in f)  # All lines including the blank ones
							lines = list(line for line in lines if line)  # Non-blank lines
							for index, line in enumerate(lines):
								if line[0].isdigit():
									word = line[line.find('.') + 2:].strip()
									if word == delete_word:
										continue
									valid_lines_lst.append(line + '\n')
									valid_lines_lst.append(lines[index + 1] + '\n')
									valid_lines_lst.append(lines[index + 2] + '\n')
									valid_lines_lst.append('\n')
						with open(file_path, "w") as f:
							for line in valid_lines_lst:
								f.write(line)
		return

	def update(self, data):
		file_name = self.index_dict[data.keys()[0]]['file_name']
		self.write_to_dict_file(file_name, data)
		self.update_index_dict()

	def store_clipboard(self, word, usage):
		digit_name = self.get_latest_file_digit_name(clipboard_dir)
		file_name = str(digit_name) + '.txt'

		num_lines = self.get_file_line_count(file_name)
		if num_lines >= max_line:
			file_name = str(digit_name + 1) + '.txt'

		file_path = os.path.join(clipboard_dir, file_name)
		max_index = -1
		if os.path.exists(file_path):
			with open(file_path) as f:
				lines = (line.rstrip() for line in f)  # All lines including the blank ones
				lines = (line for line in lines if line)  # Non-blank lines
				for line in lines:
					if line.strip()[0].isdigit():
						res = re.findall(r'\d+', line)
						if len(res) > 0:
							if res[0] > max_index:
								max_index = int(res[0])
		with open(file_path, mode='a') as f:
			f.write(str(max_index + 1) + '. ' + word + '\n')
			f.write('usage: ' + usage + '\n')
			f.write('date: ' + strftime("%Y-%m-%d", gmtime()) + '\n')
			f.write('\n')

	def write_to_dict_file(self, file_name, data):
		feeds = dict()
		num_lines = self.get_file_line_count(file_name)
		if num_lines > 2:
			filedata = None
			with open(file_name) as feedsjson:
				feeds = json.load(feedsjson)
		for word, verbose_info in data.iteritems():
			feeds[word] = verbose_info
		with open(os.path.join(absolute_prefix, file_name), mode='w') as f:
			f.write(json.dumps(feeds, indent=2))

	def write_to_index_file(self, data):
		f = open(words_index_file, "w")
		f.write(data)
		f.close()

	def update_index_dict(self):
		dict_index_dict = dict()
		dict_file_lst = self.get_all_dict_file_list()

		for file_name in dict_file_lst:
			with open(file_name) as f:
				i = 0
				for line in f:
					i += 1
					if i == 1:
						continue
					stripped_line = line.strip('\n| ')
					if stripped_line.endswith('{'):
						lst = [m.start() for m in re.finditer('"', stripped_line)]
						word = stripped_line[lst[0]+1: lst[1]]
						word_index_info = dict()
						word_index_info['line_index'] = i
						word_index_info['file_name'] = file_name
						dict_index_dict[word] = word_index_info
		self.index_dict = dict_index_dict
		self.write_to_index_file(json.dumps(dict_index_dict, indent=2))

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

	# lst(key: year->week->word  value: word_verbose_info)
	def get_classified_lst(self):
		result = []
		dict_file_lst = self.get_all_dict_file_list()

		from_word_builder_dict = dict()
		from_clipboard_dict = dict()

		for file_name in dict_file_lst:
			with open(file_name) as feedsjson:
				try:
					feeds = json.load(feedsjson)
				except ValueError:
					return result
				for word, verbose_info in feeds.iteritems():
					word_label = word.split('-')[1]
					if word_label == '1':
						res = self.get_year_and_week_by_date(verbose_info[u'date'])
						year = res[0]
						week = res[1]

						if year in from_clipboard_dict:
							if week not in from_clipboard_dict[year]:
								from_clipboard_dict[year][week] = dict()
						else:
							from_clipboard_dict[year] = dict()
							from_clipboard_dict[year][week] = dict()

						tmp = dict()
						for t, meaning in verbose_info.iteritems():
							if str(meaning).count('\\') > 0:
								tmp[t] = meaning.decode('unicode-escape').encode('utf-8')
							else:
								tmp[t] = str(meaning).encode('utf-8')
							# print(repr(m3))   #print unicode of string
						from_clipboard_dict[year][week][word[:-2]] = tmp
					else:
						res = self.get_year_and_week_by_date(verbose_info[u'date'])
						year = res[0]
						week = res[1]

						if year in from_word_builder_dict:
							if week not in from_word_builder_dict[year]:
								from_word_builder_dict[year][week] = dict()
						else:
							from_word_builder_dict[year] = dict()
							from_word_builder_dict[year][week] = dict()

						tmp = dict()
						for t, meaning in verbose_info.iteritems():
							if str(meaning).count('\\') > 0:
								tmp[t] = meaning.decode('unicode-escape').encode('utf-8')
							else:
								tmp[t] = str(meaning).encode('utf-8')
							#print(repr(m3))   #print unicode of string
						from_word_builder_dict[year][week][word[:-2]] = tmp
		result.append(from_word_builder_dict)
		if len(from_clipboard_dict) > 0:
			result.append(from_clipboard_dict)
		return result

	def get_year_and_week_by_date(self, date):
		res = []
		lst = re.split('-| ', date.strip())
		res.append(str(lst[0]))
		res.append(str(datetime.date(int(lst[0]), int(lst[1]), int(lst[2])).isocalendar()[1]))
		return res


def show_notification(msg):
	command = "osascript -e \'tell app \"System Events\" to display notification \"" + msg.encode('utf-8') + "\" with title \"Captain Info\"\'"
	os.system(command)


def test(fname):
	if not os.path.isfile(fname):
		return ''
	with open(fname, 'r') as fin:
		print(fin.read())
		print('---------')


if __name__ == "__main__":
	tackle_words = TackleWords()
	# m = tackle_words.get_word_meaning('get-0')
	# m = tackle_words.query('get-0')
	# m = tackle_words.query('boa')
	# m = tackle_words.query('love')
	# m = tackle_words.query('wikipedia')
	# print(m)
	tackle_words.import_all_dir()
	# tackle_words.delete('1', 'expression')
	# tackle_words.update_index_dict()
	# tackle_words.import_clipboard_words()
	# tackle_words.get_classified_dict()

