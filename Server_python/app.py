#coding:utf-8

import connexion
import datetime
import logging
import json

from connexion import NoContent

# 依存分析
def dependency_analysis(sentence_json):
    # 判断是否包含固定字段
    print("hello world")

logging.basicConfig(level=logging.INFO)
app = connexion.FlaskApp(__name__)
app.add_api('swagger.yaml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=9988)
    print("server is start, and port is 9988")

