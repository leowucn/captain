#!/usr/bin/env bash
./captain_env/bin/python2.7 src/learn_english/model/retrieve.py
nohup ./captain_env/bin/python2.7 src/learn_english/model/db_sync.py &
nohup ./captain_env/bin/python2.7 src/learn_english/model/tackle_word.py &
nohup ./captain_env/bin/python2.7 src/learn_english/model/captain_hub.py &
nohup ./captain_env/bin/python2.7 src/learn_english/model/vocabulary_list.py &
