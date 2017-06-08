#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from learn_english.view.learn_english import learn_english_app
import os


app = Flask(__name__)

# 学英语模块
app.register_blueprint(learn_english_app, url_prefix='/learn_english')
os.system("sh src/learn_english/run.sh")


app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)
