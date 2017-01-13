# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('/Users/leo/work/captain/model')
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

		num = len(classified_words_dict[year][week])/each_page_words_num + 1
		return render_template('word_verbose_info.html', y=year, w=week, result=classified_words_dict[year][week], button_num=num)
	return


@app.route('/specified_page/<y>/<w>/<page_index>', methods=['GET', 'POST'])
def show_specified_page_words():
	if request.method == 'POST':
		tackle = tackle_word.TackleWords()
		classified_words_dict = tackle.get_classified_dict()


	return

if __name__ == '__main__':
	app.run(debug=True)
