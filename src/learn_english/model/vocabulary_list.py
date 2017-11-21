# -*- coding: utf-8 -*-
"""
fetch vocabulary lists from vocabulary.com, thanks for their great work!
"""
import os
import urlparse
import bs4
import utility
import constants


def update_all_lists():
    raw_content = utility.get_raw_content(
        urlparse.urljoin(constants.VOCABULARY_HOME_URL, 'lists'), 'col9 listcats pad2x ')
    if raw_content == '':
        return
    category_raw_content_list = str(raw_content).split('section class')
    for category_raw_content in category_raw_content_list:
        name = utility.extract_info_from_raw(
            category_raw_content, 'sectionHeader').strip()
        if name == '':
            continue
        if name == 'Featured Lists':
            update_list(category_raw_content, 'featured')
        if name == 'Top Rated Lists':
            update_list(category_raw_content, 'top-rated')
    for url_postfix in constants.CATEGORY_DICT.keys():
        url = constants.VOCABULARY_HOME_URL + 'lists/' + url_postfix
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
    utility.show_notification(
        'Captain Update Vocabulary Lists', 'Update Successfully!')
    return


def get_all_vocabulary_lists():
    result = dict()
    if os.path.exists(constants.LISTS_FEATURED):
        result['featured'] = utility.load_json_file(constants.LISTS_FEATURED)
    if os.path.exists(constants.LISTS_TOP_RATED):
        result['top-rated'] = utility.load_json_file(constants.LISTS_TOP_RATED)
    if os.path.exists(constants.LISTS_TEST_PREP):
        result['test-prep'] = utility.load_json_file(constants.LISTS_TEST_PREP)
    if os.path.exists(constants.LISTS_LITERATURE):
        result['literature'] = utility.load_json_file(
            constants.LISTS_LITERATURE)
    if os.path.exists(constants.LISTS_MORPHOLOGY_ROOTS):
        result['morphology-and-roots'] = utility.load_json_file(
            constants.LISTS_MORPHOLOGY_ROOTS)
    if os.path.exists(constants.LISTS_HISTORICAL_DOCUMENTS):
        result['historical-documents'] = utility.load_json_file(
            constants.LISTS_HISTORICAL_DOCUMENTS)
    if os.path.exists(constants.LISTS_SPEECHES):
        result['speeches'] = utility.load_json_file(constants.LISTS_SPEECHES)
    if os.path.exists(constants.LISTS_JUST_FOR_FUN):
        result['just-for-fun'] = utility.load_json_file(
            constants.LISTS_JUST_FOR_FUN)
    if os.path.exists(constants.LISTS_NEWS):
        result['news'] = utility.load_json_file(constants.LISTS_NEWS)
    return result


def get_lists_by_category(category_name):
    if category_name == 'featured':
        return utility.load_json_file(constants.LISTS_FEATURED)
    if category_name == 'top-rated':
        return utility.load_json_file(constants.LISTS_TOP_RATED)
    if category_name == 'test-prep':
        return utility.load_json_file(constants.LISTS_TEST_PREP)
    if category_name == 'literature':
        return utility.load_json_file(constants.LISTS_LITERATURE)
    if category_name == 'morphology-and-roots':
        return utility.load_json_file(constants.LISTS_MORPHOLOGY_ROOTS)
    if category_name == 'historical-documents':
        return utility.load_json_file(constants.LISTS_HISTORICAL_DOCUMENTS)
    if category_name == 'speeches':
        return utility.load_json_file(constants.LISTS_SPEECHES)
    if category_name == 'just-for-fun':
        return utility.load_json_file(constants.LISTS_JUST_FOR_FUN)
    if category_name == 'news':
        return utility.load_json_file(constants.LISTS_NEWS)


