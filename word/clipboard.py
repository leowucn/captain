# -*- coding:utf-8 -*-
import time
import pyperclip
import tackle_word
from time import gmtime, strftime
import pronunciation
import os
import utility
import multiprocessing

interval = 2.5    # interval seconds for scanning clipboard
times = 3   # the times of repeating word pronunciation
max_length = 600    # the maximum length of word usage.
timeout = 6     # wait no more than four seconds for show pronunciation.


def watcher():
	word = ''
	i = 0
	while True:
		result = pyperclip.paste().strip().lower()
		if len(result) >= max_length:
			continue
		if result.isalpha() and len(result) != 0 and word != result:
			word = result
			i = 0
		# print('word = ' + word + ', result = ' + result + ', i = ' + str(i))
		if word != '' and len(result) > len(word) and result.find(word) >= 0:
			# in this case, result should be a usage containing the
			# corresponding result which was supposed to be a word or phrase.
			tackle = tackle_word.TackleWords()
			tackle.query(word + '-1', result, strftime("%Y-%m-%d", gmtime()))
			os.system("echo '' | pbcopy")
		if word != '':
			if i >= times:
				if result == word:
					os.system("echo '' | pbcopy")
				i = 0
				word = ''
				continue
			i += 1

			p = multiprocessing.Process(target=show, args=(word,))
			p.start()
			# Wait timeout seconds or until process finishes
			p.join(timeout)
			# If thread is still active
			if p.is_alive():
				print "running... let's kill it..."
				# Terminate
				p.terminate()
				p.join()

		time.sleep(interval)
	utility.show_notification('Captain Info', 'Sorry, some error may happened! Please check the error message!')


def show(word):
	pronunciation.show_literal_pronunciation(word)
	pronunciation.launch_pronunciation(word)


if __name__ == "__main__":
	watcher()
