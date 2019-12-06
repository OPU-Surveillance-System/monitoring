import folium
from folium.plugins.beautify_icon import BeautifyIcon
import tempfile
import webbrowser
import os
import sys
import time
import utm
import xml.etree.ElementTree as ET

def extract_xmldata(bmark):
    tree = ET.parse('{}'.format(bmark))
    root = tree.getroot()

    coordx = []
    coordy = []
    for x in root.iter('CoordX'):
        x = int(x.text)
        coordx.append(x)
    for y in root.iter('CoordY'):
        y = int(y.text)
        coordy.append(y)
    coord = [(x,y) for x,y in zip(coordx, coordy)]

    cluster = set()
    for i in root.iter('Cluster'):
        i = int(i.text)
        cluster.add(i)

    return coord, cluster

class fmap(folium.Map):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.listtf = list()

    def show(self):
        tf = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        map_osm.save(tf)
        webbrowser.open(tf.name)
        self.listtf.append(tf)

    def __del__(self):
        list(map(lambda tf: os.remove(tf.name), self.listtf))

def make_pathline(routes, bmark, htmlname):
# if __name__ == '__main__':
    # coord, cluster = extract_xmldata('/home/scom/Documents/monitoring/master/scripts/planner/solvers/Osaba_data/Osaba_50_1_1.xml')
    coord, cluster = extract_xmldata('{}'.format(bmark))
    for i in range(len(coord)):
        coord[i] = utm.to_latlon(coord[i][0], coord[i][1], 30, 'U')
    m = folium.Map(location=coord[0], zoom_start=13)

    path_color=['crimson', 'black', 'orange', 'green', 'steelblue', 'sienna', 'gold', 'hotpink', 'indigo', 'yellowgreen']
    cluster_color=[color for color in reversed(path_color)]
    customer_size = (len(coord)-1) // (len(cluster)-1)
    icons=[]
    icons.append(BeautifyIcon(
        icon='home',
        border_color='red',
        text_color='red',
        icon_shape='marker'))
    for i in range(len(cluster)-1):
        for j in range(1, customer_size+1):
            icons.append(BeautifyIcon(
                border_color=cluster_color[i],
                text_color=cluster_color[i],
                number=i*customer_size + j,
                inner_icon_style='margin-top:0;'))
    for c, icon in zip(coord, icons):
        folium.Marker(location=c, icon=icon).add_to(m)
    # routes = [0, 50, 44, 43, 42, 41, 47, 45, 46, 49, 48, 21, 22, 23, 25, 24, 26, 29, 30, 27, 28, 0, 1, 3, 4, 6, 5, 10, 9, 7, 8, 2, 31, 32, 33, 34, 35, 38, 36, 37, 39, 40, 0, 11, 13, 15, 17, 19, 20, 18, 16, 14, 12, 0]
    path=[[]]
    path_i=0
    for i, customer in enumerate(routes):
        path[path_i].append(customer)
        if customer == 0 and i != 0 and i != len(routes)-1:
            path.append([])
            path_i+=1
            path[path_i].append(customer)
    routes_coord = [[coord[cust] for cust in path_clus] for path_clus in path]

    path_line=[]
    for color, sub_routes in zip(path_color, routes_coord):
        path_line.append(folium.PolyLine(
            sub_routes,
            weight=3,
            color=color
        ).add_to(m))
    attr = {'font-weight': 'bold', 'font-size': '16'}
    for line in path_line:
        folium.plugins.PolyLineTextPath(
            line,
            '▶      ',
            repeat=True,
            offset=6,
            attributes=attr
        ).add_to(m)
    m.save('{}'.format(htmlname))
    # m.save('./test.html')



    # map_osm = fmap(location=[43.288652158323195, -3.0112171513742956])
    # map_osm.show()
    # time.sleep(2)

if __name__ == '__main__':
    routes = [0, 26, 27, 29, 30, 28, 39, 36, 37, 38, 40, 33, 32, 31, 35, 34, 50, 49, 48, 47, 46, 0, 17, 18, 19, 20, 16, 15, 13, 11, 12, 14, 6, 8, 10, 9, 7, 23, 22, 25, 24, 21, 42, 43, 44, 41, 45, 3, 2, 4, 5, 1, 0]
    bmark = 'Osaba_data/Osaba_50_2_3.xml'
    htmlname = 'test3.html'
    make_pathline(routes, bmark, htmlname)
