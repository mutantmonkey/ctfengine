from ctfengine import models
from ctfengine import db
from ctfengine.pwn.models import Flag, Machine
import random

while True:
    print("Adding a new machine. Leave blank to quit.")
    hostname = raw_input("Hostname: ")
    if len(hostname) > 0:
        m = Machine(hostname)
        db.session.add(m)
        db.session.commit()
    else:
        break

    while True:
        print("Adding a new flag on {}. Leave blank to finish adding flags "
              "for this machine.".format(hostname))
        name = raw_input("Name: ")
        if len(name) > 0:
            flag = raw_input("Flag: ")
            points = int(raw_input("Points: "))

            f = Flag(name, flag, points)
            f.machine = m.id
            db.session.add(f)
            db.session.commit()
        else:
            print()
            break
