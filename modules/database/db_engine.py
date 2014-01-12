from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, DisconnectionError

from flask import Flask

cIntra_user_id = "closeapi"
cIntra_user_pw = "82YwNQxLvMQeGeVx"
cIntra_user_db = "intra_meal"

# cIntra_user_id = "root"
# cIntra_user_pw = "Qawsedrf1234"
# cIntra_user_db = "intra_meal"


#from ccolor.py
RED = '\033[91m'		#red
WHITE = '\033[0m'		#ffffff

class Intra_Database:
	def __init__(self):
		try:
			connect_url = "mysql://{0}:{1}@127.0.0.1/{2}?charset=utf8".format(cIntra_user_id, cIntra_user_pw, cIntra_user_db)
			db_engine = create_engine(connect_url, pool_recycle=300)
#			event.listen(db_engine, 'checkout', self.checkout_listener)   
			self.connection = db_engine.connect()
			
			self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db_engine))

		except OperationalError:
				print RED+"DBError : please check database connection."+WHITE
				exit(1)

	def query(self, args):
		return self.session.query(args)

	def raw_query(self, querystr):
		return self.connection.execute(querystr)

app = Flask(__name__)
@app.teardown_appcontext
def shutdown_session(exception=None):
		self.session.remove()