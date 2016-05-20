from flask import Flask, request, json, render_template, send_from_directory
from sys import path
path.append("..")

import settings

app = Flask(__name__,
            template_folder=settings.TEMPLATE_PATH,
            static_url_path=settings.STATIC_PATH)

@app.route('/')
def signUp():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory(settings.STATIC_PATH, path)

@app.route("/pathPlanner", methods=['POST'])
def planner():
    #TODO
    data = request.get_json()
    nb_drones = data["nb_drones"]
    starting_point = data["starting_point"]
    default_waypoints = data["default_waypoints"]
    selected_waypoints = data["selected_waypoints"]
    obstacles = data["obstacles"]
    return json.dumps({"result":2})

@app.route("/pathSender", methods=["POST"])
def pathSender():
    #TODO
    return json.dumps({"result":2})

if __name__ == "__main__":
    app.debug=True
    app.run()
