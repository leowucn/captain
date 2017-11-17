#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, request, Blueprint, redirect, url_for
import os
import time
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "model")))
import tackle_word
import pronunciation
import motto
import vocabulary_list
import utility


each_page_words_num = 10
current_dir = os.path.dirname(os.path.abspath(__file__))
stop = False    # stop quickly review


learn_english_app = Blueprint(
    "learn_english", __name__, static_folder='../static', template_folder='../templates')


@learn_english_app.route('/', methods=['GET', 'POST'])
def show_year_list():
    tackle = tackle_word.TackleWords()
    res = tackle.get_classified_lst()

    if len(res) == 0:
        return render_template('congratulation.html')

    year_dict = dict(res[0].items() + res[1].items()).keys()

    all_vocabulary_dict = vocabulary_list.get_all_vocabulary_lists()
    result = dict()
    for category_name, category_lists in all_vocabulary_dict.iteritems():
        i = 0
        result[category_name] = dict()
        for list_name, list_data in category_lists.iteritems():
            if i >= 4:
                break
            result[category_name][list_name] = dict()
            result[category_name][list_name] = list_data
            i += 1
    return render_template('home.html', year_lst=sorted(year_dict), all_vocabulary_lists=result)


@learn_english_app.route('/word_date_list', methods=['GET', 'POST'])
def show_word_date_list():
    if request.method == 'POST':
        tackle = tackle_word.TackleWords()
        res = tackle.get_classified_lst()

        words_date_list_from_kindle = []
        words_date_list_from_clipboard = []
        year = request.form.keys()[0].split('-')[0]

        if year in res[0]:
            for timestamp, words_list in res[0][year].iteritems():
                words_date_list_from_kindle.append(timestamp)
        if len(res) > 1:
            if year in res[1]:
                for month, words_dict in res[1][year].iteritems():
                    words_date_list_from_clipboard.append(month)
        return render_template('word_date_list.html', year=year, words_date_list_from_kindle=sorted(words_date_list_from_kindle), words_date_list_from_clipboard=sorted(words_date_list_from_clipboard))
    return render_template('nothing.html')


@learn_english_app.route('/words_list', methods=['GET', 'POST'])
def words_list():
    if request.method == 'POST':
        lst = request.form.keys()[0].split('*')
        come_from = lst[0]
        year = lst[1]
        month = lst[2]

        return show_page(come_from, year, month, 0)
    return render_template('nothing.html')


@learn_english_app.route('/show_words_list/<come_from>/<year>/<month>/<index>')
def show_words_list(come_from, year, month, index):
    return show_page(come_from, year, month, index)


@learn_english_app.route('/specified_page', methods=['GET', 'POST'])
def show_specified_page_words():
    if request.method == 'POST':
        lst = request.form.keys()[0].split('*')
        come_from = lst[0]
        year = lst[1]
        month = lst[2]
        index = lst[3]

        return show_page(come_from, year, month, index)
    return render_template('nothing.html')


def show_page(cf, y, w1, i):
    come_from = cf
    year = y
    word_date = w1
    index = i

    start_index = int(index) * each_page_words_num
    last_index = (int(index) + 1) * each_page_words_num - 1
    i = 0

    tackle = tackle_word.TackleWords()
    res = tackle.get_classified_lst()

    src_list = []
    if '0' == cf and 0 in res:
        if year in res[0]:
            if word_date in res[0][year]:
                src_list = res[0][year][word_date]
            else:
                return render_template('nothing.html')
        else:
            return render_template('nothing.html')
    if '1' == cf and 1 in res:
        if year in res[1]:
            if word_date in res[1][year]:
                src_list = res[1][year][word_date]
            else:
                return render_template('nothing.html')
        else:
            return render_template('nothing.html')

    result_lst = []
    for item in src_list:
        if start_index <= i <= last_index:
            result_lst.append(item)
        if i > last_index:
            break
        i += 1

    num = len(src_list) / each_page_words_num + 1
    return render_template('word_verbose_info.html', come_from=come_from, y=year, w=word_date, result=result_lst, button_num=num, page_index=index, motto=motto.get_random_motto())


