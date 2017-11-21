# -*- coding:utf-8 -*-
"""
extract local clipboard words to specified folder to synchronize to git repository.
"""
import utility
import constants
import database
import tackle_word


def sync_clip_words():
    store = utility.load_json_file(constants.CLIP_WORDS_FILE)
    all_local_clip_words = database.get_clipboard_word_all()

    ok = False
    for clip_word_info in all_local_clip_words:
        word = clip_word_info['word']
        if not word in store:
            store[word] = clip_word_info['usage']
            ok = True
            continue

        store[word], need_update = utility.get_concatinated_usages(
            store[word], clip_word_info['usage'])
        if need_update:
            ok = True
    if ok:
        utility.write_json_file(constants.CLIP_WORDS_FILE, store)

    tackle = tackle_word.TackleWords()
    for word, usage in store.iteritems():
        if database.get_clipboard_word_by_word(word) is None:
            tackle.query(word, usage)


if __name__ == "__main__":
    sync_clip_words()
