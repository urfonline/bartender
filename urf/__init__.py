import requests
from datetime import datetime

from .icecast import IcecastClient

class Show:
	def __init__(self, data):
		self.id = data.get("id")
		self.name = data.get("name")

class Slot:
	def __init__(self, data):
		self.id = data.get("id")
		self.start_time = datetime.strptime(data.get("startTime"), "%H:%M:%S")
		self.end_time = datetime.strptime(data.get("endTime"), "%H:%M:%S")
		self.day = data.get("day")
		self.show = Show(data.get("show"))

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
		timestamp = date.strftime("%H:00:00")

		for slot in slate["slots"]:
			if slot["startTime"] == timestamp and slot["day"] == date.weekday():
				return Slot(slot)

		return None
