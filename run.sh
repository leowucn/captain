#!/usr/bin/env bash
python kindle/retrieve.py
nohup python core/tackle_word.py &
nohup python core/clipboard.py &
nohup python present/captain.py &
