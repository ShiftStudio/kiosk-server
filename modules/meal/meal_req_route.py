# -*- coding: utf-8 -*-
assert(__name__ != "__main__"), "No direct calling allowed"

from flask import Flask, request, abort, redirect, json

from modules.security import Security
from modules.meal.meal_engine import Meal, Today

app = Flask(__name__)
meal = Meal()
security = Security()

#external status code (flask)
ext_status = 0
#result object
s_res = {}


#redirect to intranet when connected with no args
@app.route('/meal/')
@app.route('/meal/gift/')
@app.route('/meal/verify/')
@app.route('/meal/register/')
def redr_m():
	return redirect("http://www.dimigo.hs.kr")

#Things to do:
#1. /meal/teacher/new?i=sth_to_go
#2. /meal/teacher/verify?i=sth_to_go
#3. /meal/student/verify?i=sth_to_go

@app.route('/meal/verify/<target>', methods=['POST'])
def verify(target):
	global ext_status, s_res

	if not security.verify_kiosk:
		return redirect("http://www.dimigo.hs.kr")

	#sid = request.args.get('RFIDCode')
	try:
		sid_json = json.loads(request.form['data'])
		sid = sid_json['RFIDCode']
		
		#int to string conversion
		if type(sid) is int:
			sid = str(sid)
		
		if sid is not None:
			if target == "student":
				s_res = meal.verify(sid, target)
			elif target == "teacher":
				t_cnt = sid_json['MealCount']
				s_res = meal.verify(sid, target, t_cnt)
			else:
				ext_status = "invalid_target"
		else:
			ext_status = "insufficient_variables"

	except KeyError, e:
		ext_status = "insufficient_variables"
		s_res = {"error" : str(e)}
	except ValueError, e:
		ext_status = "invalid_json"
		s_res = {"error" : str(e)}

	return make_json_response();

meal_type = ('B', 'L', 'D', 'S')

#특정 날짜의 조/중/석/간식 중 하나를 JSON Format으로 받기
@app.route('/meal/<date>/<time>')
@app.route('/meal/<date>/<time>/<action>')
def get_meal(date, time, action=None):
	global ext_status, s_res

	if time not in meal_type:
		ext_status = "invalid_target"
	else:
		#to register
		if action == "add":
			try:
				all_data = json.loads(request.form['data'])
				meal_json = all_data['meal']
				nut_json = all_data['nutrition']
				nat_json = all_data['nation']
				s_res = meal.add(date, time, 
					meal_json, nut_json, nat_json)
			except Exception, e:
				ext_status = "JSONError"
				s_res = {"error" : str(e)}
		#to retrieve
		else:
			s_res = meal.get_by_dt(date, time)

	return make_json_response()

#오늘 급식 정보 가져오기, returns array
@app.route('/meal/today/')
def get_today_meal(full=None):

	today_arr = []
	for mt in meal_type:
		today_arr.append(meal.get_by_dt(Today.today(), mt))
	s_res = {"meal_arr" : today_arr}

	return make_json_response()

@app.route('/meal/today/full/')
def get_today_meal_full():
	pass

#현재 급식 정보 가져오기, 없을 수도 있음
@app.route('/meal/now/')
def get_now_meal():

	now_meal = meal.get_now()
	return make_json_response(now_meal)

#현재 급식 현황(MealState) 가져오기
@app.route('/meal/now/state/')
def get_now_state():

	now_meal = meal.get_now_state()
	return make_json_response(now_meal)


#식권 선물하기는 아무때나 가능함
@app.route('/meal/gift/<time>/<from_id>/to/<to_id>')
def gift_meal_coupon(time, from_id, to_id):
	global s_res
	#잔류식권도 선물이 가능하여 시간별로 나누어 놓음
	if time not in meal_type:
		ext_status = "invalid_target"
	else:
		s_res = meal.gift(Today.today(), time, from_id, to_id)
		return make_json_response()
		

@app.route('/meal/new', methods=['POST'])
def add_new_meal():
	meal_data_json = request.form["data"]
	meal_data = json.loads(meal_data_json)

	# for md in meal_data:
	# 	meal.add(md)
	# return make_json_response()

def make_json_response(new_objects=None):

	if new_objects is None:
		s_res.update({"ext_status" : ext_status})
		return json.jsonify(s_res)
	else:
		new_objects.update({"ext_status" : ext_status})
		return json.jsonify(new_objects)



