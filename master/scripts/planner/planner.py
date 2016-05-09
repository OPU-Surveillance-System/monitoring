from flask import Flask, request, json, render_template, send_from_directory
import settings

app = Flask(__name__,
            template_folder=settings.TEMPLATE_PATH,
            static_url_path=settings.STATIC_PATH)

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory(settings.STATIC_PATH, path)

@app.route("/pathPlanner", methods=['GET'])
def planner():
    return json.dumps({"result":2})

@app.route('/')
def signUp():
    return render_template('index.html')

if __name__ == "__main__":
    #app.debug=True
    app.run()
