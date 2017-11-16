#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from learn_english.view.learn_english import learn_english_app


app = Flask(__name__)

# 学英语模块
app.register_blueprint(learn_english_app, url_prefix='/learn_english')

app.run(host='127.0.0.1', port=9527, threaded=True,
        debug=True, use_reloader=True)
