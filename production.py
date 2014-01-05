#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask

#후에 택배와 외출 구현할 예정. (py_core to kiosk), 급식은 admin socket 통하여 관리
#아니 택배랑 외출은 할 필요 읎겠다 당분간은

app = Flask(__name__)


#importing meal module
from modules.meal.meal_req_route import *


#redirect to intranet when connected with no args
@app.route('/')
def hello():
	return redirect("http://www.dimigo.hs.kr")

if __name__ == '__main__':
	app.run(debug=True)
	#app.run(host='0.0.0.0')
