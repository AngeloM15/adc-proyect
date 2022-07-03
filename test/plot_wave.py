import os
import sys

HOME = os.path.expanduser('~')+"/potenciostato-project"
sys.path.append(f"{HOME}")

from libs.libdata import *

libdata = Libdata()

libdata.load_data(f"{HOME}/data/electrodo1.csv")
libdata.plot_data()