@learn_english_app.route('/delete', methods=['GET', 'POST'])
def delete_word():
    if request.method == 'POST':
        lst = request.form.keys()[0].split('*')
        cf = lst[0]
        y = lst[1]
        w = lst[2]
        i = lst[3]
        word = lst[4]

        tackle = tackle_word.TackleWords()
        tackle.delete(word)
        return redirect(url_for('learn_english.show_words_list', come_from=cf, year=y, month=w, index=i))


@learn_english_app.route('/quickly_review', methods=['GET', 'POST'])
def quickly_review():
    if request.method == 'POST':
        tackle = tackle_word.TackleWords()
        res = tackle.get_classified_lst()

        lst = request.form.keys()[0].split('*')
        come_from = lst[0]
        year = lst[1]
        word_date = lst[2]
        index = lst[3]

        start_index = int(index) * each_page_words_num
        if start_index < 0:
            start_index = 0
        last_index = (int(index) + 1) * each_page_words_num - 1

        i = 0
        src_list = []
        if come_from == '0':  # from word builder
            src_list = res[0][year][word_date]
        elif come_from == '1':  # from clipboard
            src_list = res[1][year][word_date]
        else:
            return render_template('nothing.html')

        result_lst = []
        for item in src_list:
            if start_index <= i <= last_index:
                result_lst.append(item)
            if i > last_index:
                break
            i += 1

        num = len(src_list) / each_page_words_num + 1

        global stop
        stop = False
        for word_definition in result_lst:
            if stop:
                break
            word = word_definition['word'][:-2]
            time.sleep(1.5)
            pronunciation.show(word)
            time.sleep(3)
            pronunciation.show(word)
            time.sleep(3)
            pronunciation.show(word)
        return render_template('word_verbose_info.html',
                               come_from=come_from,
                               y=year,
                               w=word_date,
                               result=result_lst,
                               button_num=num,
                               page_index=index,
                               motto=motto.get_random_motto()
                               )
    return render_template('nothing.html')


@learn_english_app.route('/stop_quickly_review', methods=['GET', 'POST'])
def stop_quickly_review():
    if request.method == 'POST':
        global stop
        stop = True

        lst = request.form.keys()[0].split('*')
        come_from = lst[0]
        year = lst[1]
        word_date = lst[2]
        index = lst[3]

        return show_page(come_from, year, word_date, index)
    return render_template('nothing.html')


@learn_english_app.route('/vocabulary_list/<category_name>', methods=['GET', 'POST'])
def show_vocabulary_list(category_name):
    list_data = vocabulary_list.get_lists_by_category(
        category_name.encode('utf-8'))
    return render_template('vocabulary_list.html',
                           category_name=category_name,
                           category_name_for_show=vocabulary_list.category_dict[category_name],
                           list_data=list_data
                           )


@learn_english_app.route('/vocabulary/<category_name>/<list_name>', methods=['GET', 'POST'])
def vocabulary(category_name, list_name):
    category_name = category_name.encode('utf-8')
    list_name = list_name.encode('utf-8')
    list_data = vocabulary_list.get_list_data(category_name, list_name)

    if list_data is None:
        return render_template('nothing.html')

    list_detailed_info = list_data['list_detailed_info']
    list_detailed_description = list_data['list_detailed_description']
    list_num = list_data['list_num']

    return render_template('vocabulary.html',
                           category_name=category_name,
                           list_name=list_name,
                           list_detailed_info=list_detailed_info,
                           list_detailed_description=list_detailed_description,
                           list_num=list_num
                           )


def p(content):
    utility.append_log('---------------------')
    utility.append_log(content)


def pa(content):
    utility.append_log('---------------------')
    utility.append_log(' '.join(content))
