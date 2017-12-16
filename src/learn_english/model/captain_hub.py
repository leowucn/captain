# -*- coding:utf-8 -*-
import os
from time import gmtime, strftime, sleep
import pyperclip
import pronunciation
import extract
import utility
import tackle_word
import constants
import db_sync


def watcher():
    tackle = tackle_word.TackleWords()
    word = ''
    ori_form = ''
    i = 0
    while True:
        result = pyperclip.paste().strip()
        if not is_valid(result):
            # p("sentence not valid!")
            sleep(constants.INTERVAL)
            continue
        # utility.log2file('word = ' + word + ' , i = ' + str(i) + ' ' + ', result = ' + result)
        if word != '' and result.find(word) >= 0:
            if word != '' and len(result) > len(word) and result.find(word) >= 0:
                sentences = extract.extract(word, result)
                if len(sentences) > 0:
                    for sentence in sentences:
                        tackle.query(ori_form + '-1', sentence,
                                     strftime("%Y-%m-%d", gmtime()))
            if word != '':
                if i >= constants.MAX_DISPLAY_TIMES:
                    os.system("echo '' | pbcopy")
                    i = 0
                    word = ''
                    continue
                pronunciation.show(ori_form, i)
                i += 1
        elif 1 < len(result) <= 20 and result.isalpha():
            word = result
            ori_form = utility.get_word_original_form(word)
            i = 0
            continue

        # # When the following condition are sufficient, Captain would look like suspend, and copy word
        # # has no any effect. This is normal, as now is the time for memorizing the word learned.
        # tackle.memorize_words()

        new_hour = utility.get_current_seconds() == 0 and utility.get_current_minute() == 0
        if new_hour:
            # sync clip words one time in each hour
            db_sync.sync_clip_words()

        day_of_week = utility.get_day_of_week()
        if day_of_week in ('Monday', 'Wednesday', 'Friday'):
            if new_hour:
                utility.show_notification(constants.REMINDER_TITLE, constants.REMINDER_RECITE)
        else:
            if new_hour:
                if tackle.check_if_has_export_kindle_words():
                    utility.show_notification(constants.REMINDER_TITLE, constants.REMINDER_FINISH)
                else:
                    utility.show_notification(constants.REMINDER_TITLE, constants.REMINDER_REMINDER)

        # let the program pause for a short time.
        sleep(constants.INTERVAL)


# clip_str should only include ascii characters.
def is_valid(clip_str):
    # for c in clip_str:
    #     if ord(c) > 127:
    #         return False
    return True


if __name__ == "__main__":
    watcher()
