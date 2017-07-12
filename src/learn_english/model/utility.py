# -*- coding:utf-8 -*-
import socket
import platform
import os
import urllib
import traceback
import json
import requests
import bs4
import sys
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
        with open(file_path, 'r') as fp:
            return json.load(fp)
    return feeds


def write_to_json_file(file_name, data):
    feeds = dict()
    if os.path.exists(file_name):
        with open(file_name) as feeds_json:
            feeds = json.load(feeds_json)
    for word, verbose_info in data.iteritems():
        feeds[word] = verbose_info
    with open(file_name, mode='w') as f:
        f.write(json.dumps(feeds, indent=2))


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '0.0.0.0'


def get_raw_content(url, mark):
    if not test_network("https://www.vocabulary.com/"):
        return ''
    s = requests.session()
    s.keep_alive = False
    try:
        res = s.get(url)
    except:
        print_stack(55)
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


def test_network(url):
    code = urllib.urlopen(url).getcode()
    if code != 200:
        return False
    return True


def print_stack(c):
    print_stack('---------------------')
    print(c)
    traceback.print_exc()


ip_addr = get_ip()
