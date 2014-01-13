# -*- coding: utf-8 -*-

import urllib2
import json

#just an exception object
from sqlalchemy.orm.exc import NoResultFound

class IntraUser:

	cCard_query_url = "http://account.shiftstud.io/closeapi/card_id/"

	@classmethod
	def get_from_bid(cls, bid):

		#string to int conversion to sanitize non-number value
		#bid = int(bid)
		try:
			req = urllib2.Request(cls.cCard_query_url + bid)
			req.add_header('X-DIMIGO-SHIFT-SSO-AUTH', 'AUTHORIZED')
			r = urllib2.urlopen(req).read()

			resp_data = json.loads(r)
			
			if resp_data['status'] != "success":
				if "wrong" in resp_data['message']:
					raise NoResultFound
				else:
					raise Exception("asd")#resp_data['message'])
			else:
				return IntraUser(**resp_data)
		#do not return status value when success, weird
		except KeyError:
			return IntraUser(**resp_data)
		except urllib2.HTTPError, e:
			if e.code == 400:
				raise NoResultFound

	def __init__(self, **entries): 
		self.__dict__.update(entries)

