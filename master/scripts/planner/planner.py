from flask import Flask, request, json, render_template, send_from_directory
app = Flask(__name__, template_folder="/home/scom/Documents/opu_surveillance_system/monitoring/master/",
static_url_path="/home/scom/Documents/opu_surveillance_system/monitoring/static/")

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('/home/scom/Documents/opu_surveillance_system/monitoring/static/', path)

@app.route("/pathPlanner", methods=['GET'])
def planner():
    return json.dumps({"result":2})

@app.route('/')
def signUp():
    return render_template('index.html')

if __name__ == "__main__":
    #app.debug=True
    app.run()
