from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, DisconnectionError

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
			db_engine = create_engine(connect_url, pool_recycle=5)
			event.listen(db_engine, 'checkout', self.checkout_listener)

			self.db_conn = db_engine.connect()
			#sessionmaker() returns "class"
			self.session = (sessionmaker(bind=self.db_conn))()
			
		except OperationalError:
			print RED+"DBError : please check database connection."+WHITE
			exit(1)

	def checkout_listener(self, dbapi_con, con_record, con_proxy):
	    try:
	        try:
	            dbapi_con.ping(False)
	        except TypeError:
	            dbapi_con.ping()
	    except dbapi_con.OperationalError as exc:
	        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
	            raise DisconnectionError()
	        else:
	            raise