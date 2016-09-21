import sqlite3

from flask import Flask
 

path = "./snowdonia.db"
conn = sqlite3.connect(path, check_same_thread=False)

app = Flask(__name__)
 
from app import views
from app.maps import make_map_traffic
from app.maps import make_map_world, make_map_berlin_bvg
