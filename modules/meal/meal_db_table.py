from sqlalchemy import Column, Integer, Boolean, String, Date, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import sql
from sqlalchemy.orm import mapper, column_property

#print sqlalchemy.version
Base = declarative_base()

class Table_Meal_log_S(Base):
	__tablename__ = "meal_coupon_inst"

	id = Column(Integer, primary_key=True, autoincrement=True)
	for_meal = Column(Integer, ForeignKey("intra_meal_table.id"))
	owned_by = Column(Integer)
	is_used = Column(Integer(1))
	is_checked_admin = Column(Integer(1))
	

class Table_Meal_log_T(Base):
	__tablename__ = "intra_meal_teacher_log"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer)
	for_meal = Column(Integer, ForeignKey("intra_meal_table.id"))
	count = Column(Integer)
	modified_at = Column(Date)

	#convert kwdictionary to object
	def __init__(self, **entries): 
		self.__dict__.update(entries)
	

class Table_Meal(Base):
	__tablename__ = "intra_meal_table"

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String)
	meal_time = Column(String(1))#,ForeignKey("meal_time.time_code"))
	meal_json = Column(String)
	quantity_json = Column(String)
	nation_json = Column(String)
	date = Column(Date)
	inst_coupon_left = Column(Integer(3))
	card_usable = Column(Integer(1))

	#convert kwdictionary to object
	def __init__(self, **entries): 
		self.__dict__.update(entries)

class Table_Blacklist(Base):
	__tablename__ = "meal_blacklist"

	#sqlalchemy ORM doesn't support table without PK
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer)
	is_banned = Column(Integer)

class Table_Mealtime(Base):
	__tablename__ = "meal_time"

	#sqlalchemy ORM doesn't support table without PK
	id = Column(Integer, primary_key=True, autoincrement=True)
	time_code = Column(String(1))
	time_name = Column(String)
	start_time = Column(Time)
	end_time = Column(Time)
	type = Column(String(1))


#Joined Table : Declarative
class Table_Meal_Student(Base):
	__table__ = sql.outerjoin(Table_Meal_log_S.__table__, Table_Blacklist.__table__,
                           Table_Meal_log_S.__table__.c.owned_by == Table_Blacklist.__table__.c.user_id)

	owned_by = column_property(Table_Meal_log_S.__table__.c.owned_by, Table_Blacklist.__table__.c.user_id)
	bl_id = Table_Blacklist.__table__.c.id
	m_id = Table_Meal_log_S.__table__.c.id


"""
class Table_User(Base):
	__tablename__ = "intra_user"

	#did NOT declare full columns of the table
	id = Column(Integer, primary_key=True)
	b_id = Column(Integer)
	user_name = Column(String(10))	
	user_type = Column(String(1))

class Table_User_S(Base):
	__tablename__ = "intra_user_student"
	
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("intra_user.id"))
	grade = Column(Integer)
	cls = Column(Integer)
	number = Column(Integer)

class Table_User_T(Base):
	__tablename__ = "intra_user_teacher"
	
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("intra_user.id"))
	department = Column(String)
	position = Column(String)
"""





