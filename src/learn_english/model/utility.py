# -*- coding:utf-8 -*-
import socket
import platform
import os
import json
import requests
import bs4
import sys
import urllib2
import utility
import traceback
from nltk.stem import WordNetLemmatizer
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')


extractor = WordNetLemmatizer()


def show_notification(title, msg):
    if platform.system() == 'Darwin':
        strippend_msg = msg.strip()
        if strippend_msg == "":
            return
        command = "osascript -e \'tell app \"System Events\" to display notification \"" + strippend_msg.encode('utf-8') + "\" with title \"" + title.encode('utf-8') + "\"\'"
        os.system(command)
    return


def load_json_file(file_name):
    try:
        f = open(file_name, 'r')
        res = json.load(f)
        f.close()
        return res
    except:
        return dict()


def write_json_file(file_name, data):
    f = open(file_name, 'w')
    f.write(json.dumps(data, indent=2))
    f.close()


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '0.0.0.0'


def get_content_of_url(url):
    try:
        return urllib2.urlopen(url).read()
    except:
        return ''


def get_raw_content(url, mark):
    s = requests.session()
    s.keep_alive = False
    try:
        res = s.get(url)
    except:
        return
    soup = bs4.BeautifulSoup(res.content, 'lxml')
    return str(soup.find('div', attrs={'class': mark}))


def extract_info_from_raw(raw_content, mark):
    """
    :param raw_content:
    :param mark: extract content against mark
    :return:
    """
    try:
        point_one_index = raw_content.index(mark)
    except:
        return ''
    left_bracket_index = raw_content[point_one_index:].index('>') + point_one_index
    right_bracket_index = raw_content[point_one_index:].index('<') + point_one_index
    res = raw_content[left_bracket_index + 1:right_bracket_index]
    return res


def find_str(s, char):
    index = 0

    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index

            index += 1
    return -1


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


def get_now_minute():
    now = datetime.datetime.now()
    return now.minute


def g():
    print('---------------------------')
    for line in traceback.format_stack():
        print(line.strip())
    print('---------------------------')


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)


def append_log(content):
    with open('log.txt', 'a') as f:
        f.write(content + '\n')


# ip_addr = get_ip()


