# -*- coding: utf-8 -*-

from ..database.db_raiseable import Raiseable

from meal_time import Mealtime
import json

class AuthResult:
	SUCCESS = 0
	ALREADY_EATEN = -101
	BANNED = -102
	UNCONFIRMED = -103
	NOCOUPON = -104
	INVALID_USER = -110
	NONE = -199

	Messages = {
		0 : "식사 처리되었습니다.",
		-101 : "이미 식사하였습니다.",
		-102 : "식사할 수 없습니다.",
		-103 : "확인되지 않은 식권입니다.",
		-104 : "식권이 존재하지 않습니다. 현장발급",
		-110 : "인벨리드_유저",
		-199 : "논"	
	}

class ResultObject(Raiseable):
	#custom error for dimigo_meal
	UserNotFound = -202
	UserMismatch = -203
	NotMealTime = -210
	MealNotFound = -212

	error_map = {
		"UserNotFound" : {"Title" : "올바르지 않은 학생증입니다.", "Message" : "학생부에 문의해 주세요."},
		"UserMismatch" : {"Title" : "잘못된 키오스크에 태그하셨습니다.", "Message" : "올바른 키오스크에 태그해 주세요."},
		"MealNotFound" : {"Title" : "식사가 발견되지 않았습니다.", "Message" : "식사 정보를 등록해 주세."},
		"NotMealTime" : {"Title" : "식사 시간이 아닙니다.", "Message" : ""}
	}
	#end

	MealObject_Empty = {"mealData" : "", "mealState" : ""}

	#user, event, meal obj
	def __init__(self):
		self._res = {"status" : 0, "user" : None, "event" : None, "meal" : None}

	#overriding
	def raise_error(self, etype, e_from, e=None):
		super(ResultObject, self).raise_error(etype, e_from, e)

		if etype == ResultObject.UserNotFound:
			etype_s = "UserNotFound"
		elif etype == ResultObject.UserMismatch:
			etype_s = "UserMismatch"
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


	def from_Table_Meal(self, mealtable, mealstate):
		mt = Mealtime(mealtable.meal_time)
		mealdata_obj = {
			"mealId" : mealtable.id,
			"isUsableRFID" : mt.card_usable(),
			"mealName" : mealtable.title == "null" and str(mt) or mealtable.title,
			"mealStartTime" : mt.get_start(),
			"mealStopTime" : mt.get_stop(),
			"mealInstanceStartTime" : mt.get_start_i(),
			"mealInstanceCouponNum": mealtable.inst_coupon_left,
			"foodList" : json.loads(mealtable.meal_json)
		}
		mealstate_obj = {
			#is_used = 1
			"processedUser" : str(mealstate[0]),
			#count all
			"totalUser" : str(mealstate[1])
		}
		#id is required for "verify" obj
		self._res['meal'] = {"mealData" : mealdata_obj, "mealState" : mealstate_obj}
		if 'user' in self._res:
			del self._res['user']

	def from_User_Student(self, user, auth_result):
		# raise Exception(user.user_data.__repr__())
		user_new_obj = {
			"name" : user.user_name,
			"grade" : user.user_data['grade'],
			"class" : user.user_data['class_num'],
			"number" : user.user_data['num'],
			"profileUrl" : user.profile_img_url
		}
		event_new_obj = {
			"status" : auth_result,
			"message" : AuthResult.Messages[auth_result]
		}
		self._res['user'] = user_new_obj
		self._res['event'] = event_new_obj
		if 'meal' in self._res:
			del self._res['meal']
		
	def from_User_Teacher(self, user, auth_result):
		user_new_obj = {
			"name" : user.user_name,
        	"department": unicode(user.user_data['department_kr']),
        	"position": unicode(user.user_data['position_kr']),
			"profileUrl" : user.profile_img_url
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
