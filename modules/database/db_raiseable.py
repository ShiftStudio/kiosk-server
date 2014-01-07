from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class Raiseable:
	DataError = 0
	UserError = 1
	Debug = 99

	error_map = {

	}

	def raise_error(self, etype, emsg, e=None):
		#assigning error_type
		if etype == Raiseable.DataError:
			etype = "DataError"
		elif etype == Raiseable.UserError:
			etype = "UserError"

		#assigning error_code(status)		
		#find error code in mapper object
		try:
			self._res['event']['status'] = Raiseable.error_map[emsg]
		except KeyError:
			if type(e) is MultipleResultsFound:
				self._res['event']['status'] = -301
			elif type(e) is NoResultFound:
				self._res['event']['status'] = -302
			else:
				self._res['event']['status'] = -1

		if e is None:
			self._res['event'].update({"error_type" : etype, "message" : emsg})
		else:
			self._res['event'].update({"error_type" : etype, "message" : emsg, "error_dmp" : str(e)})
