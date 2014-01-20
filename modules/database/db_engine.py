import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, DisconnectionError

#from ..config_loader import config

from flask import Flask

cIntra_user_id = "intranet"
cIntra_user_pw = "3atfLwSryYrdQ7Ke"
cIntra_user_db = "intranet"

#cIntra_user_id = "root"
#cIntra_user_pw = "q1w2e3r4t5"
#cIntra_user_db = "closeapi"

instance = None

def get_db_instance():
	global instance

	if instance is None:
		instance = Intra_Database()

	return instance

class Intra_Database:
	def __init__(self):
		try:
			connect_url = "mysql://{0}:{1}@127.0.0.1/{2}?charset=utf8".format(cIntra_user_id, cIntra_user_pw, cIntra_user_db)
			self.db_engine = create_engine(connect_url, pool_recycle=300)
			# event.listen(db_engine, 'checkout', self.checkout_listener)   
			self.connection = self.db_engine.connect()
			
			self.session = scoped_session(sessionmaker(autocommit=False, bind=self.db_engine))

		except OperationalError:
				logging.error("DBError : please check database connection.")
				exit(1)

	def query(self, args):
		# self.session.begin()
		data = self.session.query(args)
		# self.session.commit()
		return data

	def raw_query(self, querystr):
		# try:
		# 	# self.connection.
		# 	return self.connection.execute(querystr)
		# except OperationalError, e:
		# 	#solutions for disconnection error
		# 	if "2006" in str(e):
		self.connection = self.db_engine.connect()
		return self.connection.execute(querystr)


app = Flask(__name__)
@app.teardown_appcontext
def shutdown_session(exception=None):
		self.session.remove()
