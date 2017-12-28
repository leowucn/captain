#!/usr/bin/env bash
nohup ./captain_env/bin/python2.7 src/captain.py &
sh src/learn_english/run.sh
open -a /Applications/Google\ Chrome.app http://127.0.0.1:9527/learn_english/

if pgrep -q mongod; then
    echo running;
else
    mongod &
fi
exit 0;

