#!/usr/bin/env bash
nohup python src/captain.py &
sh src/learn_english/run.sh

if pgrep -q mongod; then
    echo running;
else
    mongod;
fi
exit 0;

