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
First install *python3*, *pip* and *virtualenv*:

```bash
sudo apt-get install python3 python3-dev python3-pip virtualenv
```

Create a folder *opu_surveillance_system* and clone this repository inside it.

Then, initialize a virtualenv in the *opu_surveillance_system* folder
(**PATH** is the path to your *opu_surveillance_system* folder):

```bash
virtualenv --system-site-packages -p python3 PATH
source PATH/bin/activate
pip install -r PATH/monitoring/requirements.txt
```

Adapt the paths variables (in *master/script/paths.py*) to your environment.
Every time you make change in this file, you need to indicate to git to ignore it:

```bash
git update-index --assume-unchanged master/scripts/paths.py
```

Download *jQuery.3.1.1.min.js* and *Leaflet 1.0.1* on the Web.
Create a folder *lib* in *static/*. Then copy/past jQuery and Leaflet in *static/lib*.
Finally extract the Leaflet archive.

Make directories that will contain serialized files and plots (this directories
  have to be inside the *monitoring* folder):

```bash
mkdir master/scripts/webserver/data
cd master/scripts/webserver/data
mkdir plot serialization
cd plot
mkdir world paths plan
```

##Usage
Launch the server:

```bash
python3 master/scripts/webserver/webserver.py
```

Then open your browser and go to http://127.0.0.1:5000/
