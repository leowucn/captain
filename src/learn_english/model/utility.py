# -*- coding:utf-8 -*-
import socket
import platform
import os
import json
import requests
import bs4
import sys
import urllib2
import traceback
import utility
reload(sys)
sys.setdefaultencoding('utf-8')


def show_notification(title, msg):
    if platform.system() == 'Darwin':
        strippend_msg = msg.strip()
        if strippend_msg == "":
            return
        command = "osascript -e \'tell app \"System Events\" to display notification \"" + strippend_msg.encode('utf-8') + "\" with title \"" + title.encode('utf-8') + "\"\'"
        os.system(command)
    return


def load_json_file(file_path):
    feeds = dict()
    if os.path.exists(file_path):
        with open(file_path) as fp:
            return json.load(fp)
    return feeds


def write_json_file(file_name, data):
    if data is None:
        return
    with open(file_name, mode='w') as f:
        f.write(json.dumps(data, indent=2))


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
    res = res.replace('&amp;', '&')
    return res


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


ip_addr = get_ip()
