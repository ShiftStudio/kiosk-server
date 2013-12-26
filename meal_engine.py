# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from datetime import datetime, time, date
from db_engine import *
from db_table import *
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
	def verify(self, sid, target):
		#verify mealtime or not
		#이거 뭔가 마음에 안듬
		fid = self.get_now()['meal']['id']
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
		try:
			if target_map[target] != user_by_bid.user_type:
				self.res.raise_error(ResultObject.UserError, "user_type mismatch with bnum")
		except KeyError:
			self.res.raise_error(ResultObject.UserError, "unknown target. target must be either student or teacher")

		#querying meal permission
		auth_result = AuthResult.NONE
		try:
			if user_by_bid.user_type == "s":
				meal_result = self.db.session.query(Table_Meal_log).join(Table_User_S).\
				filter_by(user_id=user_by_bid.id).filter_by(food_id=fid).one()

				#student can only eat meal once
				if meal_result.is_allowed == True and meal_result.count < 1:
					meal_result.count += 1
					self.db.session.commit()
					auth_result = AuthResult.SUCCESS
				elif meal_result.is_allowed == True and meal_result.count >= 1:
					auth_result = AuthResult.ALREADY_EATEN
				else:
					auth_result = AuthResult.BANNED

				self.res.from_User_Student(user_by_bid.user_name, meal_result, auth_result)

			elif user_by_bid.user_type == "t":
				meal_result = self.db.session.query(Table_Meal_log).join(Table_User_T).\
				filter_by(user_id=user_by_bid.id).filter_by(food_id=fid).one()

				#teacher can eat meal multiple times
				if meal_result.is_allowed == True:
					meal_result.count += 1
					self.db.session.commit()
					auth_result = AuthResult.SUCCESS
				else:
					auth_result = AuthResult.BANNED

				self.res.from_User_Student(user_by_bid.user_name, meal_result, auth_result)

		except MultipleResultsFound, e:
			self.res.raise_error(self.res.DataError, "duplicate result", e)
		except NoResultFound, e:
			self.res.raise_error(self.res.DataError, "Meal_log not found", e)
		except Exception, e:
			self.res.raise_error(self.res.DataError, "general Database error", e)

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

			except MultipleResultsFound, e:
				self.res.raise_error(self.res.DataError, "duplicate result", e)
			except NoResultFound, e:
				self.res.raise_error(self.res.DataError, "no result found", e)
			except Exception, e:
				self.res.raise_error(self.res.DataError, "general Database error", e)

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
		return self.res.get()


#NotImplemented below

	def add(self, data):
		try:
			meal_row = Table_Meal(**data)
			self.db.session.add(meal_row)
			self.db.session.commit()
		except Exception, e:
			self.res.raise_error(self.res.DataError, e)

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
