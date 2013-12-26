# -*- coding: utf-8 -*-

from meal_time import Mealtime
import json

class AuthResult:
	SUCCESS = 0
	ALREADY_EATEN = -1
	BANNED = -2
	INVALID_USER = -10
	NONE = -99

	Messages = {
		"0" : "석쎼스",
		"-1" : "얼레디_이튼",
		"-2" : "밴드",
		"-10" : "인벨리드_유저"	
	}

class ResultObject:
	DataError = 0
	UserError = 1
	MealObject_Empty = {"mealData" : "", "mealState" : ""}
	#user, event, meal obj

	def __init__(self):
		self._res = {"user" : None, "event" : {"status" : 0}, "meal" : None}


	def from_Table_Meal(self, mealtable):
		mt = Mealtime(mealtable.meal_time)
		mealdata_obj = {
			"isUsableRFID" : mt.card_usable(),
			"mealTime" : str(mt),
			"mealStartTime" : mt.get_start(),
			"mealStopTime" : mt.get_stop(),
			"mealSupplyStartTime" : mt.get_start_s(),
			"mealSupplyStopTime" : mt.get_stop_s(),
			"mealInstanceStartTime" : mt.get_start_i(),
			#whereis 'coupon left' db?
			"mealInstanceCouponNum": None,
			"mealName" : mealtable.title,
			"foodList" : json.loads(mealtable.meal_json)
		}
		#####################whereis 'mealstate' db?
		mealstate_obj = None
		self._res['meal'] = {"mealData" : mealdata_obj, "mealState" : mealstate_obj}
		
	def from_User_Student(self, user_name, conctable, auth_result):
		user_new_obj = {
			"name" : user_name,
			"grade" : conctable.grade,
			"class" : conctable.cls,
			"number" : conctable.number,
			"profileUrl" : None
		}
		event_new_obj = {
			"status" : auth_result,
			"message" : AuthResult.Messages[str(auth_result)]
		}
		self._res['user'] = meal_new_obj
		
	def from_User_Teacher(self, user_name, conctable, auth_result):
		pass

	def empty_Meal(self):
		self._res['meal'] = ResultObject.MealObject_Empty
		
	
	def raise_error(self, etype, emsg, e=None):
		# -1 represents an error
		self._res['event']['status'] = -1
		if e is None:
			self._res['event'].update({"error_type" : etype, "error_msg" : emsg})
		else:
			self._res['event'].update({"error_type" : etype, "error_msg" : emsg, "error_dmp" : str(e)})

		# del self._res['user']
		# del self._res['meal']

	def get(self):
		return self._res
