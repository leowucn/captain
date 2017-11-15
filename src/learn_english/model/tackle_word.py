# -*- coding: utf-8 -*-
import os
from os.path import dirname, abspath
import datetime
import utility
from datetime import datetime
from get_word_meaning import get_word_meaning
import random
import time
import pronunciation
import database
import re

parent_dir = dirname(dirname(abspath(__file__)))
working_dir = os.getcwd()
absolute_prefix = os.path.join(working_dir, 'asset')
words_dir = os.path.join(parent_dir, 'asset/words')

dict_file = os.path.join(parent_dir, 'asset/dict.json')
clipboard_file = os.path.join(parent_dir, 'asset/clipboard.json')
builder_file = os.path.join(parent_dir, 'asset/builder.json')


'''
all types might appear in result queried from youdao.com.
'basic'           ------>基本释义
'usage'           ------>出现的语句
'phrase'          ------>词组短语
'synonyms'        ------>同近义词
'rel_word_tab'    ------>同根词
'discriminate'    ------>词语辨析
'collins'         ------>柯林斯
'date'            ------>单词录入时间
'index'           ------>index

word-0            represent word from word builder
word-1            represent word from clipboard
'''


class TackleWords:
    def __init__(self):
        self.words_definitions = database.get_word_definition_all()
        self.clipboard_data = database.get_clipboard_word_all()

    def save_word(self, data):
        if data['word'].endswith('-1'):
            if database.get_clipboard_word_by_word(data['word']) is None:
                data['usage'] = '✓' + data['usage'] + '\n'
                database.insert_clipboard_word(data)
            else:
                clip_word_info = database.get_clipboard_word_by_word(
                    data['word'])
                usage = clip_word_info['usage']
                if usage.find(data['usage']) < 0:
                    if not usage.endswith('\n'):
                        usage += '\n'
                usage += '✓' + data['usage'] + '\n'
                clip_word_info['usage'] = usage
                database.update_clipboard_word(clip_word_info)
            self.clipboard_data = database.get_clipboard_word_all()
        if database.get_word_definition_by_word(data['word']) is None:
            r = re.compile("[1-9]+\)").split(data['usage'])
            res = '\n@'.join(r)
            usage = '✓' + '\n✓'.join(res) + '\n'
            data['usage'] = unicode(usage, errors='replace')
            database.insert_word_definition(data)
        else:
            word_definition = database.get_word_definition_by_word(
                data['word'])
            usage = word_definition['usage']
            if usage.find(data['usage']) < 0:
                if not usage.endswith('\n'):
                    usage += '\n'
                usage += '✓' + data['usage'] + '\n'
                word_definition['usage'] = usage
                database.update_word_definition(word_definition)
        self.words_definitions = database.get_word_definition_all()

    def query(self, wrapped_word, usage=None, date=None, book=None):
        word_definition = dict()
        word_definition = database.get_word_definition_by_word(wrapped_word)
        if word_definition is not None:
            word_definition['usage'] = usage
        else:
            word_definition = get_word_meaning(wrapped_word)
            if word_definition is None:
                return
            if usage is not None:
                word_definition['usage'] = usage
            if date is not None:
                word_definition['date'] = date.strip()
            if book is not None:
                word_definition['book'] = book.strip()
        self.save_word(word_definition)
        return

    def import_words(self):
        files = [f for f in os.listdir(words_dir) if os.path.isfile(
            os.path.join(words_dir, f))]
        for file_name in files:
            if os.path.splitext(file_name)[1] != '.txt':
                continue
            file_path = os.path.join(words_dir, file_name)
            with open(file_path) as f:
                # All lines including the blank ones
                lines = (line.rstrip() for line in f)
                lines = list(line for line in lines if line)  # Non-blank lines
                for index, line in enumerate(lines):
                    if line[0].isdigit():
                        word = line[line.find('.') + 2:]
                        wrapped_word = word + '-0'
                        usage = lines[index +
                                      1][lines[index + 1].find(':') + 1:]
                        book = lines[index +
                                     2][lines[index + 2].find(':') + 1:]
                        self.query(wrapped_word, usage,
                                   file_name[:-4], book)
        for clip_word_info in self.clipboard_data:
            wrapped_word = clip_word_info['word'] + '-1'
            if database.get_clipboard_word_by_word(wrapped_word) is not None:
                continue
            self.query(
                wrapped_word, clip_word_info['usage'], clip_word_info['date'])
        utility.show_notification('Import Words', 'Success!')

    def delete(self, wrapped_word):
        database.delete_word_definition_by_word(wrapped_word)
        database.delete_clipboard_word_by_word(wrapped_word)

        splitted_word = wrapped_word.split('-')
        # delete from word builder
        if splitted_word[1] == '0':
            for file_name in os.listdir(words_dir):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(words_dir, file_name)
                    if '. ' + splitted_word[0] in open(file_path).read():
                        valid_lines_lst = []
                        with open(file_path) as f:
                            # All lines including the blank ones
                            lines = (line.rstrip() for line in f)
                            # Non-blank lines
                            lines = list(line for line in lines if line)
                            for index, line in enumerate(lines):
                                if line[0].isdigit():
                                    word = line[line.find(
                                        '.') + 2:].strip()
                                    if word == splitted_word[0]:
                                        continue
                                    valid_lines_lst.append(line + '\n')
                                    valid_lines_lst.append(
                                        lines[index + 1] + '\n')
                                    valid_lines_lst.append(
                                        lines[index + 2] + '\n')
                                    valid_lines_lst.append(
                                        lines[index + 3] + '\n')
                                    valid_lines_lst.append('\n')
                        with open(file_path, "w") as f:
                            for line in valid_lines_lst:
                                f.write(line)
                        break
        return

    # lst(key: year->date->word  value: word_info)
    def get_classified_lst(self):
        result = dict()
        result[0] = dict()
        result[1] = dict()
        for word_definition in self.words_definitions:
            t = word_definition['date'].split(' ')[0].split('-')
            year = t[0]
            month = t[1]

            w = word_definition['word'].split('-')
            word = w[0]
            where = int(w[1])

            if year not in result[where]:
                result[where][year] = dict()
            if where == 1:
                if month not in result[where][year]:
                    result[where][year][month] = []
                result[where][year][month].append(word_definition)
            else:
                word_date = word_definition['date']
                if word_date not in result[where][year]:
                    result[where][year][word_date] = []
                result[where][year][word_date].append(word_definition)
        return result

    def emit_random_word(self):
        random_word = random.choice(self.words_definitions)[:-2]
        pronunciation.show(random_word)
        time.sleep(1.5)
        pronunciation.show(random_word)
        time.sleep(1.5)
        pronunciation.show(random_word)
        time.sleep(2)

    # 获取随机单词，用于复习使用
    def memorize_words(self):
        now_minute = utility.get_now_minute()
        if 0 <= now_minute <= 5:
            self.emit_random_word()
        elif 25 <= now_minute <= 30:
            self.emit_random_word()


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)


if __name__ == "__main__":
    tackle_words = TackleWords()
    tackle_words.import_words()
