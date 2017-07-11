# -*- coding:utf-8 -*-
import socket
import platform
import os
import urllib
import json
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


def test_network():
    code = urllib.urlopen("http://www.youdao.com").getcode()
    if code != 200:
        return False
    return True


def p(c):
    print(c)


ip_addr = get_ip()
