#!/usr/bin/env bash
python src/learn_english/model/retrieve.py
nohup python src/learn_english/model/db_sync.py &
nohup python src/learn_english/model/tackle_word.py &
nohup python src/learn_english/model/captain_hub.py &
nohup python src/learn_english/model/vocabulary_list.py &
