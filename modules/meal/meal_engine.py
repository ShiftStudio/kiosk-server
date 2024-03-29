# -*- coding: utf-8 -*-

from datetime import datetime, time, date

from ..database.db_engine import *
from ..intra_user import *

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

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
		self.db = get_db_instance()
		self.res = ResultObject()

	#131227 야근
	def verify(self, sid, target, t_cnt=None):
		#verify mealtime or not
		try:
			if target == "student":
				fid = self.get_now_id(target_type='s')
			elif target == "teacher":
				fid = self.get_now_id(target_type='t')
			else:
				self.raise_error(ResultObject.DataError, "Meal_Now", e)
				return self.res.get()

			if fid is None:
				self.raise_error(ResultObject.NotMealTime, "Meal_Now")
				return self.res.get()
		except Exception, e:
			self.raise_error(ResultObject.DataError, "Meal_Now", e)
			return self.res.get()

		#querying user objects from barcode
		try:
			user_by_bid = IntraUser.get_from_bid(sid)
		except NoResultFound:
			if target == "student":
				self.raise_error(ResultObject.StudentNotFound, "UserbyBarcode")
			elif target == "teacher":
				self.raise_error(ResultObject.TeacherNotFound, "UserbyBarcode")
			else:
				self.raise_error(ResultObject.UserNotFound, "UserbyBarcode")					
			return self.res.get()
		except Exception, e:
			self.raise_error(ResultObject.UserError, "UserbyBarcode", e)
			return self.res.get()


		target_map = {"student" : "s", "teacher" : "t"}
		try:
			if target_map[target] != user_by_bid.user_type:
				self.raise_error(ResultObject.UserMismatch, "TargetMap")
				return self.res.get()
		except KeyError, e:
			self.raise_error(ResultObject.UserError, "TargetMap", e)
			return self.res.get()

		#querying meal permission
		auth_result = AuthResult.NONE
		try:
			if user_by_bid.user_type == "s":
				try:
					meal = None
					meal = self.db.query(Table_Meal_Student).\
					filter_by(for_meal=fid).filter_by(owned_by=user_by_bid.id).one()
					#student can only eat meal once
					if meal.is_banned == 1:
						auth_result = AuthResult.BANNED
					else:
						if meal.is_checked_admin == 1 and meal.is_used == 0:
							meal.is_used = 1
							self.db.session.commit()
							auth_result = AuthResult.SUCCESS
						elif meal.is_checked_admin == 1 and meal.is_used == 1:
							auth_result = AuthResult.ALREADY_EATEN
						else:
							auth_result = AuthResult.UNCONFIRMED
				except NoResultFound:
					#식권 현장발급 루틴은 여기서 구현하면 안됨요, 다른 URL 만들어서 처
					auth_result = AuthResult.NOCOUPON
					

				self.res.from_User_Student(user_by_bid, auth_result)

			elif user_by_bid.user_type == "t":
				if not (int(t_cnt) >= 1 and int(t_cnt) <= 10):
					self.raise_error(ResultObject.MealOutofRange, "t_cnt out of range : must between 1 and 10")
					return self.res.get()

				#teaher blacklist check
				try:
					user = self.db.query(Table_Blacklist).\
					filter_by(user_id=user_by_bid.id).one()
					if user.is_banned == 1:
						auth_result = AuthResult.BANNED
					else:
						auth_result = AuthResult.SUCCESS
				except NoResultFound:
					#pass when no data found
					auth_result = AuthResult.SUCCESS


				if auth_result == AuthResult.SUCCESS:
					meal = Table_Meal_log_T(user_id=user_by_bid.id, for_meal=fid, count=t_cnt, modified_at=Today.today())
					self.db.session.add(meal)
					self.db.session.commit()

				self.res.from_User_Teacher(user_by_bid, auth_result)
				#self.raise_error(self.res.Debug, "NotImplemented")

		except Exception, e:
			self.raise_error(self.res.DataError, "MealLog", e)
			self.db.session.rollback()

		return self.res.get()

	#getting meal info by date and mealtime
	def get_by_dt(self, meal_date, meal_time=None, get_full=False, target_type='s'):

		# if 
		# 	#returns all object(BLDS)
		# 	pass
		if meal_time is not None:
			try:
				meal_result = self.db.query(Table_Meal).\
				filter_by(date=meal_date).filter_by(meal_time=meal_time).one()
				self.res.from_Table_Meal(meal_result, self.get_meal_state(meal_result.id), target_type)
			except NoResultFound:
				self.raise_error(self.res.MealNotFound, "MealData")
			except Exception, e:
				self.raise_error(self.res.DataError, "MealData", e)
		
		return self.res.get()


	#getting current meal info
	def get_now(self, get_full=None, target_type='s'):
		mealtype = Mealtime.get_current(target_type=target_type)
		# import pdb; pdb.set_trace()
		if mealtype is None:
			self.res.empty_Meal()
			return self.res.get()
		elif mealtype['current'] == True:
			if get_full is None:
				return self.get_by_dt(Today.today(), mealtype['time_code'], False, target_type)
			else:
				return self.get_by_dt(Today.today(), mealtype['time_code'], True, target_type)
		elif mealtype['current'] == False:
			if get_full is None:
				return self.get_by_dt(Today.today(), mealtype['time_code'], False, target_type)
			else:
				return self.get_by_dt(Today.today(), mealtype['time_code'], True, target_type)

		self.res.empty_Meal()
		return self.res.get()

	#getting current meal info
	def get_now_id(self, target_type='s'):
		mealtype = Mealtime.get_current(target_type=target_type)
		if mealtype is None: # it will never occur
			return None
		elif mealtype['current'] == True:
			try:
				meal_result = self.db.query(
					Table_Meal).filter_by(
					date=Today.today()).filter_by(meal_time=mealtype['time_code']).one()
				return meal_result.id
			except NoResultFound:
				return None
		elif mealtype['current'] == False:
			try:
				meal_result = self.db.query(
					Table_Meal).filter_by(
					date=Today.today()).filter_by(meal_time=mealtype['time_code']).one()
				return meal_result.id
			except NoResultFound:
				return None
		else:
			return None

	#injection warning
	def get_meal_state(self, meal_id):
		obj = self.db.raw_query("""SELECT 
    COUNT(IF( is_used =1, is_used, NULL )), COUNT(id) 
FROM meal_coupon_inst
WHERE for_meal = {0}""".format(meal_id)).first()
		# self.db.session.expire(obj)
		# self.db.session.refresh(obj)
		return obj
		
