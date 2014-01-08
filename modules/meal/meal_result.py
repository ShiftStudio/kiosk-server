# -*- coding: utf-8 -*-

from ..database.db_raiseable import Raiseable

from meal_time import Mealtime
import json

class AuthResult:
	SUCCESS = 0
	ALREADY_EATEN = -101
	BANNED = -102
	INVALID_USER = -110
	NONE = -199

	Messages = {
		0 : "식사 처리되었습니다.",
		-101 : "이미 식사하였습니다.",
		-102 : "식사할 수 없습니다.",
		-110 : "인벨리드_유저",
		-199 : "논"	
	}

class ResultObject(Raiseable):
	MealObject_Empty = {"mealData" : "", "mealState" : ""}
	#user, event, meal obj

	def __init__(self):
		self._res = {"user" : None, "event" : {"status" : 0}, "meal" : None}


	def from_Table_Meal(self, mealtable):
		mt = Mealtime(mealtable.meal_time)
		mealdata_obj = {
			"isUsableRFID" : mt.card_usable(),
			"mealName" : mealtable.title == "null" and str(mt) or mealtable.title,
			"mealStartTime" : mt.get_start(),
			"mealStopTime" : mt.get_stop(),
			"mealSupplyStartTime" : mt.get_start_s(),
			"mealSupplyStopTime" : mt.get_stop_s(),
			"mealInstanceStartTime" : mt.get_start_i(),
			#whereis 'coupon left' db?
			"mealInstanceCouponNum": None,
			"foodList" : json.loads(mealtable.meal_json)
		}
		#####################whereis 'mealstate' db?
		mealstate_obj = None
		#id is required for "verify" obj
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
			"message" : AuthResult.Messages[auth_result]
		}
		self._res['user'] = user_new_obj
		self._res['event'] = event_new_obj
		if 'meal' in self._res:
			del self._res['meal']
		
	def from_User_Teacher(self, user_name, conctable, auth_result):
		user_new_obj = {
			"name" : user_name,
        	"department": conctable.department,
        	"position": conctable.position,
			"profileUrl" : None
		}
		event_new_obj = {
			"status" : auth_result,
			"message" : AuthResult.Messages[auth_result]
		}
		self._res['user'] = user_new_obj
		self._res['event'] = event_new_obj
		if 'meal' in self._res:
			del self._res['meal']

	def empty_Meal(self):
		self._res['meal'] = ResultObject.MealObject_Empty
		if 'user' in self._res:
			del self._res['user']
		
	def get(self):
		return self._res
