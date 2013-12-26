# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from datetime import datetime, time, date
from db_engine import *
from db_table import *
from meal_result import ResultObject

#*'getting' means returning ORM object

class Today:	
	@staticmethod
	def today():
		return str(datetime.today().date())

	#based on DIMIGO's meal timetable
	#will store on MEMCACHE later
	@staticmethod
	def mealtype():
		b_start	 = Today.strtot("7:00:00")
		b_end	 = Today.strtot("9:00:00")
		l_start	 = Today.strtot("12:00:00")
		l_end	 = Today.strtot("13:00:00")
		d_start	 = Today.strtot("18:00:00")
		d_end	 = Today.strtot("19:30:00")
		s_start	 = Today.strtot("20:50:00")
		s_end	 = Today.strtot("21:30:00")
		now = datetime.today().time()

		if b_start <= now <= b_end:
			return "B"
		elif l_start <= now <= l_end:
			return "L"
		elif d_start <= now <= d_end:
			return "D"
		elif s_start <= now <= s_end:
			return "S"
		else:
			return None
		return "B"

	@staticmethod
	def strtot(time_str):
		return datetime.strptime(time_str, "%H:%M").time()

class ClassHelper:
	@staticmethod
	def row2dict(row):
		d = {}
		for column in row.__table__.columns:
			d[column.name] = getattr(row, column.name)

		return d

	@staticmethod
	def dict2row(dict):
		pass


class Meal:
	def __init__(self):
		self.db = Intra_Database()
		self.res = ResultObject()

	def verify(self, sid, target):
		#verify mealtime or not
		fid = self.get_now()["id"]
		if fid is None:
			self.res.raise_error(ResultObject.DataError, "not meal time now")

		#querying user objects from barcode
		try:
			user_by_bid = self.db.session.query(Table_User).filter_by(b_id=sid).one()
		except MultipleResultsFound, e:
			self.res.raise_error(ResultObject.UserError, "duplicate bnum of user", e)
		except NoResultFound, e:
			self.res.raise_error(ResultObject.UserError, "invalid bnum for user", e)


		target_map = {"student" : "s", "teacher" : "t"}
		if target_map[target] != user_by_bid.user_type:
			self.res.raise_error(ResultObject.UserError, "user_type mismatch with bnum")

		#querying meal permission
		try:
			meal_result = self.db.session.query(Table_Meal_log).filter_by(food_id=fid).filter_by(user_id=user_by_bid.id)
			meal_result = meal_result.one()
			if meal_result.is_allowed == False:
				#return {"meal" : "no", "username" : user_by_bid.user_name}

			elif user_by_bid.user_type == "s" and meal_result.count >= 1:
				#return {"meal" : "student.already_yumyum", "username" : user_by_bid.user_name}

			else:
				meal_result.count += 1
				#does it work? yes! 
				self.db.session.commit()
##########				return {"user" : user_by_bid}
		except MultipleResultsFound, e:
			self.res.raise_error(self.res.DataError, "duplicate result", e)
		except NoResultFound, e:
			self.res.raise_error(self.res.DataError, "Meal_log not found", e)

		return self.res.get()

	#getting meal info by date and mealtime
	def get_by_dt(self, meal_date, meal_time):
		#returns all object(BLDS)
		if meal_time is None:
			pass
		else:
			try:
				meal_result = self.db.session.query(Table_Meal).filter_by(date=meal_date).filter_by(meal_time=meal_time)
				meal_result = meal_result.one()

				#object to JSON conversion?
				meal_result = ClassHelper.row2dict(meal_result)
				#convert datetime.date to string
				if type(meal_result["date"]) is date:
					meal_result["date"] = str(meal_result["date"])
				meal_result["meal"] = "yes"
#########				return meal_result

			except MultipleResultsFound, e:
				self.res.raise_error(self.res.DataError, "duplicate result", e)
			except NoResultFound, e:
				self.res.raise_error(self.res.DataError, "no result found")

		return self.res.get()


	#getting current meal info
	def get_now(self, get_full=None):
		mealtype = Today.mealtype()
		if mealtype is None:
			self.res.empty_Meal()
		else:
			if get_full is None:
				return self.get_by_dt(Today.today(), Today.mealtype())
			else:
				raise Exception()


#NotImplemented below

	def add(self, data):
		try:
			meal_row = Table_Meal(**data)
			self.db.session.add(meal_row)
			self.db.session.commit()
		except Exception, e:
			self.res.raise_error(self.res.DataError, str(e))

		return self.res.get()


#두 번 먹는게 가능함?

	def gift(self, meal_date, meal_time, u_from, u_to):	
		try:
			meal_result = self.db.session.query(Table_Meal).filter_by(date=meal_date).filter_by(meal_time=meal_time)
			fid = meal_result.one().id

			meal_tables = self.db.session.query(Table_Meal_log).filter_by(food_id=fid)
			#'from' and 'to' must be uid
			meal_from = meal_tables.filter_by(user_id=u_from)
		
		except MultipleResultsFound, e:
			self.res.raise_error(self.res.DataError, "duplicate result", e)
		except NoResultFound, e:
			self.res.raise_error(self.res.DataError, "no result found")
