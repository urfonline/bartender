class ReverseProxiedApp:
	def __init__(self, app, scheme):
		self.app = app
		self.scheme = scheme

	def __call__(self, environ, start_response):
		environ["wsgi.url_scheme"] = self.scheme

		return self.app(environ, start_response)
