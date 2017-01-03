# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import re
import requests
import bs4
import json

json_words_meaning = './json_words_meaning'


class Word:
	def __init__(self):
		pass

	def tackle_words(self, words_list):
		word_meaning = ''
		for word in words_list:
			url = 'http://dict.youdao.com/w/eng/' + word
			res = requests.get(url)
			soup = bs4.BeautifulSoup(res.content, 'lxml')
			word_meaning = ''

			word_meaning += '#----------------------basic-----------------------\n'
			basic = soup.find("div", id="phrsListTab")
			if basic:
				result = basic.find('div', attrs={'class': 'trans-container'})
				word_meaning += result.ul.get_text().strip('\n')

			word_meaning += '\n# -------------------web phrase---------------------\n'
			phrase = soup.find('div', id='webPhrase')
			if phrase:
				phrase_str = ''
				for i, s in enumerate(phrase.stripped_strings):
					r = s.replace('\n', '')
					tmp = re.sub('\W*', '', r)
					# in special case, we need to eliminate unuseful phrase, like 'Get Down (You're the One for Me)'
					if tmp.isalpha() and r.find('(') < 0:
						phrase_str += r + '     ' + re.sub('\s*', '', list(phrase.stripped_strings)[i+1]) + '\n'
				word_meaning += phrase_str

			word_meaning += '\n# ---------------------collins---------------------\n'
			collins = soup.find('div', id="collinsResult")
			if collins:
				text_list = []

				for i, s in enumerate(collins.stripped_strings):
					text_list.append(' '.join(s.split()))   # tackle special formation problem

				if text_list[1].startswith('('):
					# Phrase
					word_meaning = word_meaning + text_list[0] + '\n'
					line = ' '.join(text_list[2:])
				else:
					word_meaning = word_meaning + (' '.join(text_list[:2])) + '\n'
					line = ' '.join(text_list[3:])
				text1 = re.sub('例：', '\n例：', line)
				text1 = re.sub("\d+\.", "\n*", text1)
				text1 = text1[text1.find('*'):]
				word_meaning += text1


		print(word_meaning)
		return word_meaning


	def write(self, word_meaning):
		f = open(json_words_meaning, 'w+')
		json.dump(word_meaning, f)

word = Word()
t = word.tackle_words(('get', ))
