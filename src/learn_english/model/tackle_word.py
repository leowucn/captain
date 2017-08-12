# -*- coding: utf-8 -*-
import re
import bs4
import os
from os.path import dirname, abspath
import datetime
import utility
from datetime import datetime

parent_dir = dirname(dirname(abspath(__file__)))
working_dir = os.getcwd()
absolute_prefix = os.path.join(working_dir, 'asset')
words_dir = os.path.join(parent_dir, 'asset/words')

dict_file = os.path.join(parent_dir, 'asset/dict.json')
clipboard_file = os.path.join(parent_dir, 'asset/clipboard.json')
builder_file = os.path.join(parent_dir, 'asset/builder.json')

word_type = ('n.', 'v.', 'pron.', 'adj.', 'adv.', 'num.', 'art.', 'prep.', 'conj.', 'int.', 'vi.', 'vt.', 'aux.', 'aux.v')

'''
all types might reside in querying result.
'basic'           ------>基本释义
'usage'           ------>出现的语句
'phrase'          ------>词组短语
'synonyms'        ------>同近义词
'rel_word_tab'    ------>同根词
'discriminate'    ------>词语辨析
'collins'         ------>柯林斯
'date'            ------>单词录入时间
'index'           ------>index

word-0         represent word from word builder
word-1         represent word from clipboard
'''


