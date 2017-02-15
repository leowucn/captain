# -*- coding:utf-8 -*-
import requests
import bs4
import sys
import random

reload(sys)
sys.setdefaultencoding('utf8')


motto_type = ('business', 'family', 'famous', 'funny', 'leadership',
			  'life', 'love', 'movie', 'politic', 'religious', 'team')


def get_random_motto():
	random_motto_type = random.choice(motto_type)
	url = 'http://www.mottos.info/' + random_motto_type
	res = requests.get(url)
	soup = bs4.BeautifulSoup(res.content, 'lxml')

	raw_motto = soup.find('div', attrs={'class': 'entry-content'})
	motto_lst = []
	for i, s in enumerate(raw_motto.stripped_strings):
		if i == 0 or i == len(list(raw_motto.stripped_strings)) - 1:
			continue
		s = s.replace('“', '"')
		s = s.replace('”', '"')
		motto_lst.append(s.encode('utf-8'))

	res_lst = list()
	res_lst.append(random_motto_type)

	random_index = random.choice(range(0, len(motto_lst) - 2))

	if motto_lst[random_index].startswith('"'):
		if not motto_lst[random_index + 1].startswith('"'):
			res_lst.append(motto_lst[random_index])
			res_lst.append(motto_lst[random_index + 1])
		else:
			res_lst.append(motto_lst[random_index])
	else:
		if motto_lst[random_index + 1].startswith('"'):
			if (random_index + 2) < len(motto_lst) + 1 and not motto_lst[random_index + 2].startswith('"'):
				res_lst.append(motto_lst[random_index + 1])
				res_lst.append(motto_lst[random_index + 2])
			else:
				res_lst.append(motto_lst[random_index + 1])

	return res_lst


# get_random_motto()
