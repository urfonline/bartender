from abc import ABCMeta, abstractmethod
from datetime import datetime
from flask import g
import sqlite3
import threading

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
