# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class Raiseable(object):

	#derives from exception
	DataError = 1
	UserError = 2

	Debug = 99

	error_map = {
		"MultipleResultsFound" : {"status" : -301, "Title" : "값 중복", "Message" : "의도되지 않은 중복된 값 발견"},
		"NoResultFound" : {"status" : -302, "Title" : "값 발견되지 않음", "Message" : "존재하지 않는 값입니다."}
	}

	def raise_error(self, etype, e_from, e=None):
		
		#assigning error_type
		if etype == Raiseable.DataError:
			etype_s = "DataError"
		elif etype == Raiseable.UserError:
			etype_s = "UserError"

		#clearing result for avoiding confilcts
		self._res = {'event' : {}}
		self._res['event'].update({"errorType" : etype_s, "errorFrom" : e_from, "error" : name(e)})
		
		if e is not None:
			self._res['Title'] = "내부 오류"
			self._res['event']['errorDump'] = str(e)
			#assigning error_code(status)		
			#find error code in mapper object
			try:
				self._res.update(Raiseable.error_map[name(e)])
			except KeyError:
				self._res["status"] = -399
				self._res['Message'] = "예상되지 않은 "+name(e)+"@"+e_from


def name(exc):
	return exc.__class__.__name__

