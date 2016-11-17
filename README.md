# monitoring
GUI of the overall system

##Requirements
**JavaScript:**
* Leaflet 0.7.7
* jQuery 2.2.3

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

##Usage
Launch the server:

```bash
python3 master/scripts/webserver/webserver.py
```

Then open your browser and go to http://127.0.0.1:5000/
