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
	#custom error for dimigo_meal
	UserNotFound = -202
	UserMisMatch = -203
	NotMealTime = -210
	MealNotFound = -212

	error_map = {
		"UserNotFound" : {"Title" : "올바르지 않은 학생증입니다.", "Message" : "학생부에 문의해 주세요."},
		"UserMisMatch" : {"Title" : "잘못된 키오스크에 태그하셨습니다.", "Message" : "올바른 키오스크에 태그해 주세요."},
		"MealNotFound" : {"Title" : "식사가 발견되지 않았습니다.", "Message" : "식사 정보를 등록해 주세."},
		"NotMealTime" : {"Title" : "식사 시간이 아닙니다.", "Message" : ""}
	}
	#end

	MealObject_Empty = {"mealData" : "", "mealState" : ""}

	#user, event, meal obj
	def __init__(self):
		self._res = {"user" : None, "event" : {"status" : 0}, "meal" : None}

	#overriding
	def raise_error(self, etype, e_from, e=None):
		super(ResultObject, self).raise_error(etype, e_from, e)

		if etype == ResultObject.UserNotFound:
			etype_s = "UserNotFound"
		elif etype == ResultObject.UserMisMatch:
			etype_s = "UserMisMatch"
		elif etype == ResultObject.NotMealTime:
			etype_s = "NotMealTime"
		elif etype == ResultObject.MealNotFound:
			etype_s = "MealNotFound"

		if e is None:
			#etype must be converted if errorObject is not given
			assert(etype_s is not None), TypeError

			self._res["status"] = etype
			self._res["event"]["errorType"] = etype_s
			self._res.update(ResultObject.error_map[etype_s])


	def from_Table_Meal(self, mealtable):
		mt = Mealtime(mealtable.meal_time)
		mealdata_obj = {
			"isUsableRFID" : mt.card_usable(),
			"mealName" : mealtable.title == "null" and str(mt) or mealtable.title,
			"mealStartTime" : mt.get_start(),
			"mealStopTime" : mt.get_stop(),
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
