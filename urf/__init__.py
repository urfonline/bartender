import requests
from datetime import datetime, timedelta, time

from .icecast import IcecastClient
from .database import *
from .serialization import BartenderJSONEncoder

class Show:
	def __init__(self, data):
		self.id = data.get("id")
		self.name = data.get("name")

	def to_dict(self):
		return dict(id=self.id, name=self.name)

class Slot:
	def __init__(self, data):
		self.id = data.get("id")
		self.start_time = datetime.strptime(data.get("startTime"), "%H:%M:%S").time()
		self.end_time = datetime.strptime(data.get("endTime"), "%H:%M:%S").time()
		self.day = data.get("day")
		self.show = Show(data.get("show"))

	def to_dict(self):
		return dict(id=self.id,
					start_time=self.start_time.isoformat(),
					end_time=self.end_time.isoformat(),
					day=self.day)

class URFClient:
	def __init__(self):
		pass

	def make_graphql_request(self, query):
		r = requests.post("https://api.urfonline.com/graphql", json={
			"query": query
		})

		return r.json()

	def get_current_slate(self):
		return self.make_graphql_request("""
		query ScheduleQuery {
		  currentSlate {
		    slots {
		      id, startTime, endTime, day
		      show {
		        id, name, slug
		      }
		    }
		  }
		}
		""")["data"]["currentSlate"]

	def get_current_show(self):
		slate = self.get_current_slate()
		date = datetime.utcnow()
		ts = date.time()

		for slot in slate["slots"]:
			s = Slot(slot)

			if s.start_time <= ts and s.end_time > ts and slot["day"] == date.weekday():
				return s

		return None
