import flask
import json
import os

json_mimetypes = ['application/json']


class Request(flask.Request):
    # from http://flask.pocoo.org/snippets/45/
    def wants_json(self):
        mimes = json_mimetypes
        mimes.append('text/html')
        best = self.accept_mimetypes.best_match(mimes)
        return best in json_mimetypes and \
            self.accept_mimetypes[best] > \
            self.accept_mimetypes['text/html']


def load_flags(flag_path):
    flags = {}
    for flag in os.listdir(flag_path):
        data = json.load(open(os.path.join(flag_path, flag)))
        flags[data['flag']] = data
    return flags
