# !/usr/bin/env python
# -*- coding: utf-8 -*-
import bs4
import os
import utility
import urlparse


home_url = 'https://www.vocabulary.com/'
lists_path_featured = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/featured.json')
lists_path_top_rated = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/top_rated.json')
lists_path_test_prep = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/test_prep.json')
lists_path_literature = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/literature.json')
lists_path_morphology_roots = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/morphology_and_roots.json')
lists_path_historical_documents = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/historical_documents.json')
lists_path_speeches = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/speeches.json')
lists_path_just_for_fun = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/just_for_fun.json')
lists_path_news = os.path.join(
    os.getcwd(), 'src/learn_english/asset/vocabulary_lists/news.json')

category_dict = {
    'test-prep': 'Test Prep',
    'literature': 'Literature',
    'morphology-and-roots': 'Morphology & Roots',
    'historical-documents': 'Historical Documents',
    'speeches': 'Speeches',
    'just-for-fun': 'Just for Fun',
    'news': 'News'
}


def update_all_lists():
    p(11)
    raw_content = utility.get_raw_content(urlparse.urljoin(home_url, 'lists'), 'col9 listcats pad2x ')
    if raw_content == '':
        return
    category_raw_content_list = str(raw_content).split('section class')
    p(22)
    for category_raw_content in category_raw_content_list:
        name = utility.extract_info_from_raw(category_raw_content, 'sectionHeader').strip()
        if name == '':
            continue
        if name == 'Featured Lists':
            update_list(category_raw_content, 'featured')
        if name == 'Top Rated Lists':
            update_list(category_raw_content, 'top-rated')
    p(33)
    for url_postfix in category_dict.keys():
        url = home_url + 'lists/' + url_postfix
        content = utility.get_content_of_url(url)
        soup = str(bs4.BeautifulSoup(content, 'lxml'))
        try:
            if soup.find('bycat hasmore') < 0:
                p('Cannot find phrase "bycat hasmore"!')
                p(soup)
                p(url_postfix)
                return
        except:
            return
        update_list(str(soup).split('bycat hasmore')[1], url_postfix)
    p(44)
    utility.show_notification(
        'Captain Update Vocabulary Lists', 'Update Successfully!')
    return


def get_all_vocabulary_lists():
    result = dict()
    if os.path.exists(lists_path_featured):
        result['featured'] = utility.load_json_file(lists_path_featured)
    if os.path.exists(lists_path_top_rated):
        result['top-rated'] = utility.load_json_file(lists_path_top_rated)
    if os.path.exists(lists_path_test_prep):
        result['test-prep'] = utility.load_json_file(lists_path_test_prep)
    if os.path.exists(lists_path_literature):
        result['literature'] = utility.load_json_file(lists_path_literature)
    if os.path.exists(lists_path_morphology_roots):
        result['morphology-and-roots'] = utility.load_json_file(
            lists_path_morphology_roots)
    if os.path.exists(lists_path_historical_documents):
        result['historical-documents'] = utility.load_json_file(
            lists_path_historical_documents)
    if os.path.exists(lists_path_speeches):
        result['speeches'] = utility.load_json_file(lists_path_speeches)
    if os.path.exists(lists_path_just_for_fun):
        result['just-for-fun'] = utility.load_json_file(
            lists_path_just_for_fun)
    if os.path.exists(lists_path_news):
        result['news'] = utility.load_json_file(lists_path_news)
    return result


def get_lists_by_category(category_name):
    if category_name == 'featured':
        return utility.load_json_file(lists_path_featured)
    if category_name == 'top-rated':
        return utility.load_json_file(lists_path_top_rated)
    if category_name == 'test-prep':
        return utility.load_json_file(lists_path_test_prep)
    if category_name == 'literature':
        return utility.load_json_file(lists_path_literature)
    if category_name == 'morphology-and-roots':
        return utility.load_json_file(lists_path_morphology_roots)
    if category_name == 'historical-documents':
        return utility.load_json_file(lists_path_historical_documents)
    if category_name == 'speeches':
        return utility.load_json_file(lists_path_speeches)
    if category_name == 'just-for-fun':
        return utility.load_json_file(lists_path_just_for_fun)
    if category_name == 'news':
        return utility.load_json_file(lists_path_news)


def get_list_data(category_name, list_name):
    if category_name == 'featured':
        return get_value_by_key(utility.load_json_file(lists_path_featured), list_name)
    if category_name == 'top-rated':
        return get_value_by_key(utility.load_json_file(lists_path_top_rated), list_name)
    if category_name == 'test-prep':
        return get_value_by_key(utility.load_json_file(lists_path_test_prep), list_name)
    if category_name == 'literature':
        return get_value_by_key(utility.load_json_file(lists_path_literature), list_name)
    if category_name == 'morphology-and-roots':
        return get_value_by_key(utility.load_json_file(lists_path_morphology_roots), list_name)
    if category_name == 'historical-documents':
        return get_value_by_key(utility.load_json_file(lists_path_historical_documents), list_name)
    if category_name == 'speeches':
        return get_value_by_key(utility.load_json_file(lists_path_speeches), list_name)
    if category_name == 'just-for-fun':
        return get_value_by_key(utility.load_json_file(lists_path_just_for_fun), list_name)
    if category_name == 'news':
        return get_value_by_key(utility.load_json_file(lists_path_news), list_name)


