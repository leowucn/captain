# -*- coding:utf-8 -*-
import time
import pyperclip
import tackle_word
from time import gmtime, strftime
import pronunciation
import os
import extract
from nltk.stem import WordNetLemmatizer
import utility

interval = 2            # interval seconds for scanning clipboard
max_display_times = 3   # the times of repeating word pronunciation


tackle = tackle_word.TackleWords()
extractor = WordNetLemmatizer()


valid_characters = {
    '‐': True, '‒': True,
    '–': True, '—': True,
    '―': True, '‖': True,
    '‗': True, '‘': True,
    '’': True, '‚': True,
    '‛': True, '“': True,
    '”': True, '„': True,
    '‟': True, '…': True,
}


def watcher():
    word = ''
    i = 0
    while True:
        result = pyperclip.paste().strip()
        if 1 < len(result) <= 20 and result.isalpha():
            word = result
        if word != '' and len(result) > len(word) and result.find(word) >= 0 and is_valid_string(result):
            # p('word = ' + word + ', result = ' + result + ', i = ' + str(i))
            ori_form = get_word_original_form(word)
            sentences = extract.extract(word, result)
            if len(sentences) == 0:
                continue
            for sentence in sentences:
                tackle.query(ori_form + '-1', sentence, strftime("%Y-%m-%d", gmtime()))
            tackle.update_clipboard()
            os.system("echo '' | pbcopy")
        # p(word)
        if word != '':
            if i >= max_display_times:
                os.system("echo '' | pbcopy")
                i = 0
                word = ''
                continue
            i += 1
            ori_form = get_word_original_form(word)
            pronunciation.show(ori_form)
        time.sleep(interval)
    utility.show_notification('Clipboard motinor Error!', 'Some error happened1')


# whether the src is valid string, the code or the Chinese should be exclusive.
def is_valid_string(src):
    for c in src:
        if str(c) in valid_characters:
            continue
        if ord(c) > 127:
            p(c + ' ' + str(ord(c)))
            return False
    return True


def get_word_original_form(word):
    word = word.lower()

    ori_form = extractor.lemmatize(word, pos='v')
    if word != ori_form:
        return ori_form
    else:
        ori_form = extractor.lemmatize(word, pos='n')
        if word != ori_form:
            return ori_form
        else:
            ori_form = extractor.lemmatize(word, pos='a')
            if word != ori_form:
                return ori_form
    return word


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)

if __name__ == "__main__":
    watcher()
