import config
import lib
from flask import Flask, Request

app = Flask(__name__)
app.config.from_object(config)
app.request_class = lib.Request

import ctfengine.views

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               app.config['MAIL_FROM'],
                               app.config['ADMINS'], "ctfengine error")
    mail_handler.setFormatter(logging.Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
