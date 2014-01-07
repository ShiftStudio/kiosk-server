# -*- coding: utf-8 -*-

from datetime import datetime, time, date
from ..database.db_engine import *

from meal_db_table import *
from meal_result import ResultObject, AuthResult
from meal_time import Mealtime

#*'getting' means returning ORM object

class Today:	
	@staticmethod
	def today():
		return str(datetime.today().date())


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

	#131227 야근
	def verify(self, sid, target, t_cnt=None):
		#verify mealtime or not
		try:
			fid = self.get_now_id()
			if fid is None:
				self.res.raise_error(ResultObject.DataError, "not meal time now")
		except Exception, e:
			self.res.raise_error(ResultObject.DataError, "Meal_Now", e)
			return self.res.get()

		#querying user objects from barcode
		try:
			user_by_bid = self.db.session.query(Table_User).filter_by(b_id=sid).one()
		except Exception, e:
			self.res.raise_error(ResultObject.UserError, "UserbyBarcode", e)
			return self.res.get()

		target_map = {"student" : "s", "teacher" : "t"}
		try:
			if target_map[target] != user_by_bid.user_type:
				self.res.raise_error(ResultObject.UserError, "user_type mismatch with bnum")
				return self.res.get()
		except KeyError, e:
			self.res.raise_error(ResultObject.UserError, "TargetMap", e)
			return self.res.get()

		#querying meal permission
		auth_result = AuthResult.NONE
		try:
			if user_by_bid.user_type == "s":
				meal = self.db.session.query(Table_Meal_Student).\
				filter_by(food_id=fid).filter_by(user_id=user_by_bid.id).one()

				#student can only eat meal once
				if meal.is_allowed == True and meal.count < 1:
					meal.count += 1
					self.db.session.commit()
					auth_result = AuthResult.SUCCESS
				elif meal.is_allowed == True and meal.count >= 1:
					auth_result = AuthResult.ALREADY_EATEN
				else:
					auth_result = AuthResult.BANNED

				self.res.from_User_Student(user_by_bid.user_name, meal, auth_result)

			elif user_by_bid.user_type == "t":
				if t_cnt < 1 or t_cnt > 10:
					self.res.raise_error(ResultObject.DataError, "t_cnt out of range : must between 1 and 10")
					return self.res.get()

				meal = self.db.session.query(Table_Meal_Teacher).\
				filter_by(food_id=fid).filter_by(user_id=user_by_bid.id).one()

				#teacher can eat meal multiple times
				if meal.is_allowed == True:
					meal.count += t_cnt
					self.db.session.commit()
					auth_result = AuthResult.SUCCESS
				else:
					auth_result = AuthResult.BANNED

				self.res.from_User_Teacher(user_by_bid.user_name, meal, auth_result)
				#self.res.raise_error(self.res.Debug, "NotImplemented")

		except Exception, e:
			self.res.raise_error(self.res.DataError, "MealLog", e)
			self.db.session.rollback()

		return self.res.get()

	#getting meal info by date and mealtime
	def get_by_dt(self, meal_date, meal_time=None, get_full=False):

		if meal_time is None:
			#returns all object(BLDS)
			pass
		else:
			try:
				meal_result = self.db.session.query(Table_Meal).\
				filter_by(date=meal_date).filter_by(meal_time=meal_time).one()

				self.res.from_Table_Meal(meal_result)
			
			except Exception, e:
				self.res.raise_error(self.res.DataError, "MealData", e)

		return self.res.get()


	#getting current meal info
	def get_now(self, get_full=None):
		mealtype = Mealtime.get_current()
		if mealtype is None:
			self.res.empty_Meal()
		else:
			if get_full is None:
				return self.get_by_dt(Today.today(), mealtype, False)
			else:
				return self.get_by_dt(Today.today(), mealtype, True)

	#getting current meal info
	def get_now_id(self):
		mealtype = Mealtime.get_current()
		if mealtype is None:
			return None
		else:				
			meal_result = self.db.session.query(Table_Meal).\
				filter_by(date=Today.today()).filter_by(meal_time=mealtype).one()
			return meal_result.id


#NotImplemented below

	def add(self, data):
		try:
			meal_row = Table_Meal(**data)
			self.db.session.add(meal_row)
			self.db.session.commit()
		except Exception, e:
			self.res.raise_error(self.res.DataError, e)
			self.db.session.rollback()

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
