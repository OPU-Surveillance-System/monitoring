# monitoring
GUI of the overall system

##Requirements
**JavaScript:**
* Leaflet 1.0.1
* jQuery 3.1.1

**Python (v3):**
* Flask 0.10.1
* tqdm 4.7.4
* utm 0.4.0
* Shapely 1.5.16
* numpy 1.8.2
* matplotlib 1.5.0
* simanneal 0.1.2

##Initial steps
Adapt the paths variables (in master/script/paths.py) to your environment.
Every time you make change in this file, you need to indicate to git to ignore it:

```bash
git update-index --assume-unchanged master/scripts/paths.py
```

Download *jQuery.3.1.1.min.js* and *Leaflet 1.0.1* on the Web.
Create a folder *lib* in *static/*. Then copy/past jQuery and Leaflet in *static/lib*.
Finally extract the Leaflet archive.   
##Usage
Launch the server:

```bash
python3 master/scripts/webserver/webserver.py
```

Then open your browser and go to http://127.0.0.1:5000/
