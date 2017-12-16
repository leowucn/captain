# -*- coding:utf-8 -*-
"""
const values definination
"""

# interval seconds for scanning clipboard
INTERVAL = 1
# the times of repeating word pronunciation
MAX_DISPLAY_TIMES = 4

# mongo address
MONGO_ADDR = 'mongodb://localhost:27017'

# if one sentence has any character in the list, then
#  it might be a block of code, and should be ignored.
INVALID_CHARACTERS = {'@', '#', '^', '&', '&&',
                      '||', '*', "==", "===", '\\', '}', '`', '=', '{'}


WORD_TYPE = {'n.', 'v.', 'pron.', 'adj.', 'adv.', 'num.', 'art.',
             'prep.', 'conj.', 'int.', 'vi.', 'vt.', 'aux.', 'aux.v'}

MOTTO_PATH = 'src/learn_english/asset/motto.json'
MOTTO_TYPE = ('business', 'family', 'famous', 'funny', 'leadership',
              'life', 'love', 'movie', 'politic', 'religious', 'team')

# the interval seconds between British pronunciation and American pronunciation
PRONUNCIATION_INTERVAL = 0.7
PRONUNCIATION_DIR = 'src/learn_english/asset/pronunciation'
KINDLE_WORDS_DIR = 'src/learn_english/asset/words_from_kindle'
CLIP_WORDS_FILE = 'src/learn_english/asset/words_from_clip/words_from_clip.json'
ALL_WORDS_FILE = 'src/learn_english/asset/all_words/words.txt'
# on macOs
KINDLE_SQLITE = '/Volumes/Kindle/system/vocabulary/vocab.db'
KINDLE_SQLITE_BACKUP = '/Volumes/Kindle/system/vocabulary/vocab.db.bak'


USAGE_PREFIX = '✅: '

# -------------------------------------
# vocabulary list part
VOCABULARY_HOME_URL = 'https://www.vocabulary.com/'
LONGMAN_HOME_URL = 'https://www.ldoceonline.com/dictionary/'
YOUDAO_URL_PREFIX = 'http://www.youdao.com/w/eng/'


LISTS_FEATURED = 'src/learn_english/asset/vocabulary_lists/featured.json'
LISTS_TOP_RATED = 'src/learn_english/asset/vocabulary_lists/top_rated.json'
LISTS_TEST_PREP = 'src/learn_english/asset/vocabulary_lists/test_prep.json'
LISTS_LITERATURE = 'src/learn_english/asset/vocabulary_lists/literature.json'
LISTS_MORPHOLOGY_ROOTS = 'src/learn_english/asset/vocabulary_lists/morphology_and_roots.json'
LISTS_HISTORICAL_DOCUMENTS = 'src/learn_english/asset/vocabulary_lists/historical_documents.json'
LISTS_SPEECHES = 'src/learn_english/asset/vocabulary_lists/speeches.json'
LISTS_JUST_FOR_FUN = 'src/learn_english/asset/vocabulary_lists/just_for_fun.json'
LISTS_NEWS = 'src/learn_english/asset/vocabulary_lists/news.json'

CATEGORY_DICT = {
    'test-prep': 'Test Prep',
    'literature': 'Literature',
    'morphology-and-roots': 'Morphology & Roots',
    'historical-documents': 'Historical Documents',
    'speeches': 'Speeches',
    'just-for-fun': 'Just for Fun',
    'news': 'News'
}
# -------------------------------------
REMINDER_TITLE = '温馨提醒'
REMINDER_RECITE = '◕‿↼ 今天要认真背单词呀，加油！！！✌✌✌✌'
REMINDER_REMINDER = 'ʕ•ᴥ•ʔ 今天要导出单词了，继续加油！！！ ☕☕☕'
REMINDER_FINISH = '(｡◕‿‿◕｡) 太棒了，你导出了所有单词，继续加油！！！♥‿♥'
