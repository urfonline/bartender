from abc import ABCMeta, abstractmethod
from datetime import datetime
from flask import g
import sqlite3
import timeago

__all__ = ["DatabaseConnection", "SqliteDatabaseConnection", "get_connection"]

def get_connection():
	db = getattr(g, "_database", None)

	if db is None:
		db = SqliteDatabaseConnection()  # TODO: Swappable connection adapters

	return db

class DatabaseConnection(metaclass=ABCMeta):
	@abstractmethod
	def register_attendance(self, slot):
		pass

	@abstractmethod
	def get_logged_attendance(self, slot):
		pass

	@abstractmethod
	def get_show_logs(self, slot_id):
		pass

	@abstractmethod
	def get_all_show_logs(self):
		pass

	@abstractmethod
	def close(self):
		pass

class SqliteDatabaseConnection(DatabaseConnection):
	def __init__(self):
		self.conn = sqlite3.connect("shows.db")

	def register_attendance(self, slot):
		op = self.conn.cursor()
		try:
			date = datetime.utcnow()

			op.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", [date.strftime("%W"), slot.id, 1, int(date.timestamp())])
		except Exception as err:
			print(err)
			self.conn.rollback()
		else:
			self.conn.commit()

	def get_logged_attendance(self, slot):
		op = self.conn.cursor()

		try:
			date = datetime.utcnow()
			yearweek = int(date.strftime("%W"))

			op.execute("SELECT * FROM attendance WHERE slot_id=? AND week=?", [slot.id, yearweek])
			row = op.fetchone()

			if row is None:
				return None

			return RegisterRow(row)
		except Exception as err:
			print(err)
			return None
		finally:
			op.close()

	def get_show_logs(self, slot_id):
		op = self.conn.cursor()

		try:
			op.execute("SELECT * FROM attendance WHERE slot_id=?", [slot_id])
			rows = op.fetchall()

			if rows is None:
				return []

			return list(map(lambda d: RegisterRow(d), rows))
		except:
			return []
		finally:
			op.close()

	def get_all_show_logs(self):
		op = self.conn.cursor()

		try:
			op.execute("SELECT * FROM attendance")
			rows = op.fetchall()

			if rows is None:
				return []  # TODO: throw errors from this file

			return list(map(lambda d: RegisterRow(d), rows))
		except:
			return []
		finally:
			op.close()

	def get_show_data(self):
		op = self.conn.cursor()

		try:
			op.execute("SELECT slot_id, COUNT(week), logged_date FROM attendance GROUP BY slot_id")
			rows = op.fetchall()

			if rows is None:
				return {}

			slots = {}

			for d in rows:
				show = ShowData(d)
				slots[show.slot_id] = show

			return Proxy(slots)
		except:
			return {}
		finally:
			op.close()

	def close(self):
		self.conn.close()

class RegisterRow:
	def __init__(self, data):
		self.week = data[0]
		self.slot_id = data[1]
		self.attended = bool(data[2])
		self.signed_in_time = datetime.utcfromtimestamp(data[3])

	def to_dict(self):
		return {
			"week": self.week,
			"slot_id": self.slot_id,
			"attended": self.attended,
			"signed_in_time": self.signed_in_time
		}

class ShowData:
	def __init__(self, data):
		self.slot_id = data[0]
		self.num_attended = data[1]
		self.last_attended = datetime.utcfromtimestamp(data[2])
		self.last_attended_ago = timeago.format(self.last_attended, datetime.utcnow())

	def to_dict(self):
		return {
			"slot_id": self.slot_id,
			"num_attended": self.num_attended,
			"last_attended": self.last_attended.timestamp()
		}

class Proxy:
	def __init__(self, data: dict):
		self.data = data

	def __getitem__(self, key):
		return self.data.get(key, { "num_attended": 0, "last_attended": 0, "last_attended_ago": "Never" })

	__getattr__ = __getitem__