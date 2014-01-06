# -*- coding: utf-8 -*-

from datetime import datetime

class Mealtime:

	#based on DIMIGO's meal timetable
	#will store on MEMCACHE later
	strtot = lambda time : datetime.strptime(time, "%H:%M:%S").time()

	b_start	 = strtot("7:00:00")
	b_end	 = strtot("9:00:00")
	l_start	 = strtot("12:00:00")
	l_end	 = strtot("13:00:00")
	d_start	 = strtot("18:00:00")
	d_end	 = strtot("19:30:00")
	s_start	 = strtot("20:50:00")
	s_end	 = strtot("21:30:00")

	mt_map = {"B" : "아침", "L" : "점심", "D" : "저녁", "S" : "간식"}

	def __init__(self, mt):
		self.mt = mt

	def __repr__(self):
		return Mealtime.mt_map[self.mt]

	#잔류급식도 있잖아....
	def card_usable(self):
		return True

		#use memcached later
	def get_start(self):
		if self.mt == "B":
			return str(Mealtime.b_start)
		elif self.mt == "L":
			return str(Mealtime.l_start)
		elif self.mt == "D":
			return str(Mealtime.d_start)
		elif self.mt == "S":
			return str(Mealtime.s_start)

	def get_stop(self):
		if self.mt == "B":
			return str(Mealtime.b_end)
		elif self.mt == "L":
			return str(Mealtime.l_end)
		elif self.mt == "D":
			return str(Mealtime.d_end)
		elif self.mt == "S":
			return str(Mealtime.s_end)


	def get_start_s(self):
		return self.get_start()

	def get_stop_s(self):
		return self.get_stop()

	def get_start_i(self):
		return self.get_start()

	@classmethod
	def get_current(cls):
		now = datetime.today().time()
##debugCode
		return "B"

		if cls.b_start <= now <= cls.b_end:
			return "B"
		elif cls.l_start <= now <= cls.l_end:
			return "L"
		elif cls.d_start <= now <= cls.d_end:
			return "D"
		elif cls.s_start <= now <= cls.s_end:
			return "S"
		else:
			return None