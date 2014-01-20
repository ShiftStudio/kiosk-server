# -*- coding: utf-8 -*-

from datetime import datetime, time

from ..database.db_engine import get_db_instance
from meal_db_table import Table_Mealtime


class Mealtime:

	current = False

	def format_time(self, dt):

		return time.strftime(dt, "%H:%M:%S")

	def __init__(self, mt, target_type='s'):

		mt = str(mt)
		#relation으로 묶여있으니 Exception 생길일은 없을듯
		self.mt_map = get_db_instance().query(Table_Mealtime).\
		filter_by(time_code=mt, type=target_type).one()

	def is_serving(self):
		return Mealtime.current
		# return True

		#use memcached later
	def get_start(self):
		return self.format_time(self.mt_map.start_time)

	def get_stop(self):
		return self.format_time(self.mt_map.end_time)

	def get_start_i(self):
		return self.get_start()


	@classmethod
	def get_current(cls):
		now = datetime.today().time()
		mt_map = get_db_instance().query(Table_Mealtime)

		for mt in mt_map:
			if mt.start_time < now < mt.end_time:
				Mealtime.current = True
				return { "time_code": mt.time_code, "current" : True}
		before = None
		for mt in mt_map:
			before = mt
			if now < mt.start_time:
				Mealtime.current = False
				return { "time_code": before.time_code, "current" : False}
		return None # it will never occur