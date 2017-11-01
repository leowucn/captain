# -*- encoding: utf-8 -*-
import sqlite3
import os
from time import gmtime, strftime
import datetime
import pytz
import re

sqlite_file = '/Volumes/Kindle/system/vocabulary/vocab.db'  # on mac os
# sqlite_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vocab.db')  # for test
words_table_name = 'WORDS'
lookups_table_name = 'LOOKUPS'

words_dir = os.path.join(os.getcwd(), 'src/learn_english/asset/words')


def backup_sqlite_file():
    os.system('cp /Volumes/Kindle/system/vocabulary/vocab.db /Volumes/Kindle/system/vocabulary/.vocab.db.bak')


def get_table_data(conn, table_name):
    c = conn.cursor()
    c.execute('SELECT * FROM {tn}'.format(tn=table_name))
    return c.fetchall()


def get_table_field_names(conn, table_name):
    c = conn.cursor()
    c.execute('PRAGMA TABLE_INFO({tn})'.format(tn=table_name))
    # collect names in a list
    return [tup[1] for tup in c.fetchall()]


def delete_retrieved_data(conn, word_key_lst):
    c = conn.cursor()
    for word_key in word_key_lst:
        # delete from LOOKUPS table
        query = "delete from lookups where word_key= '%s' " % word_key
        c.execute(query)

        # delete from WORDS table
        query = "delete from words where id= '%s' " % word_key
        c.execute(query)
    conn.commit()


def tackle_kindle(conn):
    words_filed_dict = dict()
    lookups_filed_dict = dict()

    for index, filed in enumerate(get_table_field_names(conn, words_table_name)):
        words_filed_dict[filed] = index
    for index, filed in enumerate(get_table_field_names(conn, lookups_table_name)):
        lookups_filed_dict[filed] = index

    words_data_lst = get_table_data(conn, words_table_name)
    lookups_data_lst = get_table_data(conn, lookups_table_name)

    result = dict()
    exported_id_lst = []
    for word_data in words_data_lst:
        if word_data[words_filed_dict['category']] == 100:  # '100' represents the category in which the words has been mastered.
            item = dict()
            item['word'] = word_data[words_filed_dict['stem']]
            result[word_data[words_filed_dict['id']]] = item
            exported_id_lst.append(word_data[words_filed_dict['id']])

    for lookup_data in lookups_data_lst:
        word_key = lookup_data[lookups_filed_dict['word_key']]
        if word_key in exported_id_lst:
            result[word_key]['book_key'] = lookup_data[lookups_filed_dict['book_key']]
            result[word_key]['usage'] = lookup_data[lookups_filed_dict['usage']]
            result[word_key]['timestamp'] = lookup_data[lookups_filed_dict['timestamp']]
    store(result)
    delete_retrieved_data(conn, result)


# key: 'word' 'book_key' 'usage' 'timestamp'
def store(words_data):
    file_name = strftime("%Y-%m-%d", gmtime()) + '.txt'
    file_path = os.path.join(words_dir, file_name)

    new_index = 1
    if os.path.isfile(file_path):
        with open(file_path) as f:
            for line in f:
                if len(line) > 0 and line[0].isdigit():
                    res = re.findall(r'\d+', line)
                    if len(res) != 0:
                        if res[0] > new_index:
                            new_index = int(res[0]) + 1
    with open(file_path, mode='a') as f:
        for word_key, word_info in words_data.iteritems():
            if len(word_info) != 4:
                continue
            f.write(str(new_index) + '. ' + word_info['word'] + '\n')
            f.write('usage: ' + word_info['usage'].encode('utf-8') + '\n')
            f.write('book: ' + word_info['book_key'][:word_info['book_key'].find("'")] + '\n')
            tz = pytz.timezone('Asia/Shanghai')
            date = datetime.datetime.fromtimestamp(word_info['timestamp']/1000, tz).strftime('%Y-%m-%d %H:%M:%S')
            f.write('date: ' + date + '\n')
            f.write('\n')
            new_index += 1


if __name__ == "__main__":
    if os.path.isfile(sqlite_file):
        backup_sqlite_file()
        # Connecting to the database file
        sql_conn = sqlite3.connect(sqlite_file)
        tackle_kindle(sql_conn)
        # Closing the connection to the database file
        sql_conn.close()
