#!/usr/bin/env bash
cd kindle
python retrieve.py
cd ..

nohup python word/tackle_word.py &
nohup python word/clipboard.py &
nohup python present/captain.py &
