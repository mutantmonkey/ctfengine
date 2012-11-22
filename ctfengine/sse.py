import gevent
import gevent.monkey
import redis
from ctfengine import config

gevent.monkey.patch_all()
red = redis.StrictRedis()


def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe(config.REDIS_CHANNEL)
    for msg in pubsub.listen():
        if msg['type'] != 'message':
            continue
        data = msg['data'].split(': ', 1)
        yield 'event: {event}\ndata: {data}\n\n'.format(event=data[0],
                data=data[1])


def send(event, data):
    red.publish(config.REDIS_CHANNEL, event + ': ' + data)
