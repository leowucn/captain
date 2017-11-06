# -*- coding:utf-8 -*-
import time
import pyperclip
import tackle_word
from time import gmtime, strftime
import pronunciation
import os
import extract
import utility

interval = 2            # interval seconds for scanning clipboard
max_display_times = 4   # the times of repeating word pronunciation
tackle = tackle_word.TackleWords()


def watcher():
    word = ''
    ori_form = ''
    i = 0
    while True:
        result = pyperclip.paste().strip()
        if not is_valid(result):
            # p("sentence not valid!")
            time.sleep(interval)
            continue
        # p('word = ' + word + ' , i = ' + str(i) + ' ' + ', result = ' + result)
        if word != '' and result.find(word) >= 0:
            if word != '' and len(result) > len(word) and result.find(word) >= 0:
                sentences = extract.extract(word, result)
                if len(sentences) > 0:
                    for sentence in sentences:
                        tackle.query(ori_form + '-1', sentence, strftime("%Y-%m-%d", gmtime()))
            if word != '':
                if i >= max_display_times:
                    os.system("echo '' | pbcopy")
                    i = 0
                    word = ''
                    continue
                i += 1
                pronunciation.show(ori_form)
        elif 1 < len(result) <= 20 and result.isalpha():
            word = result
            ori_form = utility.get_word_original_form(word)
            i = 0
            continue

        # When the following condition are sufficient, Captain would look like suspend, and copy word 
        # has no any effect. This is normal, as now is the time for memorizing the word learned.
        tackle.memorize_words()
        time.sleep(interval)


# clip_str should only include ascii characters.
def is_valid(clip_str):
    # for c in clip_str:
    #     if ord(c) > 127:
    #         return False
    return True


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)


if __name__ == "__main__":
    watcher()
