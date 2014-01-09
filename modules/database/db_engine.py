from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, DisconnectionError

from flask import Flask

cIntra_user_id = "closeapi"
cIntra_user_pw = "82YwNQxLvMQeGeVx"
cIntra_uesr_db = "closeapi"

# cIntra_user_id = "root"
# cIntra_user_pw = "Qawsedrf1234"
# cIntra_uesr_db = "intra"


#from ccolor.py
RED = '\033[91m'		#red
WHITE = '\033[0m'		#ffffff

class Intra_Database:
	def __init__(self):
		try:
			connect_url = "mysql://{0}:{1}@127.0.0.1/{2}?charset=utf8".format(cIntra_user_id, cIntra_user_pw, cIntra_uesr_db)
			db_engine = create_engine(connect_url, pool_recycle=300)
#			event.listen(db_engine, 'checkout', self.checkout_listener)   
			db_engine.connect()
			
			self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db_engine))

		except OperationalError:
				print RED+"DBError : please check database connection."+WHITE
				exit(1)

app = Flask(__name__)
@app.teardown_appcontext
def shutdown_session(exception=None):
		self.session.remove()