def get_value_by_key(dict_data, key):
    if key in dict_data:
        return dict_data[key]
    else:
        return None


def write_lists_by_category_and_data(category_name, lists_data):
    if category_name == 'featured':
        utility.write_json_file(lists_path_featured, lists_data)
    if category_name == 'top-rated':
        utility.write_json_file(lists_path_top_rated, lists_data)
    if category_name == 'test-prep':
        utility.write_json_file(lists_path_test_prep, lists_data)
    if category_name == 'literature':
        utility.write_json_file(lists_path_literature, lists_data)
    if category_name == 'morphology-and-roots':
        utility.write_json_file(lists_path_morphology_roots, lists_data)
    if category_name == 'historical-documents':
        utility.write_json_file(lists_path_historical_documents, lists_data)
    if category_name == 'speeches':
        utility.write_json_file(lists_path_speeches, lists_data)
    if category_name == 'just-for-fun':
        utility.write_json_file(lists_path_just_for_fun, lists_data)
    if category_name == 'news':
        utility.write_json_file(lists_path_news, lists_data)


# ----------------------------------
# get all of list detailed information from category
def update_list(category_raw_content, category_name):
    category_lists_dict = get_lists_by_category(category_name)

    item_raw_content_list = category_raw_content.split('wordlist shortlisting')
    for item_raw_content in item_raw_content_list[1:]:
        list_name = utility.extract_info_from_raw(
            item_raw_content.replace('#', ''), 'href')
        if list_name in category_lists_dict:
            continue
    
        list_brief_description = utility.extract_info_from_raw(
            item_raw_content, 'description')
        if len(list_brief_description) > 160:
            list_brief_description = list_brief_description[:160] + '...'
        list_words_num = utility.extract_info_from_raw(
            item_raw_content, 'readMore')
        list_href = extract_detailed_address(item_raw_content)
        if list_name == '' or list_href == '':
            continue

        category_lists_dict[list_name] = dict()
        category_lists_dict[list_name]['list_brief_description'] = list_brief_description
        category_lists_dict[list_name]['list_num'] = list_words_num
        category_lists_dict[list_name]['list_href'] = list_href
        category_lists_dict[list_name]['list_detailed_info'] = []

        # ------------------------------------------
        # detailed_description of list
        entire_list_url = urlparse.urljoin(home_url, list_href)
        raw_words_list_description = utility.get_raw_content(
            entire_list_url, 'description')
        if raw_words_list_description is not None:
            # if category_name == 'top_rated':           
                # p(raw_words_list_description)
            words_list_description = utility.extract_info_from_raw(raw_words_list_description, 'description')
            category_lists_dict[list_name]['list_detailed_description'] = words_list_description

        raw_words_list_content_list = utility.get_raw_content(entire_list_url, 'centeredContent').split('class=\"entry learnable\"')
        
        for content in raw_words_list_content_list:
            if 'class="definition"' not in content:
                raw_words_list_content_list.remove(content)
        for index, raw_words_list_content in enumerate(raw_words_list_content_list):
            raw_words_list_content = raw_words_list_content.replace('&amp;', '&')
            raw_words_list_content = raw_words_list_content.replace('\n', ' ')
            raw_words_list_content = raw_words_list_content.replace('<i>', '')
            raw_words_list_content = raw_words_list_content.replace('</i>', '')
            raw_words_list_content = raw_words_list_content.replace('<em>', '')
            raw_words_list_content = raw_words_list_content.replace('</em>', '')
            raw_words_list_content = raw_words_list_content.replace('<strong>', '')
            raw_words_list_content = raw_words_list_content.replace('</strong>', '')
            raw_words_list_content = raw_words_list_content.replace('<br>', '')
            name = utility.extract_info_from_raw(raw_words_list_content, 'href')
            if name == "definitions & notes":
                continue

            definition = utility.extract_info_from_raw(raw_words_list_content, '\"definition\"')
            p(raw_words_list_content)
            p(category_name)
            p(list_name)
            example = utility.extract_info_from_raw(raw_words_list_content, '\"example\"')
            description = utility.extract_info_from_raw(raw_words_list_content, '\"description\"')

            list_detailed_info_dict = dict()
            list_detailed_info_dict[name] = name
            list_detailed_info_dict[name] = dict()
            list_detailed_info_dict[name]['index'] = index
            list_detailed_info_dict[name]['word_definition'] = definition
            list_detailed_info_dict[name]['word_example'] = example
            list_detailed_info_dict[name]['word_description'] = description

            category_lists_dict[list_name]['list_detailed_info'].append(list_detailed_info_dict)

    write_lists_by_category_and_data(category_name, category_lists_dict)


def extract_detailed_address(raw_content):
    """
    :param raw_content:
    :return: return list address, such as 'lists/1752913'
    """
    try:
        point_one_index = raw_content.index('href')
    except:
        return ''
    left_colon_index = raw_content[point_one_index:].index(
        '"') + point_one_index + 1
    right_colon_index = raw_content[left_colon_index:].index(
        '"') + left_colon_index
    return raw_content[left_colon_index:right_colon_index]
# -------------------------------------------------


def p(content):
    utility.append_log('---------------------')
    if type(content) == int:
        utility.append_log(str(content))
    else:
        utility.append_log(content)

if __name__ == "__main__":
    update_all_lists()
