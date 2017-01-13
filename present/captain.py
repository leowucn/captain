# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
import collections
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('/Users/leo/work/captain/word')
import tackle_word

each_page_words_num = 10
app = Flask(__name__)


@app.route('/')
def show_year_list():
	tackle = tackle_word.TackleWords()
	classified_words_dict = tackle.get_classified_dict()
	year_list = []
	for key, value in classified_words_dict.iteritems():
		year_list.append(key)
	return render_template('year_list.html', year_list=year_list)


@app.route('/week_list', methods=['GET', 'POST'])
def show_week_list():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		classified_words_dict = tackle.get_classified_dict()
		week_list = []
		year = request.form.keys()[0]
		for key, value in classified_words_dict[year].iteritems():
			week_list.append(key)
		return render_template('week_list.html', year=year, week_list=week_list)
	return


@app.route('/words_list', methods=['GET', 'POST'])
def show_words_list():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		classified_words_dict = tackle.get_classified_dict()
		year = request.form.keys()[0].split('-')[0]
		week = request.form.keys()[0].split('-')[1]

		result_dict = collections.OrderedDict()
		last_index = 1 * each_page_words_num
		i = 0
		if last_index < len(classified_words_dict[year][week]):
			for word, meaning in sorted(classified_words_dict[year][week].items()):
				result_dict[word] = meaning
				if i > last_index:
					break
				i += 1
		else:
			result_dict = classified_words_dict[year][week]

		num = len(classified_words_dict[year][week])/each_page_words_num + 1
		return render_template('word_verbose_info.html', y=year, w=week, result=result_dict, button_num=num, page_index=0)
	return


@app.route('/specified_page', methods=['GET', 'POST'])
def show_specified_page_words():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		classified_words_dict = tackle.get_classified_dict()
		year = request.form.values()[0].split('-')[0]
		week = request.form.values()[0].split('-')[1]
		index = int(request.form.values()[0].split('-')[2])

		start_index = index * each_page_words_num - 1
		if start_index < 0:
			start_index = 0
		last_index = (index + 1) * each_page_words_num - 1
		i = 0
		result_dict = collections.OrderedDict()
		for word, meaning in sorted(classified_words_dict[year][week].items()):
			if start_index <= i < last_index:
				result_dict[word] = meaning
			if i >= last_index:
				break
			i += 1

		num = len(classified_words_dict[year][week])/each_page_words_num + 1
		return render_template('word_verbose_info.html', y=year, w=week, result=result_dict, button_num=num, page_index=index)
	return

if __name__ == '__main__':
	app.run(debug=True)
