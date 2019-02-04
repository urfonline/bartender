from flask import Flask, render_template, jsonify, g
from urf import URFClient, IcecastClient, get_connection, BartenderJSONEncoder
import requests

app = Flask(__name__, template_folder="views")
urf = URFClient()
icecast = IcecastClient()

app.json_encoder = BartenderJSONEncoder

@app.route("/")
def index():
	pass # TODO: verify that we're being accessed from the studio PC

	return render_template("show_confirm.html")

@app.route("/api/attend", methods=["POST"])
def register():
	db = get_connection()
	slot = urf.get_current_show()
	status = icecast.fetch_status()

	if status.primary_source is None:
		return jsonify({"error": "Failed to contact streaming server."}), 500

	if status.primary_source.is_studio_live:
		db.register_attendance(slot)
		
		return jsonify({"show_name": slot.show.name}), 200
	else:
		return jsonify({"error": "It looks like you're not currently broadcasting. Please start broadcasting before signing in."}), 400

@app.route("/api/status")
def get_status():
	db = get_connection()
	slot = urf.get_current_show()
	show_id = slot.show.id

	row = db.get_logged_attendance(slot)

	if row is None:
		return jsonify({"attended": False, "show": slot.show}), 400
	else:
		return jsonify(row)

@app.teardown_appcontext
def close_connection(exc):
	db = getattr(g, "_database", None)

	if db is not None:
		db.close()