class TackleWords:
    def __init__(self):
        self.dict_data = utility.load_json_file(dict_file)
        self.clipboard_data = utility.load_json_file(clipboard_file)

    def get_word_meaning(self, raw_string):
        word = raw_string[:-2].strip()
        word_list = re.compile('\w+').findall(word)
        post_fix = '%20'.join(word_list)

        url = 'http://www.youdao.com/w/eng/' + post_fix
        content = utility.get_content_of_url(url)
        soup = bs4.BeautifulSoup(content, 'lxml')
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
                for i, s in enumerate(phrase.stripped_strings):
                    r = s.replace('\n', '')

                    if r.find(word) >= 0:
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
            if len(collins_str.strip()) > 1:
                word_meaning_dict['collins'] = collins_str.encode('utf-8')

        word_meaning_dict['usage'] = ''
        result = dict()
        result[raw_string] = word_meaning_dict
        return result

    @staticmethod
    def is_start_word_type(src):
        for w_type in word_type:
            if src.strip().startswith(w_type):
                return True
        return False

    def query(self, wrapped_word, usage=None, date=None, book=None):
        word_come_from = wrapped_word.split('-')[1]

        if word_come_from == '1':
            self.store_clipboard(wrapped_word[:-2], usage)

        if wrapped_word not in self.dict_data:
            result = self.get_word_meaning(wrapped_word)
            if result is None:
                return None

            if usage is not None:
                result[wrapped_word]['usage'] = self.add_usage_to_collection(result[wrapped_word]['usage'], usage)
            if date is not None:
                result[wrapped_word]['date'] = date.strip()
            if book is not None:
                result[wrapped_word]['book'] = book.strip()
            self.dict_data[wrapped_word] = result[wrapped_word]
        else:
            self.dict_data[wrapped_word]['usage'] = self.add_usage_to_collection(self.dict_data[wrapped_word]['usage'], usage)
        utility.write_json_file(dict_file, self.dict_data)
        return

    @staticmethod
    def add_usage_to_collection(collection, usage):
        if collection.find(usage) < 0:
            collection += usage
            if not usage.endswith('\n'):
                collection += '\n'
        return collection

    def update_clipboard(self):
        self.import_clipboard_words()
        self.clipboard_data = utility.load_json_file(clipboard_file)

    def upsert_word(self, word_info):
        self.dict_data[word_info.keys()[0]] = word_info.values()[0]
        utility.write_json_file(dict_file, self.dict_data)

    def import_all_dir(self):
        self.import_word_builder()
        self.import_clipboard_words()
        utility.show_notification('Captain Import Info', 'Importing words completely finished!')

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
                        wrapped_word = word + '-0'
                        if wrapped_word in self.dict_data:
                            continue
                        usage = lines[index + 1][lines[index + 1].find(':') + 1:]
                        book = lines[index + 2][lines[index + 2].find(':') + 1:]
                        self.query(wrapped_word, usage, file_name[:-4], book)

    def import_clipboard_words(self):
        for word, word_info in self.clipboard_data.iteritems():
            wrapped_word = word + '-1'
            self.query(wrapped_word, word_info['usage'], word_info['date'])

    def delete(self, wrapped_word):
        word_ele = wrapped_word.split('-')
        # ----------------delete from dict----------------------
        del self.dict_data[wrapped_word]
        utility.write_json_file(dict_file, self.dict_data)
        # ----------------delete from word builder----------------------
        if word_ele[1] == '0':
            for file_name in os.listdir(words_dir):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(words_dir, file_name)
                    if '. ' + word_ele[0] in open(file_path).read():
                        valid_lines_lst = []
                        with open(file_path) as f:
                            lines = (line.rstrip() for line in f)  # All lines including the blank ones
                            lines = list(line for line in lines if line)  # Non-blank lines
                            for index, line in enumerate(lines):
                                if line[0].isdigit():
                                    wrapped_word = line[line.find('.') + 2:].strip()
                                    if wrapped_word == word_ele[0]:
                                        continue
                                    valid_lines_lst.append(line + '\n')
                                    valid_lines_lst.append(lines[index + 1] + '\n')
                                    valid_lines_lst.append(lines[index + 2] + '\n')
                                    valid_lines_lst.append(lines[index + 3] + '\n')
                                    valid_lines_lst.append('\n')
                        with open(file_path, "w") as f:
                            for line in valid_lines_lst:
                                f.write(line)
                        break
        # ----------------delete from clipboard----------------------
        else:
            if word_ele[0] in self.clipboard_data:
                del self.clipboard_data[word_ele[0]]
                utility.write_json_file(clipboard_file, self.clipboard_data)
        return

    def store_clipboard(self, word, usage):
        if word in self.clipboard_data:
            self.clipboard_data[word]['usage'] = self.add_usage_to_collection(self.clipboard_data[word]['usage'], usage)
        else:
            word_info = dict()
            word_info['usage'] = ''
            word_info['usage'] = self.add_usage_to_collection(word_info['usage'], usage)
            word_info['date'] = str(datetime.now())[:-7]
            self.clipboard_data[word] = word_info
        utility.write_json_file(clipboard_file, self.clipboard_data)

    @staticmethod
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

    @staticmethod
    def whether_start_with_alpha(src_str):
        for s in src_str.encode('utf-8'):
            if s.isalpha():
                return True
        return False

    @staticmethod
    def whether_has_non_alpha_symbol(src_str):
        for s in src_str.encode('utf-8'):
            if not s.isalpha():
                return True
        return False

    @staticmethod
    def whether_only_alpha(src_str):
        for s in src_str.encode('utf-8'):
            if not s.isalpha():
                return False
        return True

    # lst(key: year->month->word  value: word_info)
    def get_classified_lst(self):
        result = dict()
        result[0] = dict()
        result[1] = dict()
        for wrapped_word, word_info in self.dict_data.iteritems():
            year_and_month = self.get_year_and_month(word_info[u'date'])
            year = year_and_month[0]
            month = year_and_month[1]

            wrapped_list = wrapped_word.split('-')
            word = wrapped_list[0]
            word_come_from = int(wrapped_list[1])

            if year not in result[word_come_from]:
                result[word_come_from][year] = dict()
            if month not in result[word_come_from][year]:
                result[word_come_from][year][month] = dict()
            result[word_come_from][year][month][word] = word_info
        return result

    @staticmethod
    def get_year_and_month(date):
        d1 = date.split(' ')[0]
        d2 = d1.split('-')
        return d2[:2]


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)


if __name__ == "__main__":
    tackle_words = TackleWords()
    tackle_words.import_all_dir()

