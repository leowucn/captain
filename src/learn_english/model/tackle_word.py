# -*- coding: utf-8 -*-
"""
do some stuff for tackling word
"""
import os
import io
import re
import random
import time
import utility
from get_word_meaning import get_word_meaning
import pronunciation
import database
import constants


class TackleWords:
    def __init__(self):
        pass

    def save_word(self, data):
        if data['word'].endswith('-1'):
            if database.get_clipboard_word_by_word(data['word']) is None:
                data['usage'] = utility.get_refined_usages(data['usage'])
                database.insert_clipboard_word(data)
            else:
                clip_word_info = database.get_clipboard_word_by_word(
                    data['word'])
                clip_word_info['usage'], ok = utility.get_concatinated_usages(
                    clip_word_info['usage'], data['usage'])
                if ok:
                    database.update_clipboard_word(clip_word_info)
        if database.get_word_definition_by_word(data['word']) is None:
            if not data['usage'].startswith(constants.USAGE_PREFIX):
                data['usage'] = utility.get_refined_usages(
                    data['usage'])
            database.insert_word_definition(data)
        else:
            word_definition = database.get_word_definition_by_word(
                data['word'])
            word_definition['usage'], ok = utility.get_concatinated_usages(
                word_definition['usage'], data['usage'])
            if ok:
                database.update_word_definition(word_definition)

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
        files = [f for f in os.listdir(constants.KINDLE_WORDS_DIR) if os.path.isfile(
            os.path.join(constants.KINDLE_WORDS_DIR, f))]
        for file_name in files:
            if os.path.splitext(file_name)[1] != '.txt':
                continue
            file_path = os.path.join(constants.KINDLE_WORDS_DIR, file_name)
            with io.open(file_path, mode="r", encoding="utf-8") as f:
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
                        wrapped_word = utility.get_word_original_form(
                            word) + '-0'
                        self.query(wrapped_word,  usage,
                                   file_name[:-4], book)
        clipboard_data = database.get_clipboard_word_all()
        for clip_word_info in clipboard_data:
            wrapped_word = clip_word_info['word']
            if database.get_word_definition_by_word(wrapped_word) is not None:
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
            for file_name in os.listdir(constants.KINDLE_WORDS_DIR):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(
                        constants.KINDLE_WORDS_DIR, file_name)
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

    def get_classified_lst(self):
        """
            lst(key: year->date->word  value: word_info)
        """
        result = dict()
        result[0] = dict()
        result[1] = dict()

        words_definitions = database.get_word_definition_all()
        for word_definition in words_definitions:
            t = word_definition['date'].split(' ')[0].split('-')
            year = t[0]
            month = t[1]

            wrapped_word = word_definition['word']
            where = int(wrapped_word[len(wrapped_word) - 1])

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
        words_definitions = database.get_word_definition_all()
        random_word = random.choice(words_definitions)[:-2]
        pronunciation.show(random_word)
        time.sleep(1.5)
        pronunciation.show(random_word)
        time.sleep(1.5)
        pronunciation.show(random_word)
        time.sleep(2)

    def memorize_words(self):
        """
        获取随机单词，用于复习使用
        """
        now_minute = utility.get_current_minute()
        if 0 <= now_minute <= 5:
            self.emit_random_word()
        elif 25 <= now_minute <= 30:
            self.emit_random_word()


if __name__ == "__main__":
    TackleWords().import_words()
