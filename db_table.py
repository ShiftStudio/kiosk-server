from sqlalchemy import Column, Integer, Boolean, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

#print sqlalchemy.version
Base = declarative_base()

class Table_Meal_log(Base):
	__tablename__ = "intra_meal_log"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey("intra_user.id"))
	food_id = Column(Integer, ForeignKey("intra_meal_table.id"))
	count = Column(Integer)
	is_allowed = Column(Boolean)
	
	# def __init__(self, uid, fid, count, is_allowed):
	# 	self.user_id = uid
	# 	self.food_id = fid
	# 	self.count = count
	# 	self.is_allowed = is_allowed

	#same as csharp's toString or objC's description
	def __repr__(self):
		return "<Meal_log(id, food_id, count, allowed) : (%s, %s, %s, %s)>" % (
			self.id, self.food_id, self.count, self.is_allowed)

class Table_Meal(Base):
	__tablename__ = "intra_meal_table"

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String)
	meal_time = Column(String(2))
	meal_json = Column(String)
	quantity_json = Column(String)
	nation_json = Column(String)
	date = Column(Date)

	#convert kwdictionary to object
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)


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
	cls = Column('class', Integer)
	number = Column(Integer)

class Table_User_T(Base):
	__tablename__ = "intra_user_teacher"
	
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("intra_user.id"))
	department = Column(String)
	position = Column(String)


