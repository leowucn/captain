# !/usr/bin/env python
# -*- coding: utf-8 -*-
import re


def extract(word, paragraph):
    # If the paragraph which contains word is not too long, then return it.
    if len(paragraph) <= 160:
        return [paragraph]
    sentences = []
    indices = [m.start() for m in re.finditer(word, paragraph)]
    for index in indices:
        extract_content = get_backward_content(paragraph[:index]) + get_forward_content(paragraph[index:])
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


# example = 'We believe ourselves to be honest, innocent, well meaning' \
#           ' and kind people. For the most part, we are but we are also' \
#           ' born with some qualities that cause friction in life without' \
#           ' us even realizing it. Just because we never intended to be the ' \
#           'bad one does not mean that we are incapable of causing pain to others.'
# r = extract('we', example)
# print(r)
# get_backward_content('hello. this is a example')
# get_forward_content('hello. this is a example')
