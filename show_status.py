from flask import Flask, render_template, jsonify
from urf import URFClient
import requests

app = Flask(__name__, template_folder="views")
urf = URFClient()

@app.route("/")
def index():
	pass # TODO: verify that we're being accessed from the studio PC

	return render_template("show_confirm.html")

@app.route("/api/attend", methods=["POST"])
def register():
	show = urf.get_current_show()
	
	return jsonify({"show_name": show["name"]}), 200