#NotImplemented below

	def add(self, data):
		try:
			meal_row = Table_Meal(**data)
			self.db.session.add(meal_row)
			self.db.session.commit()
		except Exception, e:
			self.raise_error(self.res.DataError, e)
			self.db.session.rollback()

		return self.res.get()


	#두 번 먹는게 가능함?
	def gift(self, meal_date, meal_time, u_from, u_to):	
		try:
			u_from = IntraUser.get_from_bid(u_from)
			u_to = IntraUser.get_from_bid(u_to)
		except NoResultFound:
			self.raise_error(ResultObject.UserNotFound, "UserbyBarcode")
			return self.res.get()
		except Exception, e:
			self.raise_error(ResultObject.UserError, "UserbyBarcode", e)
			return self.res.get()

		#verify mealtime or not
		try:
			fid = self.get_now_id()
			if fid is None:
				self.raise_error(ResultObject.NotMealTime, "Meal_Now")
				return self.res.get()
		except Exception, e:
			self.raise_error(ResultObject.DataError, "Meal_Now", e)
			return self.res.get()

		try:
			meal = self.db.query(Table_Meal_Student).\
			filter_by(for_meal=fid).filter_by(owned_by=u_from.id).one()
			#student can only eat meal once

			if meal.is_checked_admin == 1 and meal.is_used == 0:
				meal.owned_by = u_to.id
				self.db.session.commit()
				auth_result = AuthResult.SUCCESS
			elif meal.is_checked_admin == 1 and meal.is_used == 1:
				auth_result = AuthResult.ALREADY_EATEN
			else:
				auth_result = AuthResult.UNCONFIRMED
		except NoResultFound:
			auth_result = AuthResult.NOCOUPON
			
		###result should be given

	def raise_error(self, etype, e_from, e=None):
		#we really need this
		self.db.session.rollback()
		self.db.session.close()
		self.db.session.remove()

		self.res.raise_error(etype, e_from, e)
