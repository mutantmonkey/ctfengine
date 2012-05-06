import config
import lib
from flask import Flask, Request

app = Flask(__name__)
app.config.from_object(config)
app.request_class = lib.Request

import ctfengine.views
