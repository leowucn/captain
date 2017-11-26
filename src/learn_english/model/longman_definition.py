# -*- coding: utf-8 -*-
import re
import datetime
import bs4
import utility
import constants


def p(c):
    print(c)


def longman_definition(wrapped_word):
    """
    get word meaning from ldoceonline.com, thanks for their great work.
    """
    url = constants.LONGMAN_HOME_URL + wrapped_word[:-2].strip()
    content = utility.get_content_of_url(url)
    soup = bs4.BeautifulSoup(markup=content, features='lxml')
    definition_dict = dict()


longman_definition('giggle-1')
