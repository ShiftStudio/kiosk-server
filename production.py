#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, url_for, request, json, abort, redirect

#(py_core to intra_db)
from meal_engine import Meal, Today
#후에 택배와 외출 구현할 예정. (py_core to kiosk), 급식은 admin socket 통하여 관리
#아니 택배랑 외출은 할 필요 읎겠다 당분간은
#from kiosk_engine import Kiosk_Meal
from security import Security
from datetime import date

app = Flask(__name__)
meal = Meal()
security = Security()

status = 0
s_res = {}


#redirect to intranet when connected with no args
@app.route('/')
@app.route('/meal/')
@app.route('/meal/gift/')
@app.route('/meal/verify/')
@app.route('/meal/register/')
def hello():
	return redirect("http://www.dimigo.hs.kr")

#Things to do:
#1. /meal/teacher/new?i=sth_to_go
#2. /meal/teacher/verify?i=sth_to_go
#3. /meal/student/verify?i=sth_to_go

@app.route('/meal/verify/<target>')
def verify(target):
	if not security.verify_kiosk:
		return redirect("http://www.dimigo.hs.kr")

	#sid = request.args.get('id')
	sid_json = request.args.post('data');
	sid = json.loads(sid_json)['RFIDCode'];

	if sid is not None:
		if target == "student" or "teacher":
			s_res = meal.verify(sid, target)
		else:
			status = "invalid_target"
	else:
		status = "insufficient_variables"
	return make_json_response(status, s_res);

meal_type = ('B', 'L', 'D', 'S')

#특정 날짜의 조/중/석/간식 중 하나를 JSON Format으로 받기
@app.route('/meal/<date>/<time>')
@app.route('/meal/<date>/<time>/<action>')
def get_meal(date, time, action=None):

	if time not in meal_type:
		status = "invalid_target"
	else:
		#to register
		if action == "add":
			try:
				all_data = json.loads(request.args.post('data'))
				meal_json = all_data['meal']
				nut_json = all_data['nutrition']
				nat_json = all_data['nation']
				s_res = meal.add(date, time, 
					meal_json, nut_json, nat_json)
			except Exception, e:
				status = "JSONError"
				s_res = {"error" : str(e)}
		#to retrieve
		else:
			s_res = meal.get_by_dt(date, time)

	return make_json_response(status, s_res)

#오늘 급식 정보 가져오기, returns array
@app.route('/meal/today/<full>')
def get_today_meal(full=None):
	today_arr = []
	for mt in meal_type:
		today_arr.append(meal.get_by_dt(Today.today(), mt))
	s_res = {"meal_arr" : today_arr}

	return make_json_response(status, s_res)


#현재 급식 정보 가져오기, 없을 수도 있음
@app.route('/meal/now/<full>')
def get_now_meal(full=None):
	now_meal = meal.get_now(full)
	return make_json_response(status, now_meal)

#현재 급식 현황(MealState) 가져오기
@app.route('/meal/now/state')
def get_now_state():
	now_meal = meal.get_now_state()
	return make_json_response(status, now_meal)


#식권 선물하기는 아무때나 가능함
@app.route('/meal/gift/<time>/<from_id>/to/<to_id>')
def gift_meal_coupon(time, from_id, to_id):
	#잔류식권도 선물이 가능하여 시간별로 나누어 놓음
	if time not in meal_type:
		status = "invalid_target"
	else:
		s_res = meal.gift(Today.today(), time, from_id, to_id)
		return make_json_response(status, s_res)
		

@app.route('/meal/new', methods=['POST'])
def add_new_meal():
	meal_data_json = request.args.post("data")
	meal_data = json.loads(meal_data_json)
	try:
		for md in meal_data:
			meal.add(md)
		return make_json_response(status)
	except Exception, e:
		return make_json_response("error", {"error_dmp" : str(e)})

#########Kiosk commands#########

def make_json_response(status, objects=None):
	if objects is None:
		return json.jsonify({"status" : status})

	objects["status"] = status
	return json.jsonify(objects)


if __name__ == '__main__':
	app.run(debug=True)
	#app.run(host='0.0.0.0')

