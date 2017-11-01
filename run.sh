#!/usr/bin/env bash
pgrep -f captain | xargs kill -9

python src/learn_english/model/retrieve.py
nohup python src/captain.py &
