# -*- coding: utf-8 -*-
import re
import bs4
import utility
import datetime


word_type = ('n.', 'v.', 'pron.', 'adj.', 'adv.', 'num.', 'art.',
             'prep.', 'conj.', 'int.', 'vi.', 'vt.', 'aux.', 'aux.v')


def get_word_meaning(wrapped_word):
    word = wrapped_word[:-2].strip()
    word_list = re.compile('\w+').findall(word)
    post_fix = '%20'.join(word_list)

    url = 'http://www.youdao.com/w/eng/' + post_fix
    content = utility.get_content_of_url(url)
    soup = bs4.BeautifulSoup(content, 'lxml')
    word_meaning_dict = dict()

    # ----------------------basic-----------------------
    basic = soup.find('div', attrs={'class': 'baav'})
    basic_str = ''
    if basic is not None:
        basic_str += ' '.join(list(basic.stripped_strings)) + '\n'
    basic = soup.find("div", id="phrsListTab")
    if basic is not None:
        result = basic.find('div', attrs={'class': 'trans-container'})
        if result is not None:
            basic_str += result.ul.get_text().strip('\n')

    # if basic_str of word is '', we can make sure that this word or phrase does not exist.
    if basic_str == '':
        return None
    word_meaning_dict['basic'] = basic_str

    # -------------------词组短语---------------------
    result = soup.find('div', id='transformToggle')
    if result is not None:
        phrase = result.find('div', id='wordGroup')
        if phrase is not None:
            phrase_str = ''
            for i, s in enumerate(phrase.stripped_strings):
                r = s.replace('\n', '')
                if r.find(word) >= 0:
                    if i + 1 >= len(list(phrase.stripped_strings)):
                        break
                    phrase_str += r + '     ' + \
                        re.sub('\s*', '', list(phrase.stripped_strings)
                               [i + 1]) + '\n'
            if len(phrase_str) != 0:
                word_meaning_dict['phrase'] = phrase_str.strip('\n')

    # -------------------同近义词---------------------
    result = soup.find('div', id='transformToggle')
    if result is not None:
        synonyms = result.find('div', id='synonyms')
        if synonyms is not None:
            synonyms_str = ''
            lst = []
            for s in synonyms.stripped_strings:
                lst.append(s)

            i_next_index = 0
            for i, s in enumerate(lst):
                if i < i_next_index:
                    continue

                if is_start_word_type(s):
                    synonyms_str += s + '\n'

                    j_next_index = 0
                    j_begin = i + 1
                    for j, d in enumerate(lst[j_begin:]):
                        if j < j_next_index:
                            continue
                        if is_start_word_type(d):
                            i_next_index = j_begin + j
                            synonyms_str += '\n'
                            break
                        if d == ',':
                            synonyms_str += ', '
                        else:
                            synonyms_str += d
            word_meaning_dict['synonyms'] = synonyms_str.strip('\n')

    # -------------------同根词---------------------
    result = soup.find('div', id='transformToggle')
    if result is not None:
        rel_word_tab = result.find('div', id='relWordTab')
        if rel_word_tab is not None:
            rel_word_tab_str = ''

            is_found = False
            for i, s in enumerate(rel_word_tab.stripped_strings):
                if s == u'词根：':
                    rel_word_tab_str += s + ' ' + \
                        list(rel_word_tab.stripped_strings)[i + 1] + '\n'
                    is_found = True
                    continue
                if is_found:
                    is_found = False
                    continue
                if s.find('.') >= 0:
                    rel_word_tab_str += s + '\n'
                elif s.encode(
                        'utf-8').isalpha():  # without "encode('utf-8')", the Chinese symbol is recognized as alpha
                    rel_word_tab_str += s + '   '
                else:
                    if len(rel_word_tab_str) > 0:
                        rel_word_tab_str += s + '\n'
                    else:
                        rel_word_tab_str += s
            word_meaning_dict['rel_word_tab'] = rel_word_tab_str.strip('\n')

    # -------------------词语辨析---------------------
    result = soup.find('div', id='transformToggle')
    if result is not None:
        discriminate = result.find('div', id='discriminate')
        if discriminate is not None:
            discriminate_str = ''
            is_found = False
            for i, s in enumerate(discriminate.stripped_strings):
                if is_found:
                    is_found = False
                    continue
                if is_alpha_and_x(s, ','):
                    discriminate_str += '\n' + s + '\n'
                    attach = list(discriminate.stripped_strings)[i + 1] + '\n'
                    is_found = True
                    if whether_start_with_alpha(attach):
                        continue
                    else:
                        discriminate_str += attach
                    continue
                if whether_only_alpha(s):
                    discriminate_str += s + '   '
                if whether_has_non_alpha_symbol(s) and s != u'以上来源于' and s != u'网络':
                    discriminate_str += s + '\n'
            word_meaning_dict['discriminate'] = discriminate_str.strip('\n')

    # ---------------------collins---------------------
    collins = soup.find('div', id="collinsResult")
    if collins is not None:
        text_list = []
        for i, s in enumerate(collins.stripped_strings):
            # tackle special formation problem
            text_list.append(' '.join(s.split()))

        line = ' '.join(text_list[3:])
        collins_str = re.sub('例：', '\n例：', line)
        collins_str = re.sub("\d+\.", "\n*", collins_str)
        collins_str = collins_str[collins_str.find('*'):]
        if len(collins_str.strip()) > 1:
            word_meaning_dict['collins'] = collins_str.encode('utf-8')

    word_meaning_dict['word'] = wrapped_word
    word_meaning_dict['date'] = str(datetime.datetime.now())[:-7]
    return word_meaning_dict


def is_alpha_and_x(src_str, x):
    has_alpha = False
    has_x = False
    for s in src_str.encode('utf-8'):
        if s.isalpha():
            has_alpha = True
            continue
        elif s == str(x):
            has_x = True
            continue
        elif s == str(' '):
            continue
        else:
            return False
    if has_alpha and has_x:
        return True
    return False


def whether_start_with_alpha(src_str):
    for s in src_str.encode('utf-8'):
        if s.isalpha():
            return True
    return False


def whether_has_non_alpha_symbol(src_str):
    for s in src_str.encode('utf-8'):
        if not s.isalpha():
            return True
    return False


def whether_only_alpha(src_str):
    for s in src_str.encode('utf-8'):
        if not s.isalpha():
            return False
    return True


def is_start_word_type(src):
    for w_type in word_type:
        if src.strip().startswith(w_type):
            return True
    return False


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)
