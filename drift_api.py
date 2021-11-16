import tornado.ioloop
import tornado.web
import drift_collector
import threading
import time
import json
from datetime import datetime

def reduce(whole, reduce_to=1000):
    """reduce number of entries in list by skipping"""
    reducer = int(len(whole)/reduce_to)
    reduced = whole[::reducer]
    return reduced


def to_ts(date_strings):
    timestamps = []
    for key in date_strings:
        timestamp = datetime.timestamp(datetime.strptime(key, "%Y-%m-%d %H:%M:%S+00:00"))
        timestamps.append(int(timestamp))
    return timestamps

def x_get(dict, key):
    drift_list = []
    for subdict in dict.values():
        try:
            drift_list.append(subdict[key])
        except Exception as e:
            print(f"Error with {subdict}, probably wrong part of the dict (go rework dict logic): {e}")
    return drift_list

class ChartHandler(tornado.web.RequestHandler):
    def get(self):
        while True:
            try:
                with open("database.json", "r+") as infile:
                    input_dict = json.loads(infile.read())
                    break
            except Exception as e:
                print(f"Error {e}, retrying file access")

        drift_list = reduce(x_get(input_dict, "drift"))
        labels = reduce(list(input_dict.keys()))

        self.render("chart.html",
                    labels=json.dumps(labels),
                    values=json.dumps(drift_list)
                    )


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(drift_collector.read_input())


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/chart", ChartHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


class ThreadedClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            drift_collector.collect()
            time.sleep(60)


if __name__ == "__main__":
    background = ThreadedClient()
    background.start()
    print("Background process started")

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
