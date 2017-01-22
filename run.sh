#!/usr/bin/env bash
nohup python kindle/retrieve.py &
nohup python word/tackle_word.py &
nohup python word/clipboard.py &
nohup python present/captain.py &
