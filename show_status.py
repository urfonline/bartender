from flask import Flask, render_template, jsonify
from urf import URFClient, IcecastClient
import requests

app = Flask(__name__, template_folder="views")
urf = URFClient()
icecast = IcecastClient()

@app.route("/")
def index():
	pass # TODO: verify that we're being accessed from the studio PC

	return render_template("show_confirm.html")

@app.route("/api/attend", methods=["POST"])
def register():
	slot = urf.get_current_show()
	status = icecast.fetch_status()

	if status.primary_source is None:
		return jsonify({"error": "Failed to contact streaming server."}), 500

	if status.primary_source.is_studio_live:
		# TODO: Log this in database!!
		
		return jsonify({"show_name": slot.show.name}), 200
	else:
		return jsonify({"error": "It looks like you're not currently broadcasting. Please start broadcasting before signing in."}), 400

@app.route("/api/status")
def get_status():
	slot = urf.get_current_show()
	show_id = slot.show.id

	# TODO: Check database for this slot
	pass
