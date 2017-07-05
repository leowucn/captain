# !/usr/bin/env python
# -*- coding: utf-8 -*-
en_verbs_path = 'src/learn_english/asset/en_verbs/en-verbs.txt'


def generate_dic():
    en_verbs_dic = dict()
    with open(en_verbs_path) as f:
        for line in f:
            if line.startswith(';;;'):
                continue
            separator_indices = []
            for i, c in enumerate(line):
                if i + 1 < len(line):
                    if c != ',' and line[i + 1] == ',':
                        separator_indices.append(i + 1)
            original_form = ''
            if len(separator_indices) >= 0:
                original_form = extract_word(line, separator_indices[0])
            derived_forms = []
            if len(separator_indices) >= 1:
                for index in separator_indices[1:]:
                    derived_forms.append(extract_word(line, index))
            for form in derived_forms:
                en_verbs_dic[form] = original_form
    return en_verbs_dic


def extract_word(line, separator_index):
    res = []
    for c in line[separator_index - 1::-1]:
        if c == ',':
            break
        res.append(c)
    return ''.join(res)[::-1]


# l = 'convolute,,,convolutes,,convoluting,,,,,convoluted,convoluted,,,,,,,,,,,,'
# generate_dic()
# extract_word(l, 1)