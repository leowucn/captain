# !/usr/bin/env python
# -*- coding: utf-8 -*-
import re


invalid_characters = {
    '@': True, '#': True,
    '^': True, '&': True,
    '&&': True, '||': True,
    '*': True, "==": True,
    "===": True, '\\': True,
    '/': True, '`': True,
    '=': True, '{': True,
    '}': True
}


def extract(word, paragraph):
    # If the paragraph which contains word is not so long, then return it.
    if len(paragraph) <= 160:
        return [paragraph]
    sentences = []
    indices = [m.start() for m in re.finditer(word, paragraph)]
    for index in indices:
        if index > 0 and paragraph[index-1] != ' ':
            continue
        if index < len(paragraph)-1:
            if paragraph[index+len(word)] != ' ' and paragraph[index+len(word)] != '.':
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
    for c in paragraph[::-1]:
        if c == '.' or c == '!' or c == '?':
            break
        res.append(c)
    return ''.join(res)[::-1]


def get_forward_content(paragraph):
    """ extract the content from paragraph between
     the head of paragraph or the index of symbols
      like '.', '!' which appear. """
    res = []
    for c in paragraph:
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


example = '''Having said that, I'm a nurse at the VA hospital.  We were required to take a 3 day course on "Reigniting the Spirit of Care".  I knew I'd hate it because it's pretty spiritual and I'm the least spiritual thing around.'''
r = extract('it', example)
print(r)
# get_backward_content('hello. this is a example')
# get_forward_content('hello. this is a example')
