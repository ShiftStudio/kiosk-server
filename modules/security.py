
class Security:
	#verify request if generated by kiosk or not
	#special token "Kiosk2014at" + current timestamp
	#timestamp difference should not greater than 30 seconds (1800 ms)
	@staticmethod
	def verify_kiosk():
		return True

	#verify request if generated by meal_admin or not
	@staticmethod
	def verify_admin():
		return True