def get_list_data(category_name, list_name):
    if category_name == 'featured':
        return get_value_by_key(utility.load_json_file(constants.LISTS_FEATURED), list_name)
    if category_name == 'top-rated':
        return get_value_by_key(utility.load_json_file(constants.LISTS_TOP_RATED), list_name)
    if category_name == 'test-prep':
        return get_value_by_key(utility.load_json_file(constants.LISTS_TEST_PREP), list_name)
    if category_name == 'literature':
        return get_value_by_key(utility.load_json_file(constants.LISTS_LITERATURE), list_name)
    if category_name == 'morphology-and-roots':
        return get_value_by_key(utility.load_json_file(constants.LISTS_MORPHOLOGY_ROOTS), list_name)
    if category_name == 'historical-documents':
        return get_value_by_key(utility.load_json_file(constants.LISTS_HISTORICAL_DOCUMENTS), list_name)
    if category_name == 'speeches':
        return get_value_by_key(utility.load_json_file(constants.LISTS_SPEECHES), list_name)
    if category_name == 'just-for-fun':
        return get_value_by_key(utility.load_json_file(constants.LISTS_JUST_FOR_FUN), list_name)
    if category_name == 'news':
        return get_value_by_key(utility.load_json_file(constants.LISTS_NEWS), list_name)


def get_value_by_key(dict_data, key):
    if key in dict_data:
        return dict_data[key]
    else:
        return None


def write_lists_by_category_and_data(category_name, lists_data):
    if category_name == 'featured':
        utility.write_json_file(constants.LISTS_FEATURED, lists_data)
    if category_name == 'top-rated':
        utility.write_json_file(constants.LISTS_TOP_RATED, lists_data)
    if category_name == 'test-prep':
        utility.write_json_file(constants.LISTS_TEST_PREP, lists_data)
    if category_name == 'literature':
        utility.write_json_file(constants.LISTS_LITERATURE, lists_data)
    if category_name == 'morphology-and-roots':
        utility.write_json_file(constants.LISTS_MORPHOLOGY_ROOTS, lists_data)
    if category_name == 'historical-documents':
        utility.write_json_file(
            constants.LISTS_HISTORICAL_DOCUMENTS, lists_data)
    if category_name == 'speeches':
        utility.write_json_file(constants.LISTS_SPEECHES, lists_data)
    if category_name == 'just-for-fun':
        utility.write_json_file(constants.LISTS_JUST_FOR_FUN, lists_data)
    if category_name == 'news':
        utility.write_json_file(constants.LISTS_NEWS, lists_data)


def update_list(category_raw_content, category_name):
    """
    get all of list detailed information from category
    """
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
        entire_list_url = urlparse.urljoin(
            constants.VOCABULARY_HOME_URL, list_href)
        raw_words_list_description = utility.get_raw_content(
            entire_list_url, 'description')
        if raw_words_list_description is not None:
            words_list_description = utility.extract_info_from_raw(
                raw_words_list_description, 'description')
            category_lists_dict[list_name]['list_detailed_description'] = words_list_description

        raw_words_list_content_list = utility.get_raw_content(
            entire_list_url, 'centeredContent').split('class=\"entry learnable\"')

        for content in raw_words_list_content_list:
            if 'class="definition"' not in content:
                raw_words_list_content_list.remove(content)
        for index, raw_words_list_content in enumerate(raw_words_list_content_list):
            raw_words_list_content = raw_words_list_content.replace(
                '&amp;', '&')
            raw_words_list_content = raw_words_list_content.replace('\n', ' ')
            raw_words_list_content = raw_words_list_content.replace('<i>', '')
            raw_words_list_content = raw_words_list_content.replace('</i>', '')
            raw_words_list_content = raw_words_list_content.replace('<em>', '')
            raw_words_list_content = raw_words_list_content.replace(
                '</em>', '')
            raw_words_list_content = raw_words_list_content.replace(
                '<strong>', '')
            raw_words_list_content = raw_words_list_content.replace(
                '</strong>', '')
            raw_words_list_content = raw_words_list_content.replace('<br>', '')
            name = utility.extract_info_from_raw(
                raw_words_list_content, 'href')
            if name == "definitions & notes":
                continue

            definition = utility.extract_info_from_raw(
                raw_words_list_content, '\"definition\"')
            example = utility.extract_info_from_raw(
                raw_words_list_content, '\"example\"')
            description = utility.extract_info_from_raw(
                raw_words_list_content, '\"description\"')

            list_detailed_info_dict = dict()
            list_detailed_info_dict[name] = name
            list_detailed_info_dict[name] = dict()
            list_detailed_info_dict[name]['index'] = index
            list_detailed_info_dict[name]['word_definition'] = definition
            list_detailed_info_dict[name]['word_example'] = example
            list_detailed_info_dict[name]['word_description'] = description

            category_lists_dict[list_name]['list_detailed_info'].append(
                list_detailed_info_dict)

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


if __name__ == "__main__":
    update_all_lists()
