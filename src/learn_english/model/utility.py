# -*- coding:utf-8 -*-
"""
utility function
"""
import platform
import os
import re
import json
import sys
import urllib2
import datetime
import bs4
import requests
from nltk.stem import WordNetLemmatizer
import constants
from datetime import date
import calendar
reload(sys)
sys.setdefaultencoding('utf-8')


REVEAL_ORIGINAL_FORM = WordNetLemmatizer()


def show_notification(title, msg):
    if platform.system() == 'Darwin':
        strippend_msg = msg.strip()
        if strippend_msg == "":
            return
        command = "osascript -e \'tell app \"System Events\" to display notification \"" + \
            strippend_msg.encode('utf-8') + "\" with title \"" + \
            title.encode('utf-8') + "\"\'"
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
    left_bracket_index = raw_content[point_one_index:].index(
        '>') + point_one_index
    right_bracket_index = raw_content[point_one_index:].index(
        '<') + point_one_index
    res = raw_content[left_bracket_index + 1:right_bracket_index]
    return res


def get_day_of_week():
    my_date = date.today()
    return calendar.day_name[my_date.weekday()]


def get_word_original_form(word):
    word = word.strip().lower()
    ori_form = REVEAL_ORIGINAL_FORM.lemmatize(word, pos='n')
    if word != ori_form:
        return ori_form
    else:
        ori_form = REVEAL_ORIGINAL_FORM.lemmatize(word, pos='a')
        if word != ori_form:
            return ori_form
        else:
            ori_form = REVEAL_ORIGINAL_FORM.lemmatize(word, pos='v')
            if word != ori_form:
                return ori_form
    return word


def get_concatinated_usages(dst_usage, new_usage):
    new_usage = new_usage.replace(constants.USAGE_PREFIX, '')
    new_usage_lst = new_usage.split('\n')
    ok = False
    for usage in new_usage_lst:
        if dst_usage.find(usage) < 0:
            if not usage.endswith('\n') and len(usage) > 0:
                usage += '\n'
            if not dst_usage.endswith('\n') and len(dst_usage) > 0:
                dst_usage += '\n'
            dst_usage += get_refined_usages(usage)
            ok = True
    return dst_usage, ok


def get_refined_usages(raw_usages):
    lst = re.compile('[0-9]+\)').split(raw_usages)
    if len(lst) == 1:
        return constants.USAGE_PREFIX + lst[0]
    return constants.USAGE_PREFIX + ('\n' + constants.USAGE_PREFIX).join(lst[1:])


def get_current_minute():
    return int(datetime.datetime.now().strftime("%M"))


def get_current_seconds():
    return int(datetime.datetime.now().strftime("%S"))


def log2file(content):
    append_log('---------------------')
    append_log(str(content))


def append_log(content):
    with open('log.txt', 'a') as f:
        f.write(content + '\n')

# print(get_word_original_form('apples'))
