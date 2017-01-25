#!/usr/bin/env bash
cd kindle
python retrieve.py
cd ..

nohup python word/tackle_word.py &

cd word
nohup python clipboard.py &
cd ..

nohup python present/captain.py &
