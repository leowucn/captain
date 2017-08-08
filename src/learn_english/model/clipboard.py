# -*- coding:utf-8 -*-
import time
import pyperclip
import tackle_word
from time import gmtime, strftime
import pronunciation
import os
import utility
import extract
from nltk.stem import WordNetLemmatizer

interval = 2.5          # interval seconds for scanning clipboard
max_display_times = 3   # the times of repeating word pronunciation
timeout = 10            # wait no more than four seconds for show pronunciation.


tackle = tackle_word.TackleWords()
extractor = WordNetLemmatizer()


invalid_characters = {
    '[': True, ']': True,
    '@': True, '#': True,
    '^': True, '&': True,
    '&&': True, '||': True,
    '*': True, "==": True,
    "===": True, '\\': True,
    '/': True, '`': True,
    '=': True, '{': True,
    '}': True
}


def watcher():
    try:
        word = ''
        i = 0
        while True:
            result = pyperclip.paste().strip()
            if 1 <= len(result) <= 20 and result.isalpha():
                word = result
                i = 0
                os.system("echo '' | pbcopy")
            p('word = ' + word + ', result = ' + result + ', i = ' + str(i))
            if word != '' and len(result) > len(word) and result.find(word) >= 0 and is_valid_string(result):
                # print('word = ' + word + ', result = ' + result + ', i = ' + str(i))
                ori_form = extractor.lemmatize(word.lower(), pos='v')
                sentences = extract.extract(word, result)
                for sentence in sentences:
                    tackle.query(ori_form + '-1', sentence, strftime("%Y-%m-%d", gmtime()))
                os.system("echo '' | pbcopy")
            if word != '':
                if i >= max_display_times:
                    os.system("echo '' | pbcopy")
                    i = 0
                    word = ''
                    continue
                i += 1
                ori_form = extractor.lemmatize(word.lower(), pos='v')
                pronunciation.show(ori_form)
            time.sleep(interval)

    except BaseException as e:
        print(str(e))
        utility.show_notification('Captain Info', 'Sorry, some error may happened! Please check the error message!')


# whether the src is valid string, the code or the Chinese should be exclusive.
def is_valid_string(src):
    # src is valid only when in which it is contained ascii char
    if not all(ord(c) < 128 for c in src):
        return False
    for ch in src:
        # if ch in invalid_characters or not ch.isalpha():
        if ch in invalid_characters:
            return False
    return True


def p(c):
    print(c)

if __name__ == "__main__":
    watcher()
