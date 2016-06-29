"""
Webserver for handling event from Master's GUI
"""

from flask import Flask, request, json, render_template, send_from_directory
from sys import path
import pickle
path.append("..")
path.append("../planner")

import settings
import planner as ppl
import map_converter as m

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

@app.route("/mapConverter", methods=['POST'])
def converter():
    """
    Call converter to represent map as a grid
    """

    #TODO
    data = request.get_json()
    limits = data["limits"]
    starting_point = data["starting_point"]
    obstacles = data["obstacles"]
    default_targets = data["default_waypoints"]
    mapper = m.Mapper(limits, starting_point, obstacles, default_targets)
    mapper.plot_world()
    #response = ppl.convert_map()
    response = 0

    return json.dumps({"response":response})

@app.route("/pathPlanner", methods=['POST'])
def planner():
    """
    Calls planner module with parameters coming from GUI
    """

    #TODO
    data = request.get_json()
    nb_drones = data["nb_drones"]
    default_waypoints = data["default_waypoints"]
    selected_waypoints = data["selected_waypoints"]
    try:
        f = open("data/mapper.pickle", "rb")
        mapper = pickle.load(f)
        f.close()
        computed_path = ppl.get_computed_path()
    except IOError:
        response = "World not virtualized yet. Please click on 'compute grid'."

    return json.dumps({"computed_path":computed_path, "response":response})

@app.route("/pathSender", methods=["POST"])
def path_sender():
    """
    Sends computed path to drones
    """

    #TODO

    return json.dumps({"result":2})

if __name__ == "__main__":
    app.debug=True
    app.run()
