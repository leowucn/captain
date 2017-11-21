# -*- coding: utf-8 -*-
"""
emit pronunciation
"""
import re
import urllib
import subprocess
import time
import os
import string
from threading import Thread
import requests
import bs4
import utility
import database
import constants


def show(word):
    thread_first = Thread(target=show_literal_pronunciation, args=(word,))
    thread_second = Thread(target=launch_pronunciation, args=(word,))

    thread_first.start()
    thread_second.start()

    thread_first.join()
    thread_second.join()


def launch_pronunciation(word):
    if not word[0].startswith(tuple(string.ascii_letters)):
        return
    stripped_word = word.strip().lower()
    if len(stripped_word) == 0:
        return
    dst_dir = os.path.join(constants.PRONUNCIATION_DIR, stripped_word[0])
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        get_pronunciation(stripped_word, dst_dir)
        return
    else:
        files = [f for f in os.listdir(
            dst_dir) if os.path.isfile(os.path.join(dst_dir, f))]
        d = dict()
        for filename in files:
            if os.path.splitext(filename)[0] == stripped_word + '-uk':
                d['uk'] = os.path.join(dst_dir, filename)
            if os.path.splitext(filename)[0] == stripped_word + '-us':
                d['us'] = os.path.join(dst_dir, filename)
        if len(d) > 0:
            if 'uk' in d:
                subprocess.Popen(['mpg123', '-q', d['uk']]).wait()
                time.sleep(constants.PRONUNCIATION_INTERVAL)
            if 'us' in d:
                subprocess.Popen(['mpg123', '-q', d['us']]).wait()
        else:
            get_pronunciation(stripped_word, dst_dir)
            return
    return


def get_pronunciation(word, dst_dir):
    """
    include British and American pronunciation.
    """
    url = 'http://dictionary.cambridge.org/dictionary/english/' + word
    content = utility.get_content_of_url(url)
    mp3_pos_lst = [m.start() for m in re.finditer('data-src-mp3', content)]
    ogg_pos_lst = [m.start() for m in re.finditer('data-src-ogg', content)]
    if len(mp3_pos_lst) == 0 or len(ogg_pos_lst) == 0:
        return
    if len(mp3_pos_lst) >= 2 and len(ogg_pos_lst) >= 2:
        mp3_pos_lst = mp3_pos_lst[:2]
        ogg_pos_lst = ogg_pos_lst[:2]
    else:
        min_len = min(len(mp3_pos_lst), len(ogg_pos_lst))
        mp3_pos_lst = mp3_pos_lst[:min_len]
        ogg_pos_lst = ogg_pos_lst[:min_len]

    url_lst = []
    try:
        offset = 14     # len('data-src-mp3') + 2 or len('data-src-ogg') + 2
        for i in range(len(mp3_pos_lst)):
            url_lst.append(
                content[mp3_pos_lst[i] + offset: ogg_pos_lst[i] - 2])
    except:
        return

    mp3_name_lst = []
    if len(url_lst) == 1:
        file_extension_uk = os.path.splitext(url_lst[0])[1]
        name_uk = os.path.join(dst_dir, word + '-uk' + file_extension_uk)
        mp3_name_lst.append(name_uk)
        urllib.urlretrieve(''.join(url_lst[0]), name_uk)
    else:
        file_extension_uk = os.path.splitext(url_lst[0])[1]
        name_uk = os.path.join(dst_dir, word + '-uk' + file_extension_uk)
        mp3_name_lst.append(name_uk)
        urllib.urlretrieve(''.join(url_lst[0]), name_uk)

        file_extension_us = os.path.splitext(url_lst[0])[1]
        name_us = os.path.join(dst_dir, word + '-us' + file_extension_us)
        mp3_name_lst.append(name_us)
        urllib.urlretrieve(''.join(url_lst[1]), name_us)

    for name in mp3_name_lst:
        if os.path.isfile(name):
            subprocess.Popen(['mpg123', '-q', name]).wait()
            time.sleep(constants.PRONUNCIATION_INTERVAL)


def show_literal_pronunciation(word):
    if not word[0].startswith(tuple(string.ascii_letters)):
        return
    stripped_word = word.strip()
    if not stripped_word.isalpha():
        return
    basic = database.get_word_basic_by_word(word)
    if basic is None:
        result = get_text_pronunciation(stripped_word)
        if len(result) == 0:
            return
        if result['pronun'] == "" or result['basic'] == "":
            return
        basic = dict()
        basic['word'] = word
        basic['pronun'] = result['pronun']
        basic['basic'] = result['basic']
        database.insert_word_basic(basic)

    literal = basic['pronun'].replace("'", ".")
    literal = literal.replace("ˈ", ".")

    utility.show_notification(
        word + ' -> ' + literal.encode('utf-8'), basic['basic'].encode('utf-8'))
    return


def get_text_pronunciation(word):
    basic = dict()
    url = 'http://www.youdao.com/w/eng/' + word.lower().strip()
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content, 'lxml')
    pronunciation = soup.find('div', attrs={'class': 'baav'})
    if pronunciation is not None:
        basic['pronun'] = ' '.join(list(pronunciation.stripped_strings))
    else:
        basic['pronun'] = ''

    # ----------------------basic definition-----------------------
    basic_soup = soup.find("div", id="phrsListTab")
    if basic_soup is not None:
        result = basic_soup.find('div', attrs={'class': 'trans-container'})
        if result is not None:
            basic['basic'] = result.ul.get_text().strip('\n')
        else:
            basic['basic'] = ''
    else:
        basic['basic'] = ''
    return basic

# launch_pronunciation('agree')
# show_literal_pronunciation('agree')
