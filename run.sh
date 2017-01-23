#!/usr/bin/env bash
cd kindle
python retrieve.py
cd ..

cd word
python tackle_word.py
cd ..

nohup python word/clipboard.py &
nohup python present/captain.py &
