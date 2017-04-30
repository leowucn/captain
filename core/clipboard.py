# -*- coding:utf-8 -*-
import time
import pyperclip
import tackle_word
from time import gmtime, strftime
import pronunciation
import os
import utility
import multiprocessing
import re

interval = 2.5    # interval seconds for scanning clipboard
times = 3   # the times of repeating word pronunciation
max_length = 600    # the maximum length of word usage.
timeout = 10     # wait no more than four seconds for show pronunciation.


def watcher():
    try:
        word = ''
        i = 0
        while True:
            result = pyperclip.paste().strip().lower()
            if len(result) >= max_length:
                continue
            if result.isalpha() and len(result) >= 1 and word != result:
                word = result
                i = 0
            # print('word = ' + word + ', result = ' + result + ', i = ' + str(i))
            if word != '' and len(result) > len(word) and result.find(word) >= 0 and is_valid_string(result):
                alpha_lst = " ".join(re.findall("[a-zA-Z]+", result))
                if len(alpha_lst) - len(word) > 5:
                    # in this case, result should be a usage containing the
                    # corresponding result which was supposed to be a word or phrase.
                    tackle = tackle_word.TackleWords()
                    tackle.query(word + '-1', result, strftime("%Y-%m-%d", gmtime()))
                os.system("echo '' | pbcopy")
            if word != '':
                if i >= times:
                    if result == word:
                        os.system("echo '' | pbcopy")
                    i = 0
                    word = ''
                    continue
                i += 1

                p1 = multiprocessing.Process(target=pronunciation.show_literal_pronunciation, args=(word,))
                p2 = multiprocessing.Process(target=pronunciation.launch_pronunciation, args=(word,))
                p1.start()
                p2.start()
                # Wait timeout seconds or until process finishes
                p1.join(timeout)
                p2.join(timeout)
                # If thread is still active
                if p1.is_alive():
                    print "p1 running... let's kill it..."
                    # Terminate
                    p1.terminate()
                    p1.join()
                if p2.is_alive():
                    print "p2 running... let's kill it..."
                    # Terminate
                    p2.terminate()
                p2.join()
            time.sleep(interval)
    except:
        utility.show_notification('Captain Info', 'Sorry, some error may happened! Please check the error message!')


# whether the src is valid string, the code or the Chinese should be exclusive.
def is_valid_string(src):
    invalid_characters = {'.': True, '[': True, ']': True, '@': True, '#': True, '^': True, '&': True, '&&': True, '||': True, '*': True, "==": True, "===": True, '\\': True, '/': True, '`': True}
    for ch in src:
        if ch in invalid_characters:
            return False
    return True

if __name__ == "__main__":
    watcher()
