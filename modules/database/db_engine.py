from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

cIntra_user_id = "closeapi"
cIntra_user_pw = "82YwNQxLvMQeGeVx"
cIntra_uesr_db = "closeapi"

#from ccolor.py
RED = '\033[91m'		#red
WHITE = '\033[0m'		#ffffff

class Intra_Database:
	def __init__(self):
		try:
			self.connect_url = "mysql://{0}:{1}@127.0.0.1/{2}?charset=utf8".format(cIntra_user_id, cIntra_user_pw, cIntra_uesr_db)
			self.db_conn = create_engine(self.connect_url, pool_recycle=5).connect()
			#sessionmaker() returns "class"
			self.session = (sessionmaker(bind=self.db_conn))()
		except OperationalError:
			print RED+"DBError : please check database connection."+WHITE
			exit(1)

