"""
Webserver for handling event from Master's GUI
"""

from flask import Flask, request, json, render_template, send_from_directory
from sys import path
path.append("..")
path.append("../planner")

import settings
import planner as ppl

app = Flask(__name__,
            template_folder=settings.TEMPLATE_PATH,
            static_url_path=settings.STATIC_PATH)

@app.route('/')
def signUp():
    """
    Generates master's page
    """

    return render_template('index.html')

@app.route('/static/<path:path>')
def send_js(path):
    """
    Links static files
    """

    return send_from_directory(settings.STATIC_PATH, path)

@app.route("/pathPlanner", methods=['POST'])
def planner():
    """
    Calls planner module with parameters coming from GUI
    """

    #TODO
    data = request.get_json()
    nb_drones = data["nb_drones"]
    starting_point = data["starting_point"]
    default_waypoints = data["default_waypoints"]
    selected_waypoints = data["selected_waypoints"]
    obstacles = data["obstacles"]
    computed_path = ppl.get_computed_path()
    return json.dumps({"computed_path":computed_path})

@app.route("/pathSender", methods=["POST"])
def pathSender():
    """
    Sends computed path to drones
    """

    #TODO
    return json.dumps({"result":2})

if __name__ == "__main__":
    app.debug=True
    app.run()
