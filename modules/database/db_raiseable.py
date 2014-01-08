# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class Raiseable:
	DataError = 0
	UserError = 1
	UserNotFound = 12
	Debug = 99

	error_map = {
		"MultipleResultsFound" : -301,
		"NoResultFound" : -302
	}

	error_msg_map = {
		"MultipleResultsFound" : "의도되지 않은 중복된 값 발견",
		"NoResultFound" : "존재하지 않는 값입니다."
	}

	def raise_error(self, etype, e_from, e=None):
		#assigning error_type
		if etype == Raiseable.DataError:
			etype = "DataError"
		elif etype == Raiseable.UserError:
			etype = "UserError"
		elif etype == Raiseable.UserNotFound:
			etype = "UserNotFound"		

		#clearing result for avoiding confilcts
		self._res = {'event' : {}}
		self._res['Title'] = "의도적 내부 오류"
		self._res['event'].update({"error_type" : etype, "error_from" : e_from, "error" : str(type(e))})
		
		if e is not None:
			self._res['Title'] = "내부 오류"
			self._res['event']['error_dmp'] = str(e)
			#assigning error_code(status)		
			#find error code in mapper object
			try:
				self._res['event']['status'] = Raiseable.error_map[str(type(e))]
				self._res['Message'] = Raiseable.error_msg_map[str(type(e))]
			except KeyError:
				self._res['event']["status"] = -399
				self._res['Message'] = "예상되지 않은 "+str(type(e))+"@"+e_from
		#땜빵용 코드
		if etype == "UserNotFound":
			self._res['Title'] = '등록되지 않은 학생증입니다'
			self._res['Message'] = '학생부로 문의해 주세요'
