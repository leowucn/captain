# !/usr/bin/env python
# -*- coding: utf-8 -*-
import re


invalid_characters = {
    '@': True, '#': True,
    '^': True, '&': True,
    '&&': True, '||': True,
    '*': True, "==": True,
    "===": True, '\\': True,
    '}': True, '`': True,
    '=': True, '{': True
}


def extract(word, paragraph):
    # If the paragraph which contains word is not so long, then return it.
    if len(paragraph) <= 160:
        return [paragraph]
    sentences = []
    indices = [m.start() for m in re.finditer(word, paragraph)]
    for index in indices:
        if index > 0 and paragraph[index-1].isalpha():
            continue
        if index < len(paragraph)-1:
            if paragraph[index+len(word)].isalpha():
                continue
        extract_content = get_backward_content(paragraph[:index]) + get_forward_content(paragraph[index:])
        extract_content = extract_content.strip() + '\n'
        if is_valid_string(extract_content):
            sentences.append(extract_content.strip() + '\n')
    return list(set(sentences))


def get_backward_content(paragraph):
    """ extract the content from paragraph between
     the head of paragraph or the index of symbols
      like '.', '!' which appear. """
    res = []
    for i, c in enumerate(paragraph[::-1]):
        if i < 80:
            res.append(c)
            continue
        if c == '.' or c == '!' or c == '?':
            break
        res.append(c)
    return ''.join(res)[::-1]


def get_forward_content(paragraph):
    """ extract the content from paragraph between
     the head of paragraph or the index of symbols
      like '.', '!' which appear. """
    res = []
    for i, c in enumerate(paragraph):
        if i < 80:
            res.append(c)
            continue
        if c == '.' or c == '!' or c == '?':
            res.append(c)
            break
        res.append(c)
    return ''.join(res)


def is_valid_string(src):
    for ch in src:
        if ch in invalid_characters:
            return False
    return True


def p(c):
    print(c)


# example = '''Via this IP address it’s possible to customize the default gateway. To reach an administrative console you have to paste link http://192.168.0.1 into your web-browser. This act is from the system administrator’s arsenal, but any user of the above-mentioned devices can do it yourself.'''
# example = '''However,Mrs. Elliot received a lot of hate for doing that. People said that this was absolutely unacceptable, and everyone was avoiding her.'''
# r = extract('said', example)
# print(r)
# get_backward_content('hello. this is a example')
# get_forward_content('hello. this is a example')
