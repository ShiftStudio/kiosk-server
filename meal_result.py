#from db_table import *

class ResultObject:
	DataError = 0
	UserError = 1
	MealObject_Empty = {"mealData" : None}
	#user, event, meal obj

	def __init__(self):
		self._res = {"user" : None, "event" : {"status" : 0}, "meal" : None}

	def from_Table_Meal(self, mealtable):
		#meal_new_obj = 
		self._res['meal'] = meal_new_obj
		del self._res['user']

	def from_User_Student(self, usertable, mealtable):
		user_new_obj = {
			"name" : usertable.user_name,
			"grade" : 
		}
		self._res['user'] = meal_new_obj
		del self._res['meal']

	def from_User_Teacher(self):
		pass

	def empty_Meal(self):
		self._res['meal'] = MealObject_Empty
		del self._res['user']		

	
	def raise_error(self, etype, emsg, e=None):
		# -1 represents an error
		self._res['event']['status'] = -1
		if e is None:
			self._res['event'].update({"error_type" : etype, "error_msg" : emsg})
		else:
			self._res['event'].update({"error_type" : etype, "error_msg" : emsg, "error_dmp" : str(e)})

		del self._res['user']
		del self._res['meal']

	def get(self):
		return _res