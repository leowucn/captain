# -*- coding:utf-8 -*-
"""
database interface for conventionce handling
"""
from bson import ObjectId
from pymongo import MongoClient
import constants

MONGO_CLIENT = MongoClient(constants.MONGO_ADDR)


# ------------------------------------------------
# word definition collection
def insert_word_definition(word_definition):
    db = MONGO_CLIENT['db_captain']
    collection = db['word_definition']
    oid = ObjectId()
    word_definition['_id'] = str(oid)
    collection.insert_one(word_definition)


def delete_word_definition_by_word(word):
    db = MONGO_CLIENT['db_captain']
    collection = db['word_definition']
    collection.delete_one({'word': word})


def update_word_definition(word_definition):
    db = MONGO_CLIENT['db_captain']
    collection = db['word_definition']
    oid = ObjectId()
    word_definition['_id'] = str(oid)
    collection.delete_one({'word': word_definition['word']})
    collection.insert_one(word_definition)


def get_word_definition_by_word(word):
    db = MONGO_CLIENT['db_captain']
    collection = db['word_definition']
    return collection.find_one({'word': word})


def get_word_definition_all():
    db = MONGO_CLIENT['db_captain']
    collection = db['word_definition']
    return collection.find({})


# ------------------------------------------------
# clipboard collection
def insert_clipboard_word(clipboard_word):
    db = MONGO_CLIENT['db_captain']
    collection = db['clipboard_word']
    oid = ObjectId()
    clipboard_word['_id'] = str(oid)
    collection.insert_one(clipboard_word)


def delete_clipboard_word_by_word(word):
    db = MONGO_CLIENT['db_captain']
    collection = db['clipboard_word']
    collection.delete_one({'word': word})


def update_clipboard_word(clipboard_word):
    db = MONGO_CLIENT['db_captain']
    collection = db['clipboard_word']
    oid = ObjectId()
    clipboard_word['_id'] = str(oid)
    collection.delete_one({'word': clipboard_word['word']})
    collection.insert_one(clipboard_word)


def get_clipboard_word_by_word(word):
    db = MONGO_CLIENT['db_captain']
    collection = db['clipboard_word']
    return collection.find_one({'word': word})


def get_clipboard_word_all():
    db = MONGO_CLIENT['db_captain']
    collection = db['clipboard_word']
    return collection.find({})

# ------------------------------------------------
# word basic definition


def insert_word_basic(word_basic):
    db = MONGO_CLIENT['db_captain']
    collection = db['word_basic']
    oid = ObjectId()
    word_basic['_id'] = str(oid)
    collection.insert_one(word_basic)


def get_word_basic_by_word(word):
    db = MONGO_CLIENT['db_captain']
    collection = db['word_basic']
    return collection.find_one({'word': word})


def get_word_basic_all():
    db = MONGO_CLIENT['db_captain']
    collection = db['word_basic']
    return collection.find({})

# insert_word_definition({"author": "Mike","text": "My first blog post!", 'word':'hello'})
# res = get_word_definition_by_word('hell')
# print(res)
# delete_word_definition_by_id(res[u'_id'])
