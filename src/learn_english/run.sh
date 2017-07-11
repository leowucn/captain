#!/usr/bin/env bash
pgrep -f tackle_word | xargs kill -9
pgrep -f clipboard | xargs kill -9

python src/learn_english/model/retrieve.py
nohup python src/learn_english/model/tackle_word.py &
nohup python src/learn_english/model/clipboard.py &
nohup python src/learn_english/model/fetch_list.py &
