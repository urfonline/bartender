import requests

class SourceStats:
	def __init__(self, data):
		self.listeners = data.get("listeners")
		self.title = data.get("title")
		self.url = data.get("listenurl")

		self.is_studio_live = (self.title == "URFOnline.com - Live from the studio")

class StatsResponse:
	def __init__(self, data):
		self.server_start = data.get("server_start")
		self.sources = list(map(lambda d: SourceStats(d), data.get("source")))

		try:
			self.primary_source = self.sources[1]
		except IndexError:
			self.primary_source = None

class IcecastClient:
	remote_url = "http://uk2.internet-radio.com:30764/status-json.xsl"
	
	def __init__(self):
		pass

	def fetch_status(self):
		r = requests.get(self.remote_url)

		return StatsResponse(r.json()["icestats"])
