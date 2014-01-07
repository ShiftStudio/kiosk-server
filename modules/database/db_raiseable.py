from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class Raiseable:
	DataError = 0
	UserError = 1
	Debug = 99

	error_map = {

	}

	def raise_error(self, etype, e_from, e=None):
		#assigning error_type
		if etype == Raiseable.DataError:
			etype = "DataError"
		elif etype == Raiseable.UserError:
			etype = "UserError"

		#clearing result for avoiding confilcts
		self._res = {'event' : {}}

		self._res['event'].update({"error_type" : etype, "error_from" : e_from})
		
		if e is not None:
			self._res['event']['error_dmp'] = str(e)
			#assigning error_code(status)		
			#find error code in mapper object
			try:
				self._res['event']['status'] = Raiseable.error_map[str(type(e))]
			except KeyError:
				if type(e) is MultipleResultsFound:
					self._res['event'].update({"status" : -301, "message" : "unexpected multiple result found"})
				elif type(e) is NoResultFound:
					self._res['event'].update({"status" : -302, "message" : "no result found"})
				else:
					self._res['event'].update({"status" : -302, "message" : "Unhandled Exception"})

