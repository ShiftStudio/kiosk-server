# -*- coding: utf-8 -*-

from datetime import datetime, time

from ..database.db_engine import get_db_instance
from meal_db_table import Table_Mealtime


class Mealtime:

	def format_time(self, dt):

		return time.strftime(dt, "%H:%M:%S")

	def __init__(self, mt):

		mt = str(mt)
		#relation으로 묶여있으니 Exception 생길일은 없을듯
		self.mt_map = get_db_instance().query(Table_Mealtime).\
		filter_by(time_code=mt).one()

	def is_serving(self):
		return True

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

#		pdb.set_trace()

		for mt in mt_map:
			if mt.start_time < now < mt.end_time:
				return mt.time_code

		return None