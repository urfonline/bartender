from flask import Flask, render_template, jsonify, g, request, redirect, url_for
from urf import URFClient, IcecastClient, get_connection, BartenderJSONEncoder, Slot
from flask_dance.contrib.google import make_google_blueprint, google
from configparser import ConfigParser

config = ConfigParser()
config.read("config/config.ini")

app = Flask(__name__, template_folder="views")
blueprint = make_google_blueprint(
	client_id=config["oauth"]["client_id"],
	client_secret=config["oauth"]["client_secret"],
	scope=[
		"openid",
		"https://www.googleapis.com/auth/userinfo.email",
		"https://www.googleapis.com/auth/userinfo.profile"
	],
	redirect_to="admin"
)
app.secret_key = config["app"]["secret_key"]
app.register_blueprint(blueprint, url_prefix="/login")

urf = URFClient()
icecast = IcecastClient()

allowed_ips = ["139.184.150.23", "127.0.0.1"]

app.json_encoder = BartenderJSONEncoder

@app.route("/")
def index():
	if request.remote_addr not in allowed_ips:
		return "Not Studio PC", 404

	return render_template("show_confirm.html")

@app.route("/admin")
def admin():
	if not google.authorized:
		return redirect(url_for("google.login"))

	r = google.get("https://people.googleapis.com/v1/people/me?personFields=names")
	if not r.ok:
		print(r.text)
		return redirect(url_for("google.login"))
		
	user_data = r.json()
	db = get_connection()

	slots = urf.get_all_shows()
	attendance = db.get_show_data()

	slots.sort(key=attendance.key_for(), reverse=True)

	return render_template("admin_home.html", slots=slots, register=attendance, user=user_data["names"][0])

@app.route("/admin/actions", methods=["POST"])
def admin_force_attend():
	if not google.authorized:
		return redirect(url_for("google.login"))

	if request.form["action"] == "force_attend":
		db = get_connection()
		slot = urf.get_current_show()

		if slot is None:
			raise Exception("No slot was found?")

		if db.get_logged_attendance(slot) is None:
			db.register_attendance(slot)

			return redirect(url_for("admin"))
		else:
			raise Exception("Slot already registered!")

@app.route("/logout")
def logout():
	token = blueprint.token["access_token"]
	resp = google.post(
		"https://accounts.google.com/o/oauth2/revoke",
		params={"token": token},
		headers={"Content-Type": "application/x-www-form-urlencoded"}
	)

	print(resp.text)
	if resp.ok:
		return "Logged out.", 200
	else:
		return "There was a problem logging out :(", 500

@app.route("/api/attend", methods=["POST"])
def register():
	db = get_connection()
	slot = urf.get_current_show()
	status = icecast.fetch_status()

	if status.primary_source is None:
		return jsonify({"error": "Failed to contact streaming server."}), 500

	if slot is None:
		return jsonify({"error": "No active slot?"}), 500

	if status.primary_source.is_studio_live:
		if db.get_logged_attendance(slot) is None:
			db.register_attendance(slot)
		
		return jsonify({"show_name": slot.show.name}), 200
	else:
		return jsonify({"error": "It looks like you're not currently broadcasting. Please start broadcasting before signing in."}), 400

@app.route("/api/status")
def get_status():
	db = get_connection()
	slot = urf.get_current_show()

	if slot is None:
		return jsonify({"attended": False, "slot": None, "show": None})

	row = db.get_logged_attendance(slot)

	if row is None:
		return jsonify({"attended": False, "slot": slot, "show": slot.show}), 400
	else:
		return jsonify({"attended": row.attended, "slot": slot, "show": slot.show, "signed_in_time": row.signed_in_time})

@app.teardown_appcontext
def close_connection(exc):
	db = getattr(g, "_database", None)

	if db is not None:
		db.close()
