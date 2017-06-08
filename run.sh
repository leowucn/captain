#!/usr/bin/env bash
pgrep -f captain | xargs kill -9

nohup python src/captain.py &
